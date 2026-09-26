# docwrite

CLI tool that generates README documentation for your codebase using a local LLM — no cloud API, no cost.

## What it does

docwrite reads through your codebase, understands what it does, and drafts a README for you — automatically. It runs against a local LLM through [Ollama](https://ollama.com), so your code never leaves your machine.

## Why local?

- **Private** — your code is never sent to a cloud API
- **Free** — no API keys, no per-token cost
- **Flexible** — auto-detects and uses whatever Ollama model you already have installed (Llama 3, Mistral, DeepSeek Coder, etc.)

## Requirements

- [Ollama](https://ollama.com) installed, with at least one model pulled
- Node.js and Python installed

## Quickstart

```bash
git clone https://github.com/sengoraku/docwrite.git
cd docwrite
# setup + usage instructions coming soon
