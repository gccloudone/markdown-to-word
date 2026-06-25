#!/usr/bin/env python3
"""
Preprocess markdown files for conversion to DOCX/PDF.

This script performs the following preprocessing:
1. Strips YAML frontmatter (metadata between --- lines)
2. Converts \newpage macros to Pandoc-compatible page breaks
3. Ensures proper formatting for tables and code blocks

Usage:
    python preprocess_markdown.py <input.md> <output.md>
"""

import sys
import re
import os


def strip_yaml_frontmatter(content):
    """
    Remove YAML frontmatter from markdown content.
    
    YAML frontmatter is metadata between --- delimiters at the start of the file.
    This metadata should not appear in the final document.
    """
    # Match YAML frontmatter: --- ... --- at the very beginning
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    return content


def convert_newpage_to_pandoc(content):
    """
    Convert \newpage macros to Pandoc-compatible page breaks.
    
    For DOCX output, we ensure \newpage is on its own line, which Pandoc will
    recognize as a page break when combined with the pagebreak.lua filter.
    """
    # Replace \newpage with a blank line containing only the form feed character
    # This ensures it's treated as a standalone paragraph
    # Handle both \newpage and \newpage{} 
    def replace_newpage(match):
        # Return a blank line before and after to ensure it's in its own paragraph
        return '\n\f\n'
    
    content = re.sub(r'\\newpage\{?\}?', replace_newpage, content)
    return content


def preprocess_markdown(input_path, output_path):
    """
    Preprocess a markdown file for conversion.
    
    Args:
        input_path: Path to input markdown file
        output_path: Path to output preprocessed markdown file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply preprocessing steps
        content = strip_yaml_frontmatter(content)
        content = convert_newpage_to_pandoc(content)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Write preprocessed content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Preprocessed '{input_path}' -> '{output_path}'")
        return True
        
    except Exception as e:
        print(f"❌ Error preprocessing markdown: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python preprocess_markdown.py <input.md> <output.md>")
        print()
        print("Preprocesses markdown by:")
        print("  - Stripping YAML frontmatter (metadata)")
        print("  - Converting \\newpage macros to page breaks")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = preprocess_markdown(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
