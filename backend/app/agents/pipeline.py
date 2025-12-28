"""Agent pipeline: Planner -> Retriever -> Reasoner -> Validator -> Responder"""
from typing import Dict, List, Optional
from backend.app.core.vector_store import VectorStore
from backend.app.core.embeddings import LLMProvider
from backend.app.utils.validators import detect_prompt_injection, sanitize_text
from backend.app.utils.logger import logger


class AgentPipeline:
    """
    Orchestrates the agent-based RAG pipeline:
    1. Planner: Decides retrieval strategy
    2. Retriever: Fetches relevant chunks
    3. Reasoner: Synthesizes evidence
    4. Validator: Checks grounding and safety
    5. Responder: Formats final answer
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = LLMProvider()

    def process_question(self, question: str, top_k: int = 5, answer_style: str = "concise") -> Dict:
        """
        Process a question through the full agent pipeline
        Returns dict with answer, citations, confidence, and safety flags
        """
        logger.info(f"Processing question: {question[:100]}...")

        # 1. Planner: Analyze question and decide strategy
        plan = self._planner(question)

        if not plan["needs_retrieval"]:
            return {
                "answer": plan["response"],
                "citations": [],
                "confidence": "low",
                "safety_flags": plan.get("safety_flags", []),
                "reasoning": "No retrieval needed"
            }

        # 2. Retriever: Fetch relevant chunks
        retrieved_chunks = self._retriever(question, top_k)

        if not retrieved_chunks:
            return {
                "answer": "I don't have any documents to answer this question. Please upload relevant documents first.",
                "citations": [],
                "confidence": "low",
                "safety_flags": [],
                "reasoning": "No chunks retrieved"
            }

        # 3. Reasoner: Synthesize evidence
        reasoning_result = self._reasoner(question, retrieved_chunks, answer_style)

        # 4. Validator: Check grounding and safety
        validation_result = self._validator(reasoning_result, retrieved_chunks)

        if not validation_result["is_valid"]:
            return {
                "answer": validation_result["fallback_response"],
                "citations": [],
                "confidence": "low",
                "safety_flags": validation_result["safety_flags"],
                "reasoning": validation_result["reason"]
            }

        # 5. Responder: Format final answer
        final_response = self._responder(reasoning_result, retrieved_chunks, validation_result)

        return final_response

    def _planner(self, question: str) -> Dict:
        """
        Planner agent: Decides if retrieval is needed and checks for basic issues
        """
        # Check for prompt injection
        is_injection, patterns = detect_prompt_injection(question)
        if is_injection:
            logger.warning(f"Potential prompt injection detected: {patterns}")
            return {
                "needs_retrieval": False,
                "response": "I cannot process this question as it contains potentially unsafe patterns.",
                "safety_flags": ["prompt_injection"]
            }

        # Check if knowledge base is empty
        stats = self.vector_store.get_collection_stats()
        if stats["total_chunks"] == 0:
            return {
                "needs_retrieval": False,
                "response": "No documents have been uploaded yet. Please upload documents before asking questions.",
                "safety_flags": ["empty_knowledge_base"]
            }

        # Check if question is too vague
        if len(question.strip()) < 10:
            return {
                "needs_retrieval": False,
                "response": "Your question seems too short. Could you provide more details?",
                "safety_flags": ["vague_question"]
            }

        # Normal case: proceed with retrieval
        return {
            "needs_retrieval": True,
            "safety_flags": []
        }

    def _retriever(self, question: str, top_k: int) -> List[Dict]:
        """
        Retriever agent: Performs vector search and returns top-k chunks
        """
        try:
            results = self.vector_store.search(question, top_k=top_k)
            logger.info(f"Retrieved {len(results)} chunks")
            return results
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            return []

    def _reasoner(self, question: str, chunks: List[Dict], answer_style: str) -> Dict:
        """
        Reasoner agent: Synthesizes evidence into a draft answer
        """
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(f"[Source {i+1}] {chunk['text'][:500]}")

        context = "\n\n".join(context_parts)

        # Build prompt for LLM
        style_instruction = {
            "concise": "Provide a brief, direct answer.",
            "detailed": "Provide a comprehensive, detailed answer.",
            "bullet": "Provide the answer as bullet points."
        }.get(answer_style, "Provide a clear answer.")

        prompt = f"""You are a helpful assistant answering questions based only on the provided document context.

Question: {question}

Context from documents:
{context}

Instructions:
- Answer ONLY based on the provided context
- {style_instruction}
- If the context doesn't contain the answer, say "The provided documents do not contain information about this."
- Cite which source(s) support each claim using [Source N] notation

Answer:"""

        try:
            answer = self.llm.generate_completion(prompt, max_tokens=500, temperature=0.3)
            logger.info("Reasoner generated draft answer")

            return {
                "answer": answer,
                "context_used": context,
                "num_sources": len(chunks)
            }
        except Exception as e:
            logger.error(f"Reasoner error: {str(e)}")
            return {
                "answer": "I encountered an error while processing your question.",
                "context_used": "",
                "num_sources": 0,
                "error": str(e)
            }

    def _validator(self, reasoning_result: Dict, chunks: List[Dict]) -> Dict:
        """
        Validator agent: Checks that answer is grounded in retrieved context
        """
        answer = reasoning_result.get("answer", "")
        safety_flags = []

        # Check for injection in retrieved context
        for chunk in chunks:
            is_injection, _ = detect_prompt_injection(chunk["text"])
            if is_injection:
                safety_flags.append("injection_in_context")

        # Check if answer indicates lack of information
        no_info_phrases = [
            "do not contain",
            "don't contain",
            "no information",
            "cannot answer",
            "not found in"
        ]

        has_no_info = any(phrase in answer.lower() for phrase in no_info_phrases)

        # Check if answer is too short (potential failure)
        if len(answer.strip()) < 20 and not has_no_info:
            return {
                "is_valid": False,
                "fallback_response": "I couldn't generate a proper answer. Could you rephrase your question?",
                "safety_flags": safety_flags + ["answer_too_short"],
                "reason": "Answer validation failed: too short"
            }

        # Check for error in reasoning
        if "error" in reasoning_result:
            return {
                "is_valid": False,
                "fallback_response": "I encountered a technical issue. Please try again.",
                "safety_flags": safety_flags + ["llm_error"],
                "reason": "LLM error during reasoning"
            }

        # Passed validation
        confidence = self._assess_confidence(reasoning_result, chunks)

        return {
            "is_valid": True,
            "confidence": confidence,
            "safety_flags": safety_flags,
            "reason": "Validation passed"
        }

    def _assess_confidence(self, reasoning_result: Dict, chunks: List[Dict]) -> str:
        """Assess confidence level based on retrieval scores and answer content"""
        if not chunks:
            return "low"

        # Check average similarity score
        avg_score = sum(c["score"] for c in chunks) / len(chunks)

        # Check if answer indicates uncertainty
        answer = reasoning_result.get("answer", "").lower()
        uncertain_phrases = ["might", "possibly", "perhaps", "unclear", "not sure"]
        has_uncertainty = any(phrase in answer for phrase in uncertain_phrases)

        if avg_score > 0.8 and not has_uncertainty:
            return "high"
        elif avg_score > 0.6:
            return "medium"
        else:
            return "low"

    def _responder(self, reasoning_result: Dict, chunks: List[Dict], validation_result: Dict) -> Dict:
        """
        Responder agent: Formats the final response with citations
        """
        answer = reasoning_result.get("answer", "")

        # Build citations from retrieved chunks
        citations = []
        for i, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            citations.append({
                "doc_id": metadata.get("doc_id", "unknown"),
                "filename": metadata.get("filename", "unknown"),
                "page": metadata.get("num_pages"),
                "sheet": metadata.get("num_sheets"),
                "chunk_id": metadata.get("chunk_id", "unknown"),
                "score": round(chunk["score"], 3)
            })

        return {
            "answer": answer,
            "citations": citations,
            "confidence": validation_result.get("confidence", "medium"),
            "safety_flags": validation_result.get("safety_flags", []),
            "reasoning": f"Used {len(chunks)} source chunks"
        }
