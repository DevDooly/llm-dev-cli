import re

class PiiMasker:
    PATTERNS = {
        "RRN": (re.compile(r"\b\d{6}-[1-4]\d{6}\b"), "[REDACTED_RRN]"),
        "PHONE": (re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b"), "[REDACTED_PHONE]"),
        "EMAIL": (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
        "CARD": (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[REDACTED_CARD]")
    }

    @classmethod
    def mask(cls, text: str) -> str:
        if not text:
            return ""
        masked = text
        for _, (pattern, replacement) in cls.PATTERNS.items():
            masked = pattern.sub(replacement, masked)
        return masked
