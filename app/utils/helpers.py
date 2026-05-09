"""Utility helpers."""


def format_runtime(minutes: int) -> str:
    """Convert minutes to 'Xh Ym' format."""
    if not minutes:
        return "N/A"
    h, m = divmod(minutes, 60)
    return f"{h}h {m}m" if h else f"{m}m"
