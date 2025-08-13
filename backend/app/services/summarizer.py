import os
import re
from pathlib import Path
from typing import List
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


class Summarizer:
    def __init__(self) -> None:
        # Model can be switched via env (e.g., allenai/led-large-16384, facebook/bart-large-cnn)
        # Updated to use more modern and efficient models
        project_root = Path(__file__).resolve().parents[3]
        default_cache = project_root / "models" / "transformers"
        cache_dir = os.getenv("TRANSFORMERS_CACHE", str(default_cache))

        # Set environment variables to ensure models are loaded from local cache
        os.environ["TRANSFORMERS_CACHE"] = str(default_cache)
        os.environ["HF_HOME"] = str(project_root / "models" / "huggingface")

        # Use more modern model by default - facebook/bart-large-cnn is more reliable
        model_id = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id, cache_dir=cache_dir)
        device = 0 if torch.cuda.is_available() else -1
        self.summarizer = pipeline("summarization", model=model, tokenizer=self.tokenizer, device=device)
        self._is_led = "led" in model_id.lower()

        # Tunables - optimized for better performance
        default_max = 4096 if self._is_led else 1024
        self.max_input_tokens = int(os.getenv("SUMMARIZER_MAX_INPUT_TOKENS", str(min(getattr(self.tokenizer, 'model_max_length', default_max) or default_max, default_max))))
        self.token_overlap = int(os.getenv("SUMMARIZER_TOKEN_OVERLAP", "128"))
        self.map_tokens = int(os.getenv("SUMMARIZER_MAP_TOKENS", "160"))
        self.reduce_tokens = int(os.getenv("SUMMARIZER_REDUCE_TOKENS", "220"))

    def _split_text(self, text: str) -> List[str]:
        # Token-based overlapping chunks for accurate model limits
        if not text:
            return [""]
        enc = self.tokenizer(text, return_tensors=None, add_special_tokens=False)
        ids = enc.get("input_ids", [])
        if not ids:
            return [text]
        max_len = self.max_input_tokens
        overlap = self.token_overlap
        chunks_ids: List[List[int]] = []
        i = 0
        n = len(ids)
        while i < n:
            end = min(i + max_len, n)
            chunk = ids[i:end]
            chunks_ids.append(chunk)
            if end == n:
                break
            i = max(0, end - overlap)
        # Decode
        return [self.tokenizer.decode(c, skip_special_tokens=True) for c in chunks_ids]

    def _sanitize(self, text: str) -> str:
        # Remove URLs and phone-like patterns to avoid noisy outputs
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"\b\+?\d[\d\-\s()x]{6,}\b", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def summarize(self, text: str, max_words: int = 250) -> str:
        """Summarize text with enhanced error handling"""
        try:
            # Clean and prepare text
            text = self._sanitize(text)
            if not text.strip():
                return "No content to summarize."
            
            # Validate max_words parameter
            if not isinstance(max_words, int) or max_words <= 0:
                max_words = 250
            
            # For shorter texts, use direct summarization
            if len(text.split()) < 500:
                return self._sanitize(self._generate_summary(text, max_words))
            
            # Map-Reduce summarization over overlapping chunks
            chunks = self._split_text(text)
            
            if len(chunks) == 1:
                return self._sanitize(self._generate_summary(text, max_words))

            section_summaries: list[str] = []
            for ch in chunks:
                if len(ch.strip()) < 50:  # Skip very short chunks
                    continue
                try:
                    summary = self._generate_summary(ch, min(self.map_tokens, 150))
                    if summary and len(summary.strip()) > 20:  # Only keep meaningful summaries
                        section_summaries.append(self._sanitize(summary))
                except Exception as chunk_error:
                    print(f"Error processing chunk: {chunk_error}")
                    continue

            if not section_summaries:
                return self._sanitize(self._generate_summary(text, max_words))

            # If we have multiple summaries, combine them
            if len(section_summaries) > 1:
                combined_text = " ".join(section_summaries)
                return self._sanitize(self._generate_summary(combined_text, max_words))
            
            return self._sanitize(section_summaries[0])
            
        except Exception as e:
            print(f"Error in summarizer: {str(e)}")
            return "I apologize, but I encountered an error while summarizing the text. Please try again or contact support if the issue persists."

    def _generate_summary(self, text: str, max_new_tokens: int) -> str:
        """Generate summary with enhanced error handling"""
        try:
            # Validate input parameters
            if not text or not isinstance(text, str):
                return "Invalid text input."
            
            if not isinstance(max_new_tokens, int) or max_new_tokens <= 0:
                max_new_tokens = 150
            
            # Custom path for LED to ensure global attention is set
            if self._is_led:
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_input_tokens,
                )
                input_ids = inputs["input_ids"]
                attention_mask = inputs.get("attention_mask")
                # Global attention mask: first token attends globally
                global_attention_mask = torch.zeros_like(input_ids)
                global_attention_mask[:, 0] = 1

                model = self.summarizer.model
                device = self.summarizer.device if hasattr(self.summarizer, "device") else -1
                if device != -1:
                    input_ids = input_ids.to(device)
                    if attention_mask is not None:
                        attention_mask = attention_mask.to(device)
                    global_attention_mask = global_attention_mask.to(device)

                summary_ids = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    global_attention_mask=global_attention_mask,
                    num_beams=4,
                    max_new_tokens=max_new_tokens,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                    length_penalty=2.0,
                    temperature=0.7,
                    do_sample=False,
                )
                return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            # Fallback to pipeline for non-LED models
            out = self.summarizer(
                text,
                max_new_tokens=max_new_tokens,
                num_beams=4,
                do_sample=False,
                truncation=True,
                early_stopping=True,
                length_penalty=2.0,
                no_repeat_ngram_size=3,
            )
            return out[0]["summary_text"]
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Error generating summary. Please try again."


