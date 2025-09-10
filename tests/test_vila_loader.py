from agent import vila_loader


def test_run_vlm_none():
    text, prob = vila_loader.run_vlm(None, "prompt")
    assert text.startswith("-"), text
    assert 0 <= prob <= 1


def test_run_vlm_generate(monkeypatch):
    class Dummy:
        def generate(self, prompt):
            return f"gen:{prompt}"

    text, prob = vila_loader.run_vlm(Dummy(), "hi")
    assert text == "gen:hi"
    assert prob == 0.75
