"""TF-IDF vectorization wrapper."""
from sklearn.feature_extraction.text import TfidfVectorizer


def create_vectorizer(max_features: int = 5000, stop_words: str = "english") -> TfidfVectorizer:
    """Create a configured TF-IDF vectorizer.

    Why TF-IDF:
    - Fast to fit and transform (< 1s for 5000 movies)
    - Interpretable weights
    - No GPU required
    - Small memory footprint (~15MB for 5K movies)
    - Handles variable-length text well
    """
    return TfidfVectorizer(
        max_features=max_features,
        stop_words=stop_words,
        ngram_range=(1, 2),  # Unigrams + bigrams for phrase capture
        min_df=2,            # Ignore extremely rare terms
        max_df=0.95,         # Ignore terms in >95% of docs
        sublinear_tf=True,   # Apply log normalization to term frequencies
    )
