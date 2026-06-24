#!/usr/bin/env python3
"""
Convert markdown tables to sections/headings for better Word rendering.

This script transforms markdown tables into properly formatted sections where
each row becomes a heading with its content, making them render beautifully in Word.

Usage:
    python tables_to_sections.py <input_file.md> [output_file.md] [format]

Formats:
    'pair'     - Each row: "### Header1: Value1 | Header2: Value2" (default)
    'columns'  - Each cell as separate section: "### Header1\nValue1\n### Header2\nValue2"
    'list'     - Bullet list format: "- **Header1:** Value1"
"""

import sys
import re
from datetime import datetime


def parse_markdown_table(table_text):
    """
    Parse a markdown table into headers and rows.
    
    Args:
        table_text: String containing the markdown table
        
    Returns:
        dict with 'headers' and 'rows' lists, or None if not a valid table
    """
    lines = table_text.strip().split('\n')
    
    if len(lines) < 2:
        return None
    
    # Parse header row (first line)
    header_line = lines[0].strip()
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    # Validate separator line (second line should contain dashes, pipes, colons, spaces)
    separator_line = lines[1].strip()
    if not re.match(r'^[\|\-:\s]+$', separator_line):
        return None
    
    # Parse data rows
    rows = []
    for line in lines[2:]:
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if cells:
            rows.append(cells)
    
    return {'headers': headers, 'rows': rows}


def table_to_pair_format(headers, rows, heading_level=3):
    """Convert table to pair format: ### Header1: Value1 | Header2: Value2"""
    sections = []
    for row in rows:
        if len(row) != len(headers):
            continue
        pairs = []
        for header, value in zip(headers, row):
            pairs.append(f"**{header}:** {value}")
        section = f"{'#' * heading_level} {' | '.join(pairs)}"
        sections.append(section)
        sections.append('')  # Empty line between sections
    return '\n'.join(sections)


def table_to_columns_format(headers, rows, heading_level=3):
    """Convert table to columns format: Each cell as separate section"""
    sections = []
    for row in rows:
        if len(row) != len(headers):
            continue
        for header, value in zip(headers, row):
            if value:  # Only add non-empty values
                sections.append(f"{'#' * heading_level} {header}")
                sections.append(f"{value}")
                sections.append('')
    return '\n'.join(sections)


def table_to_list_format(headers, rows):
    """Convert table to bullet list format"""
    lines = []
    for row in rows:
        if len(row) != len(headers):
            continue
        for header, value in zip(headers, row):
            if value:
                lines.append(f"- **{header}:** {value}")
    return '\n'.join(lines)


def convert_markdown(input_path, output_path=None, format_type='pair', heading_level=3):
    """
    Convert markdown file tables to sections.
    
    Args:
        input_path: Path to input markdown file
        output_path: Path to output markdown file (default: overwrite input)
        format_type: 'pair', 'columns', or 'list'
        heading_level: Heading level for sections (1-6)
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content by lines
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a table
        if line.strip().startswith('|') and line.strip().endswith('|'):
            # Collect the entire table
            table_lines = [line]
            i += 1
            while i < len(lines) and (lines[i].strip().startswith('|') or 
                     re.match(r'^[\|\-: \t]+$', lines[i].strip())):
                table_lines.append(lines[i])
                i += 1
            
            table_text = '\n'.join(table_lines)
            table_data = parse_markdown_table(table_text)
            
            if table_data:
                # Convert table based on format
                if format_type == 'columns':
                    converted = table_to_columns_format(
                        table_data['headers'], 
                        table_data['rows'], 
                        heading_level
                    )
                elif format_type == 'list':
                    converted = table_to_list_format(
                        table_data['headers'], 
                        table_data['rows']
                    )
                else:  # 'pair' format (default)
                    converted = table_to_pair_format(
                        table_data['headers'], 
                        table_data['rows'], 
                        heading_level
                    )
                
                result_lines.append(converted)
                continue
        
        result_lines.append(line)
        i += 1
    
    output_content = '\n'.join(result_lines)
    
    # Write output
    if output_path is None:
        output_path = input_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"✅ Converted {input_path} to {output_path}")
    print(f"   Format: {format_type}, Heading level: {heading_level}")
    
    # Count tables converted
    table_starts = [i for i, line in enumerate(lines) if line.strip().startswith('|') and line.strip().endswith('|')]
    print(f"   Tables converted: {len(table_starts)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tables_to_sections.py <input_file.md> [output_file.md] [format] [heading_level]")
        print()
        print("Formats:")
        print("  'pair'     - Each row: '### Header1: Value1 | Header2: Value2' (default)")
        print("  'columns'  - Each cell as separate section: '### Header1\\nValue1' ")
        print("  'list'     - Bullet list format: '- **Header1:** Value1'")
        print()
        print("Example:")
        print("  python tables_to_sections.py docs/ra-03.md docs/ra-03-fixed.md pair 3")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    format_type = sys.argv[3] if len(sys.argv) > 3 else 'pair'
    heading_level = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    
    convert_markdown(input_file, output_file, format_type, heading_level)
