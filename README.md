# Markdown to Word Converter

This repository provides a script and GitHub Action to convert a Markdown file to a Word document (`.docx`) using **md2docx-python** for optimal table rendering.

## Usage

Convert a Markdown file to Word locally:

```bash
./convert-to-word.sh "My Document Title" docs/sample.md output/sample.docx "UNCLASSIFIED"
```

You can also override defaults with environment variables:

```bash
TITLE="My Document" MARKDOWN_FILE="docs/sample.md" OUTPUT_FILE="output/sample.docx" CLASSIFICATION="UNCLASSIFIED" ./convert-to-word.sh
```

## Requirements

- `python3` (3.7+ recommended)
- Python packages from `requirements.txt`:
  - `python-docx` - For DOCX manipulation
  - `PyYAML` - For YAML frontmatter parsing
  - `md2docx-python` - For Markdown to DOCX conversion

Install dependencies:

```bash
pip install -r requirements.txt
```

## Features

- **Native table support** - md2docx-python handles markdown tables beautifully in Word
- **Custom headers** - Title and classification (e.g., UNCLASSIFIED) are added to the document header
- **YAML frontmatter** - Automatically extracts title and classification from markdown metadata
- **No external dependencies** - Only Python and pip packages required (no pandoc, no Node.js)

## Notes

- The script resolves relative paths from the repository root.
- Output directories are created automatically.
- The title and classification are added to the Word document header.
- Markdown tables are converted natively without pre-processing.

## GitHub Action

This repository also includes a composite GitHub Action. To use it from a workflow:

```yaml
name: Markdown to Word
on:
  workflow_dispatch:

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: gccloudone/markdown-to-word@main
        with:
          default_title: "My Document"
          markdown_file: "docs/sample.md"
          output_file: "output/sample.docx"
          classification: "UNCLASSIFIED"
```

The action installs Python dependencies from `requirements.txt` and then runs the conversion with md2docx-python.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `default_title` | Yes | - | Default title for the document |
| `markdown_file` | Yes | - | Path to the Markdown file |
| `output_file` | No | `output/output.docx` | Output DOCX file path |
| `classification` | No | `UNCLASSIFIED` | Classification text for header |

## Extracting Metadata from Markdown

The converter automatically extracts metadata from YAML frontmatter in your markdown file:

```markdown
---
title: My Document Title
classification: UNCLASSIFIED
---

# Content here...
```

If frontmatter is present, it will be used instead of the provided inputs.
