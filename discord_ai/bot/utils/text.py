def chunk(text: str, limit: int = 1900) -> list[str]:
    return [text[i : i + limit] for i in range(0, len(text), limit)] or [""]
