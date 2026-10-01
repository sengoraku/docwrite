import os
import sys
import json
import urllib.request

OLLAMA_URL = "http://localhost:11434"

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php", ".c", ".cpp", ".h"}


def get_installed_model():
    """Auto-detect the first available Ollama model."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags") as response:
            data = json.loads(response.read())
            models = data.get("models", [])
            if not models:
                print("No Ollama models found. Run 'ollama pull <model>' first.")
                sys.exit(1)
            return models[0]["name"]
    except Exception as e:
        print(f"Could not connect to Ollama. Is it running? Error: {e}")
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
    return "\n".join(collected)


def generate_readme(model, code_context):
    """Send codebase content to Ollama and get generated README text."""
    prompt = (
        "You are a technical writer. Based on the following codebase, "
        "write a clear, well-structured README.md file. Include a project "
        "title, description, installation steps, and usage instructions.\n\n"
        f"CODEBASE:\n{code_context}\n\nREADME.md:"
    )

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=300) as response:
        result = json.loads(response.read())
        return result.get("response", "")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py /path/to/project")
        sys.exit(1)

    target_path = sys.argv[1]
    if not os.path.isdir(target_path):
        print(f"Error: {target_path} is not a valid directory.")
        sys.exit(1)

    print("Detecting installed Ollama model...")
    model = get_installed_model()
    print(f"Using model: {model}")

    print("Reading codebase...")
    code_context = read_codebase(target_path)

    if not code_context.strip():
        print("No recognizable code files found in that directory.")
        sys.exit(1)

    print("Generating README (this may take a minute)...")
    readme_content = generate_readme(model, code_context)

    output_path = os.path.join(target_path, "README.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Done! README written to {output_path}")


if __name__ == "__main__":
    main()
