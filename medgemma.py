"""Utilities for interacting with the google/medgemma-4b-it model via Hugging Face."""

from __future__ import annotations

import functools
from typing import Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "google/medgemma-4b-it"


def _load_model() -> Tuple[AutoTokenizer, AutoModelForCausalLM]:
    """Load the tokenizer and model for Med-Gemma 4B instruction tuned.

    The model is loaded on the available device (GPU if available, otherwise CPU)
    using bfloat16 precision to reduce memory usage.
    """

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # ``device_map="auto"`` will put the model on GPU if one is available.
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return tokenizer, model


# Cache the model after the first load so that multiple calls do not reload it
# repeatedly.
@functools.lru_cache(maxsize=1)
def load_model() -> Tuple[AutoTokenizer, AutoModelForCausalLM]:
    return _load_model()


def generate_response(prompt: str, *, max_new_tokens: int = 50) -> str:
    """Generate a response for the given ``prompt`` using the Med-Gemma model.

    Parameters
    ----------
    prompt:
        The input text to condition the model on.
    max_new_tokens:
        The maximum number of tokens to generate. Defaults to 50.

    Returns
    -------
    str
        The decoded text output from the model with special tokens removed.
    """

    tokenizer, model = load_model()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":
    # Example usage when running as a script
    print(generate_response("Describe the role of MRI in brain imaging."))
