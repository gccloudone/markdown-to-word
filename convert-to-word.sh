#!/usr/bin/env bash
set -euo pipefail

# === CONFIGURATION ===
DEFAULT_TITLE="[Untitled Document]"        # Default title for the DOCX file
DEFAULT_MD_FILE="docs/sample.md"          # Default Markdown file path
DEFAULT_OUTPUT_FILE="output/sample.docx"  # Default output file path
DEFAULT_CLASSIFICATION="UNCLASSIFIED"                 # Classification text (e.g., "UNCLASSIFIED")

# Resolve the repository and script directories so relative paths work from any working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR" && pwd)"

# Allow overriding defaults with environment variables or CLI arguments.
# Handle cases where fewer arguments are passed (for backward compatibility)
TITLE="${1:-${TITLE:-$DEFAULT_TITLE}}"                # First argument, environment var, or default title
MARKDOWN_FILE="${2:-${MARKDOWN_FILE:-$DEFAULT_MD_FILE}}"      # Second argument, env var, or default Markdown file
OUTPUT_FILE="${3:-${OUTPUT_FILE:-$DEFAULT_OUTPUT_FILE}}"    # Third argument, env var, or default output DOCX file
CLASSIFICATION="${4:-${CLASSIFICATION:-$DEFAULT_CLASSIFICATION}}"  # Fourth argument: classification text (e.g., "UNCLASSIFIED")

# === FUNCTIONS ===
usage() {
    echo "Usage: $0 [title] [markdown_file] [output_file] [classification]"
    echo "  title: Title to set in the DOCX metadata (default: '$DEFAULT_TITLE')."
    echo "  markdown_file: Path to the Markdown file (default: '$DEFAULT_MD_FILE')."
    echo "  output_file: Path to the output DOCX file (default: '$DEFAULT_OUTPUT_FILE')."
    echo "  classification: Classification text for header (default: '$DEFAULT_CLASSIFICATION')."
    exit 1
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
fi

# === CHECK DEPENDENCIES ===
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: 'python3' is not installed. Please install it and try again."
    exit 1
fi

if ! python3 -c 'import docx' >/dev/null 2>&1; then
    echo "❌ Error: Python package 'python-docx' is not installed. Install it with 'pip3 install -r requirements.txt'."
    exit 1
fi

if ! python3 -c 'from md2docx import convert' >/dev/null 2>&1; then
    echo "❌ Error: Python package 'md2docx-python' is not installed. Install it with 'pip3 install -r requirements.txt'."
    exit 1
fi

# === RESOLVE PATHS ===
WORKSPACE_ROOT="${GITHUB_WORKSPACE:-$PWD}"

if [[ "$MARKDOWN_FILE" != /* ]]; then
    MARKDOWN_FILE="$WORKSPACE_ROOT/$MARKDOWN_FILE"
fi
if [[ "$OUTPUT_FILE" != /* ]]; then
    OUTPUT_FILE="$WORKSPACE_ROOT/$OUTPUT_FILE"
fi

# === EXTRACT METADATA FROM YAML FRONTMATTER ===
echo "📖 Checking for YAML frontmatter metadata..."
python3 "$REPO_ROOT/scripts/extract_metadata.py" "$MARKDOWN_FILE" > /tmp/metadata.txt 2>&1 || true

# Extract metadata values
if [[ -f /tmp/metadata.txt ]]; then
    while IFS= read -r line; do
        if [[ "$line" == Metadata* ]]; then
            continue
        fi
        if [[ "$line" == *:* ]]; then
            key=$(echo "$line" | cut -d: -f1 | xargs)
            value=$(echo "$line" | cut -d: -f2- | xargs)
            case "$key" in
                title)
                    if [[ -z "$TITLE" || "$TITLE" == "$DEFAULT_TITLE" ]]; then
                        TITLE="$value"
                    fi
                    ;;
                classification)
                    if [[ -z "$CLASSIFICATION" || "$CLASSIFICATION" == "$DEFAULT_CLASSIFICATION" ]]; then
                        CLASSIFICATION="$value"
                    fi
                    ;;
            esac
        fi
    done < /tmp/metadata.txt
    
    echo "   ✅ Metadata: title='$TITLE', classification='$CLASSIFICATION'"
fi

# === CHECK FILES ===
if [[ ! -f "$MARKDOWN_FILE" ]]; then
    echo "❌ Error: Markdown file '$MARKDOWN_FILE' not found."
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

# === CONVERT TO WORD ===
echo "🔄 Converting '$MARKDOWN_FILE' to '$OUTPUT_FILE' with title '$TITLE' and classification '$CLASSIFICATION'..."
python3 "$REPO_ROOT/scripts/convert_with_md2docx.py" "$MARKDOWN_FILE" "$OUTPUT_FILE" "$TITLE" "$CLASSIFICATION"
EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ Conversion successful: $OUTPUT_FILE"
else
    echo "❌ Conversion failed."
    exit $EXIT_CODE
fi
