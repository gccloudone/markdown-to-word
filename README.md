# Markdown to Word Converter

This repository provides a script and GitHub Action to convert a Markdown file to a Word document (`.docx`) using Pandoc.

## Usage

Convert a Markdown file to Word locally:

```bash
./convert-to-word.sh "My Document Title" docs/sample.md output/sample.docx template/ssc-template-v2.7.dotx
```

You can also override defaults with environment variables:

```bash
TITLE="My Document" MARKDOWN_FILE="docs/sample.md" OUTPUT_FILE="output/sample.docx" REFERENCE_DOC="template/ssc-template-v2.7.dotx" ./convert-to-word.sh
```

## Requirements

- `pandoc`
- `python3`
- Python package `python-docx`
- `@mermaid-js/mermaid-cli` (`mmdc`)

## Notes

- The script resolves relative paths from the repository root.
- Output directories are created automatically.
