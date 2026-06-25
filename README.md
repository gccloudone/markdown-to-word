# Markdown to Word Converter

This repository provides a script and GitHub Action to convert a Markdown file to a Word document (`.docx`) using **Pandoc** with table pre-processing for optimal Word rendering.

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

- `pandoc` (tested with 3.9.0.2)
- `python3` (3.7+ recommended)
- `@mermaid-js/mermaid-cli` (for diagram support)
- Python packages from `requirements.txt`:
  - `python-docx` - For DOCX manipulation
  - `PyYAML` - For YAML frontmatter parsing

Install dependencies:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Pandoc (Ubuntu/Debian)
sudo apt-get install pandoc

# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli
```

## Features

- **Table pre-processing** - Converts markdown tables to small individual tables (split format) for better Word rendering
- **Custom headers** - Title and classification (e.g., UNCLASSIFIED) are added to the document header
- **YAML frontmatter** - Automatically extracts title and classification from markdown metadata
- **Mermaid diagram support** - Converts Mermaid diagrams to images
- **Page breaks** - Supports `<!-- new page -->` comments for page breaks

## Notes

- The script resolves relative paths from the repository root.
- Output directories are created automatically.
- The title and classification are added to the Word document header.
- Markdown tables are pre-processed into small individual tables for better Word rendering.
- Uses a reference DOCX template for consistent styling.

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
          reference_doc: "template/ssc-template-v2.7.dotx"
          convert_tables: "true"
          table_format: "split"
          classification: "UNCLASSIFIED"
```

The action installs dependencies (Pandoc, Node.js, Mermaid CLI, Python packages) and then runs the conversion.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `default_title` | Yes | - | Default title for the document |
| `markdown_file` | Yes | - | Path to the Markdown file |
| `output_file` | No | `output/output.docx` | Output DOCX file path |
| `reference_doc` | No | `template/ssc-template-v2.7.dotx` | Reference DOCX template |
| `convert_tables` | No | `true` | Convert tables to small individual tables |
| `table_format` | No | `split` | Table conversion format (split, definition, columns, pair, list) |
| `classification` | No | `UNCLASSIFIED` | Classification text for header |

## Extracting Metadata from Markdown

The converter automatically extracts metadata from YAML frontmatter in your markdown file:

```markdown
---
title: My Document Title
classification: UNCLASSIFIED
control: IR-4
---

# Content here...
```

If frontmatter is present, it will be used instead of the provided inputs. The YAML frontmatter is stripped from the output document.
