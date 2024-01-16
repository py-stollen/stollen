def camel_to_snake(string: str) -> str:
    parts: list[str] = [f"{c.lower()}_" if c.isupper() else c for c in string]
    return "".join(parts).rstrip("_")
