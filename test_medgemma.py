"""Simple script to exercise the Med-Gemma model implementation."""

from medgemma import generate_response


def main() -> None:
    prompt = "What imaging modality is typically used for soft tissue contrast?"
    print("Prompt:", prompt)
    print("Response:", generate_response(prompt, max_new_tokens=5))


if __name__ == "__main__":
    main()
