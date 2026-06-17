import os
import sys
import requests
from google import genai
from google.genai.errors import APIError


def prompt_ollama(model: str, prompt: str) -> str:

    url = "http://127.0.0.1:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get(
            "response", "Error: Empty response payload received."
        )
    except requests.exceptions.Timeout:
        return "[Ollama Error] Request timed out. The local model is taking too long to load."
    except requests.exceptions.RequestException as e:
        return f"[Ollama Error] Connection failed: {e}"


def prompt_gemini(model: str, prompt: str) -> str:

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "[Gemini Error] Setup failure: The 'GEMINI_API_KEY' environment variable is not defined."

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except APIError as e:
        return f"[Gemini Error] {e.code} {e.message}"
    except Exception as e:
        return f"[Gemini Error] An unexpected runtime execution error occurred: {e}"


def prompt_model(model: str, prompt: str) -> str:

    ollama_models = {"llama3.1", "phi3", "deepseek-r1:1.5b"}
    gemini_models = {
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
    }

    if model in ollama_models or "deepseek" in model:
        return prompt_ollama(model, prompt)
    elif model in gemini_models:
        return prompt_gemini(model, prompt)
    else:
        return f"[Error] Validation failure: '{model}' is not recognized as a valid deployment option."


def main():

    if len(sys.argv) < 3:
        print("Usage Error: Missing arguments.")
        print(
            'Format Required: uv run prompt_mode..py <model_name> "<evaluation_prompt>"'
        )
        sys.exit(1)

    model_argument = sys.argv[1]
    prompt_argument = sys.argv[2]

    generated_text = prompt_model(model_argument, prompt_argument)
    print("\n--- RESPONSE ---\n")
    print(generated_text)


if __name__ == "__main__":
    main()
