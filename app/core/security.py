"""Security utilities: rate limiting, CORS, input sanitization."""
import re
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri="memory://",
)


def setup_security(app: Flask) -> None:
    """Configure CORS and rate limiting."""
    CORS(app, origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ])
    limiter.init_app(app)


def sanitize_input(text: str) -> str:
    """Strip HTML tags and limit length for search queries."""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", text)
    # Remove special characters except spaces, hyphens, apostrophes
    clean = re.sub(r"[^\w\s\-']", "", clean)
    # Limit length
    return clean[:200].strip()
