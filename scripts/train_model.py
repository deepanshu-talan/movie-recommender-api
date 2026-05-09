"""Train the TF-IDF model and build the cosine similarity matrix.

Usage:
    python scripts/train_model.py --input data/tmdb_dataset/movies.json

Reads the movie dataset, builds TF-IDF vectors, computes cosine
similarity, and saves all artifacts to data/artifacts/.
"""
import os
import sys
import json
import argparse
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.preprocessing import build_tags
from app.ml.vectorizer import create_vectorizer
from app.core.logging_config import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger("train_model")

ARTIFACTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "artifacts"
)


def train(input_path: str) -> None:
    """Train TF-IDF model and save artifacts."""
    # Load dataset
    logger.info("loading_dataset", path=input_path)
    with open(input_path, "r", encoding="utf-8") as f:
        movies = json.load(f)
    logger.info("dataset_loaded", count=len(movies))
    if not movies:
        print(f"Dataset is empty: {input_path}")
        print("Run `python scripts/fetch_tmdb_data.py --count 100` after setting TMDB_API_KEY or TMDB_ACCESS_TOKEN.")
        sys.exit(1)

    # Build tags for each movie
    logger.info("building_features")
    tags = [build_tags(m) for m in movies]

    # Filter out movies with empty tags
    valid = [(m, t) for m, t in zip(movies, tags) if t.strip()]
    movies = [m for m, _ in valid]
    tags = [t for _, t in valid]
    logger.info("valid_movies", count=len(movies))
    if not tags:
        print("No trainable movie text was found in the dataset.")
        print("Fetch data with overviews, genres, or keywords before training.")
        sys.exit(1)

    # Create and fit TF-IDF vectorizer
    logger.info("fitting_tfidf")
    vectorizer = create_vectorizer(max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(tags)
    logger.info("tfidf_complete", shape=str(tfidf_matrix.shape))

    # Compute cosine similarity
    logger.info("computing_similarity")
    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    logger.info("similarity_complete", shape=str(sim_matrix.shape))

    # Save artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    joblib.dump(vectorizer, os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib"))
    joblib.dump(tfidf_matrix, os.path.join(ARTIFACTS_DIR, "tfidf_matrix.joblib"))
    joblib.dump(sim_matrix, os.path.join(ARTIFACTS_DIR, "cosine_sim_matrix.joblib"))

    # Save movie index (metadata only, no large fields)
    movie_index = []
    for m in movies:
        movie_index.append({
            "id": m.get("id"),
            "title": m.get("title", ""),
            "overview": m.get("overview", "")[:200],
            "year": m.get("year", ""),
            "genres": m.get("genres", []),
            "vote_average": m.get("vote_average", 0),
            "vote_count": m.get("vote_count", 0),
            "popularity": m.get("popularity", 0),
            "poster_path": m.get("poster_path"),
            "backdrop_path": m.get("backdrop_path"),
            "original_language": m.get("original_language", ""),
        })

    with open(os.path.join(ARTIFACTS_DIR, "movie_index.json"), "w", encoding="utf-8") as f:
        json.dump(movie_index, f, indent=2, ensure_ascii=False)

    logger.info("artifacts_saved", directory=ARTIFACTS_DIR)
    print("\nTraining complete!")
    print(f"   Movies: {len(movies)}")
    print(f"   TF-IDF matrix: {tfidf_matrix.shape}")
    print(f"   Similarity matrix: {sim_matrix.shape}")
    print(f"   Artifacts saved to: {ARTIFACTS_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Train recommendation model")
    parser.add_argument("--input", type=str, default="data/tmdb_dataset/movies.json", help="Input dataset path")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Dataset not found: {args.input}")
        print("   Run `python scripts/fetch_tmdb_data.py` first.")
        sys.exit(1)

    train(args.input)


if __name__ == "__main__":
    main()
