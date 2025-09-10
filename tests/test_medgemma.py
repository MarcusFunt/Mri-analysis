import torch
from unittest import mock

import medgemma


def test_load_model_is_cached():
    fake = (object(), object())
    medgemma.load_model.cache_clear()
    with mock.patch("medgemma._load_model", return_value=fake) as mocked:
        a = medgemma.load_model()
        b = medgemma.load_model()
        assert a is b is fake
        assert mocked.call_count == 1


class DummyBatch(dict):
    def to(self, device):
        self["device"] = device
        return self


def test_generate_response_uses_model(monkeypatch):
    prompt = "hello"

    class DummyTokenizer:
        def __call__(self, text, return_tensors):
            assert text == prompt
            assert return_tensors == "pt"
            return DummyBatch({"input_ids": torch.tensor([[1]])})

        def decode(self, ids, skip_special_tokens):
            assert skip_special_tokens
            return "decoded"

    class DummyModel:
        device = torch.device("cpu")

        def generate(self, **kwargs):
            assert kwargs["max_new_tokens"] == 5
            assert "input_ids" in kwargs
            return torch.tensor([[0, 1]])

    monkeypatch.setattr(medgemma, "load_model", lambda: (DummyTokenizer(), DummyModel()))

    result = medgemma.generate_response(prompt, max_new_tokens=5)
    assert result == "decoded"
