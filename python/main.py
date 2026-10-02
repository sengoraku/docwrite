import os
import sys
import json
import time
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434"

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php", ".c", ".cpp", ".h"}

MAX_CODE_CHARS = 15000
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3


def get_installed_model():
    """Auto-detect the first available Ollama model."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=10) as response:
            data = json.loads(response.read())
            models = data.get("models", [])
            if not models:
                print("No Ollama models found. Run 'ollama pull <model>' first.")
                sys.exit(1)
            return models[0]["name"]
    except urllib.error.URLError as e:
        print(f"Could not connect to Ollama at {OLLAMA_URL}. Is it running? ('ollama serve')")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while detecting model: {e}")
        sys.exit(1)


def read_codebase(path):
    """Walk the target folder and collect code file contents."""
    collected = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in CODE_EXTENSIONS:
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, path)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    collected.append(f"--- {relpath} ---\n{content}\n")
                except Exception:
                    continue

    full_text = "\n".join(collected)

    if len(full_text) > MAX_CODE_CHARS:
        print(
            f"Warning: codebase content is large ({len(full_text)} chars). "
            f"Truncating to the first {MAX_CODE_CHARS} characters for generation."
        )
        full_text = full_text[:MAX_CODE_CHARS] + "\n\n[... truncated for length ...]"

    return full_text


def generate_readme(model, code_context):
    """Send codebase content to Ollama and get generated README text, with retries."""
    prompt = (
        "You are a technical writer. Based on the following codebase, "
        "write a clear, well-structured README.md file. Include a project "
        "title, description, installation steps, and usage instructions. "
        "Only describe what is actually present in the code — do not invent "
        "URLs, package names, or setup steps that aren't shown.\n\n"
        f"CODEBASE:\n{code_context}\n\nREADME.md:"
    )

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read())
                return result.get("response", "")
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Failed to generate README after {MAX_RETRIES} attempts. Last error: {last_error}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py /path/to/project")
        sys.exit(1)

    target_path = sys.argv[1]
    if not os.path.isdir(target_path):
        print(f"Error: '{target_path}' is not a valid directory.")
        sys.exit(1)

    print("Detecting installed Ollama model...")
    model = get_installed_model()
    print(f"Using model: {model}")

    print("Reading codebase...")
    code_context = read_codebase(target_path)

    if not code_context.strip():
        print(
            f"No recognizable code files found in '{target_path}'. "
            f"Supported extensions: {', '.join(sorted(CODE_EXTENSIONS))}"
        )
        sys.exit(1)

    print("Sending to model — this may take a minute depending on your hardware...")
    readme_content = generate_readme(model, code_context)

    output_path = os.path.join(target_path, "README.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Done! README written to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nSomething went wrong: {e}")
        sys.exit(1)
