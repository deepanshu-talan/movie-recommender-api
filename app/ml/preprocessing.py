"""Text preprocessing for ML pipeline."""
import re


def clean_text(text: str) -> str:
    """Clean and normalize text for TF-IDF vectorization."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_tags(movie: dict) -> str:
    """Build combined text feature from movie metadata.

    Combines genres, keywords, and overview into a single string
    for TF-IDF vectorization.
    """
    parts = []

    # Genres
    genres = movie.get("genres", [])
    if genres:
        if isinstance(genres[0], dict):
            genre_text = " ".join(g["name"] for g in genres)
        else:
            genre_text = " ".join(str(g) for g in genres)
        parts.append(genre_text)

    # Keywords (boost by repeating)
    keywords = movie.get("keywords", [])
    if keywords:
        keyword_text = " ".join(keywords)
        parts.append(keyword_text)
        parts.append(keyword_text)  # Double-weight keywords

    # Overview
    overview = movie.get("overview", "")
    if overview:
        parts.append(overview)

    return clean_text(" ".join(parts))
