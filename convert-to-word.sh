#!/bin/bash
# === CONFIGURATION ===
DEFAULT_TITLE="[Untitled Document]"        # Default title for the DOCX file
DEFAULT_MD_FILE="sample.md"                # Default Markdown file path
DEFAULT_OUTPUT_FILE="output/sample.docx"   # Default output file path
DEFAULT_REFERENCE_DOC="template/ssc-template-v2.7.dotx"  # Default reference template

# Allow overriding defaults with environment variables or CLI arguments
TITLE="${1:-$DEFAULT_TITLE}"                # First argument or default title
MARKDOWN_FILE="${2:-$DEFAULT_MD_FILE}"      # Second argument or default Markdown file
OUTPUT_FILE="${3:-$DEFAULT_OUTPUT_FILE}"    # Third argument or default output DOCX file
REFERENCE_DOC="${4:-$DEFAULT_REFERENCE_DOC}" # Fourth argument or default reference template

# === FUNCTIONS ===
usage() {
    echo "Usage: $0 [title] [markdown_file] [output_file] [reference_doc]"
    echo "  title: Title to set in the DOCX metadata (default: '$DEFAULT_TITLE')."
    echo "  markdown_file: Path to the Markdown file (default: '$DEFAULT_MD_FILE')."
    echo "  output_file: Path to the output DOCX file (default: '$DEFAULT_OUTPUT_FILE')."
    echo "  reference_doc: Path to the DOCX reference template (default: '$DEFAULT_REFERENCE_DOC')."
    exit 1
}

# === CHECK DEPENDENCIES ===
if ! command -v pandoc &> /dev/null; then
    echo "❌ Error: 'pandoc' is not installed. Please install it and try again."
    exit 1
fi

# === CHECK FILES ===
if [[ ! -f "$MARKDOWN_FILE" ]]; then
    echo "❌ Error: Markdown file '$MARKDOWN_FILE' not found."
    exit 1
fi

if [[ ! -f "$REFERENCE_DOC" ]]; then
    echo "❌ Error: Reference DOCX template '$REFERENCE_DOC' not found in the 'template/' directory."
    exit 1
fi

if [ -z "$GITHUB_ACTION_PATH" ]; then
  export GITHUB_ACTION_PATH="."
fi

# === CONVERT TO WORD ===
echo "🔄 Converting '$MARKDOWN_FILE' to '$OUTPUT_FILE' using template '$REFERENCE_DOC' with title '$TITLE'..."
pandoc "$MARKDOWN_FILE" --metadata=title:"$TITLE" \
                        --lua-filter=$GITHUB_ACTION_PATH/filters/pagebreak.lua \
                        --lua-filter=$GITHUB_ACTION_PATH/filters/toc.lua \
                        -o "$OUTPUT_FILE" \
                        --reference-doc="$REFERENCE_DOC"

# Run any additional processing scripts (if needed):
python3 $GITHUB_ACTION_PATH/scripts/update_header.py "$OUTPUT_FILE" "$TITLE"
python3 $GITHUB_ACTION_PATH/scripts/update_tables.py "$OUTPUT_FILE"
EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ Conversion successful: $OUTPUT_FILE"
else
    echo "❌ Conversion failed."
    exit $EXIT_CODE
fi
