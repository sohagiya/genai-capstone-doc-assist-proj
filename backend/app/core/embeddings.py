"""Embeddings generation using OpenAI or Gemini"""
from typing import List
import openai
import google.generativeai as genai
from backend.app.config import settings
from backend.app.utils.logger import logger


class EmbeddingsProvider:
    """Generate embeddings using configured LLM provider"""

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.model = settings.embeddings_model

        if self.provider == "openai":
            openai.api_key = settings.llm_api_key
        elif self.provider == "gemini":
            genai.configure(api_key=settings.llm_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        logger.info(f"Initialized embeddings provider: {self.provider}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []

        try:
            if self.provider == "openai":
                return self._generate_openai_embeddings(texts)
            elif self.provider == "gemini":
                return self._generate_gemini_embeddings(texts)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        client = openai.OpenAI(api_key=settings.llm_api_key)

        response = client.embeddings.create(
            model=self.model,
            input=texts
        )

        embeddings = [item.embedding for item in response.data]
        logger.info(f"Generated {len(embeddings)} OpenAI embeddings")
        return embeddings

    def _generate_gemini_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Gemini API"""
        embeddings = []

        for text in texts:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])

        logger.info(f"Generated {len(embeddings)} Gemini embeddings")
        return embeddings


class LLMProvider:
    """Generate text completions using configured LLM provider"""

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.model = settings.llm_model

        if self.provider == "openai":
            openai.api_key = settings.llm_api_key
        elif self.provider == "gemini":
            genai.configure(api_key=settings.llm_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

        logger.info(f"Initialized LLM provider: {self.provider}")

    def generate_completion(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text completion"""
        try:
            if self.provider == "openai":
                return self._generate_openai_completion(prompt, max_tokens, temperature)
            elif self.provider == "gemini":
                return self._generate_gemini_completion(prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    def _generate_openai_completion(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate completion using OpenAI API"""
        client = openai.OpenAI(api_key=settings.llm_api_key)

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    def _generate_gemini_completion(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate completion using Gemini API"""
        model = genai.GenerativeModel(self.model)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )

        return response.text
