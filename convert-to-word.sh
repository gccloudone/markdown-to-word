#!/usr/bin/env bash
set -euo pipefail

# === CONFIGURATION ===
DEFAULT_TITLE="[Untitled Document]"        # Default title for the DOCX file
DEFAULT_MD_FILE="docs/sample.md"          # Default Markdown file path
DEFAULT_OUTPUT_FILE="output/sample.docx"  # Default output file path
DEFAULT_REFERENCE_DOC="template/ssc-template-v2.7.dotx"  # Default reference template
DEFAULT_CONVERT_TABLES="true"            # Convert tables to sections (true/false)
DEFAULT_TABLE_FORMAT="split"              # Table conversion format: split, definition, columns, pair, or list
DEFAULT_CLASSIFICATION="UNCLASSIFIED"                 # Classification text (e.g., "UNCLASSIFIED")

# Resolve the repository and script directories so relative paths work from any working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR" && pwd)"

# Allow overriding defaults with environment variables or CLI arguments.
# Handle cases where fewer arguments are passed (for backward compatibility)
TITLE="${1:-${TITLE:-$DEFAULT_TITLE}}"                # First argument, environment var, or default title
MARKDOWN_FILE="${2:-${MARKDOWN_FILE:-$DEFAULT_MD_FILE}}"      # Second argument, env var, or default Markdown file
OUTPUT_FILE="${3:-${OUTPUT_FILE:-$DEFAULT_OUTPUT_FILE}}"    # Third argument, env var, or default output DOCX file
REFERENCE_DOC="${4:-${REFERENCE_DOC:-$DEFAULT_REFERENCE_DOC}}" # Fourth argument, env var, or default reference template
CONVERT_TABLES="${5:-${CONVERT_TABLES:-$DEFAULT_CONVERT_TABLES}}"  # Fifth argument: convert tables to sections
TABLE_FORMAT="${6:-${TABLE_FORMAT:-$DEFAULT_TABLE_FORMAT}}"    # Sixth argument: table conversion format
CLASSIFICATION="${7:-${CLASSIFICATION:-$DEFAULT_CLASSIFICATION}}"  # Seventh argument: classification text (e.g., "UNCLASSIFIED")

# For backward compatibility: ensure reference_doc has a filename
if [[ -z "$REFERENCE_DOC" || "$REFERENCE_DOC" == */ ]]; then
    REFERENCE_DOC="${REFERENCE_DOC}template/ssc-template-v2.7.dotx"
fi

# === FUNCTIONS ===
usage() {
    echo "Usage: $0 [title] [markdown_file] [output_file] [reference_doc] [convert_tables] [table_format] [classification]"
    echo "  title: Title to set in the DOCX metadata (default: '$DEFAULT_TITLE')."
    echo "  markdown_file: Path to the Markdown file (default: '$DEFAULT_MD_FILE')."
    echo "  output_file: Path to the output DOCX file (default: '$DEFAULT_OUTPUT_FILE')."
    echo "  reference_doc: Path to the DOCX reference template (default: '$DEFAULT_REFERENCE_DOC')."
    echo "  convert_tables: Convert tables to sections for better Word rendering (default: '$DEFAULT_CONVERT_TABLES')."
    echo "  table_format: Table conversion format - split, definition, columns, pair, or list (default: '$DEFAULT_TABLE_FORMAT')."
    echo "  classification: Classification text for header (default: '$DEFAULT_CLASSIFICATION')."
    exit 1
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
fi

# === CHECK DEPENDENCIES ===
if ! command -v pandoc >/dev/null 2>&1; then
    echo "❌ Error: 'pandoc' is not installed. Please install it and try again."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: 'python3' is not installed. Please install it and try again."
    exit 1
fi

if ! python3 -c 'import docx' >/dev/null 2>&1; then
    echo "❌ Error: Python package 'python-docx' is not installed. Install it with 'pip3 install -r requirements.txt'."
    exit 1
fi

if ! command -v mmdc >/dev/null 2>&1; then
    echo "❌ Error: 'mmdc' (Mermaid CLI) is not installed. Please install @mermaid-js/mermaid-cli and try again."
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
if [[ "$REFERENCE_DOC" != /* ]]; then
    REFERENCE_DOC="$REPO_ROOT/$REFERENCE_DOC"
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

# === CONVERT TABLES TO SECTIONS (optional) ===
if [[ "$CONVERT_TABLES" == "true" ]]; then
    echo "📋 Converting tables to sections for better Word rendering..."
    TEMP_DIR="${RUNNER_TEMP:-/tmp}"
    TEMP_MD_FILE="$TEMP_DIR/$(date +%s)-converted.md"
    python3 "$REPO_ROOT/scripts/tables_to_sections.py" "$MARKDOWN_FILE" "$TEMP_MD_FILE" "$TABLE_FORMAT" "3"
    if [[ -f "$TEMP_MD_FILE" ]]; then
        MARKDOWN_FILE="$TEMP_MD_FILE"
    else
        echo "⚠️  Table conversion failed, using original file"
    fi
fi

# === CHECK FILES ===
if [[ ! -f "$MARKDOWN_FILE" ]]; then
    echo "❌ Error: Markdown file '$MARKDOWN_FILE' not found."
    exit 1
fi

if [[ ! -f "$REFERENCE_DOC" ]]; then
    echo "❌ Error: Reference DOCX template '$REFERENCE_DOC' not found."
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

# === CONVERT TO WORD ===
echo "🔄 Converting '$MARKDOWN_FILE' to '$OUTPUT_FILE' using template '$REFERENCE_DOC' with title '$TITLE'..."
pandoc "$MARKDOWN_FILE" --metadata=title:"$TITLE" \
                        --lua-filter="$REPO_ROOT/filters/pagebreak.lua" \
                        --lua-filter="$REPO_ROOT/filters/toc.lua" \
                        --lua-filter="$REPO_ROOT/filters/mermaid.lua" \
                        -o "$OUTPUT_FILE" \
                        --reference-doc="$REFERENCE_DOC"

# Run any additional processing scripts (if needed):
python3 "$REPO_ROOT/scripts/update_header.py" "$OUTPUT_FILE" "$TITLE" "$CLASSIFICATION"

# Update tables with better formatting (styles: grid, clean, borderless, custom)
# Always run table styling, even with converted tables
python3 "$REPO_ROOT/scripts/update_tables.py" "$OUTPUT_FILE" "clean" "6" "4472C4" "4" "center" "True" "True" "D9E2F3" "False" "9"
EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ Conversion successful: $OUTPUT_FILE"
else
    echo "❌ Conversion failed."
    exit $EXIT_CODE
fi

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ Conversion successful: $OUTPUT_FILE"
else
    echo "❌ Conversion failed."
    exit $EXIT_CODE
fi
