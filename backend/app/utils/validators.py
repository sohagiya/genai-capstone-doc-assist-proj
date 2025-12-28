"""Input validation and security checks"""
import re
from typing import List, Tuple


# Common prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|prior)\s+instructions",
    r"disregard\s+(previous|above|prior)",
    r"forget\s+(previous|above|all)",
    r"new\s+instructions?:",
    r"system\s*:",
    r"<\s*script",
    r"javascript:",
    r"data:text/html",
]


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file has an allowed extension"""
    if not filename or "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def validate_file_size(file_size: int, max_bytes: int) -> bool:
    """Check if file size is within limit"""
    return 0 < file_size <= max_bytes


def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    """
    Detect potential prompt injection attempts in text
    Returns (is_injection, detected_patterns)
    """
    detected = []
    text_lower = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            detected.append(pattern)

    return len(detected) > 0, detected


def sanitize_text(text: str) -> str:
    """
    Basic sanitization of text to remove potentially harmful content
    Strips HTML-like tags and normalizes whitespace
    """
    # Remove HTML-like tags
    text = re.sub(r"<[^>]+>", "", text)

    # Normalize whitespace
    text = " ".join(text.split())

    return text.strip()


def validate_question(question: str, max_length: int = 1000) -> Tuple[bool, str]:
    """
    Validate a user question
    Returns (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "Question cannot be empty"

    if len(question) > max_length:
        return False, f"Question exceeds maximum length of {max_length} characters"

    # Check for injection patterns
    is_injection, patterns = detect_prompt_injection(question)
    if is_injection:
        return False, "Question contains potentially unsafe patterns"

    return True, ""
