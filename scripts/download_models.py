"""Pre-download all models to a local ./models directory and set env variables.
Run:
  python scripts/download_models.py
Then start the backend so it uses the local cache.
"""
import os
from pathlib import Path

from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer


MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def set_local_cache_env() -> None:
    os.environ["HF_HOME"] = str(MODELS_DIR / "huggingface")
    os.environ["TRANSFORMERS_CACHE"] = str(MODELS_DIR / "transformers")
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODELS_DIR / "sentence-transformers")


def download_transformers_model(model_id: str) -> None:
    print(f"Downloading HF model: {model_id}")
    # Ensure tokenizer and model weights are cached
    AutoTokenizer.from_pretrained(model_id, cache_dir=str(MODELS_DIR / "transformers"))
    AutoModelForSeq2SeqLM.from_pretrained(model_id, cache_dir=str(MODELS_DIR / "transformers"))


def download_sentence_transformer(model_id: str) -> None:
    print(f"Downloading SentenceTransformer: {model_id}")
    SentenceTransformer(model_id, cache_folder=str(MODELS_DIR / "sentence-transformers"))


def main() -> None:
    set_local_cache_env()
    # Summarization models
    download_transformers_model("t5-small")
    download_transformers_model("allenai/led-large-16384")
    download_transformers_model("facebook/bart-large-cnn")
    # Semantic search model
    download_sentence_transformer("all-MiniLM-L6-v2")
    print("All models downloaded to:", MODELS_DIR)
    print("Set these env vars before running the backend for persistent local cache:")
    print("  setx HF_HOME \"" + str(MODELS_DIR / "huggingface") + "\"")
    print("  setx TRANSFORMERS_CACHE \"" + str(MODELS_DIR / "transformers") + "\"")
    print("  setx SENTENCE_TRANSFORMERS_HOME \"" + str(MODELS_DIR / "sentence-transformers") + "\"")


if __name__ == "__main__":
    main()


