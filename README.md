# docwrite

CLI tool that generates README documentation for your codebase using a local LLM — no cloud API, no cost.

## What it does

docwrite reads through your codebase, understands what it does, and drafts a README for you — automatically. It runs against a local LLM through [Ollama](https://ollama.com), so your code never leaves your machine.

## Why local?

- **Private** — your code is never sent to a cloud API
- **Free** — no API keys, no per-token cost
- **Flexible** — auto-detects and uses whatever Ollama model you already have installed

## Requirements

- [Ollama](https://ollama.com) installed and running, with at least one model pulled (e.g. `ollama pull qwen2.5-coder:1.5b`)
- Python 3

## Usage

```bash
git clone https://github.com/sengoraku/docwrite.git
cd docwrite/python
python3 main.py /path/to/your/project
```

This generates a `README.md` directly inside the target project folder.

## Known limitations

- Smaller local models can occasionally invent plausible-but-incorrect setup details (e.g. a placeholder git URL, assumed dependency files that don't exist). Always review the generated README before publishing it.
- Generation speed depends on your hardware — CPU-only inference can take a minute or more for larger codebases.

## Status

🚧 Early development — core pipeline works, polish and a proper CLI wrapper coming.

## License

MIT
