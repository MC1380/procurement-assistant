def normalize_evidence_text(text: str) -> str:
    """Normalize evidence text for deterministic matching."""
    normalized = text.lower()
    normalized = " ".join(normalized.split())

    normalized = normalized.replace("|", ":")
    normalized = normalized.replace(" :", ":")

    return normalized