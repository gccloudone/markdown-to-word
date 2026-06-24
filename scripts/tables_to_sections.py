#!/usr/bin/env python3
"""
Convert markdown tables to better Word-compatible formats.

This script transforms markdown tables into properly formatted content 
for Word documents, addressing various rendering issues.

Usage:
    python tables_to_sections.py <input_file.md> [output_file.md] [format]

Formats:
    'split'      - Each row as separate small table (RECOMMENDED for Word)
    'definition' - **Header:** value (bold labels, no headings)
    'columns'    - ## Header\nvalue (headers as actual headings)
    'pair'       - ### Header1: Value1 | Header2: Value2 (compact, all in one heading)
    'list'       - - **Header:** value (bullet list)
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


def table_to_columns_format(headers, rows, heading_level=2):
    """Convert table to columns format: Each cell as separate section with header as heading and value as content"""
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


def table_to_definition_format(headers, rows):
    """Convert table to definition/list format: Cleaner look with headers as bold text, not headings"""
    sections = []
    for row in rows:
        if len(row) != len(headers):
            continue
        for header, value in zip(headers, row):
            if value:  # Only add non-empty values
                sections.append(f"**{header}:** {value}")
        sections.append('')  # Blank line between rows
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


def table_to_split_format(headers, rows):
    """Convert table to multiple small tables - each row becomes its own table"""
    tables = []
    for row in rows:
        if len(row) != len(headers):
            continue
        # Create a small table for this row
        table_lines = []
        # Header row
        table_lines.append('| ' + ' | '.join(headers) + ' |')
        # Separator row
        table_lines.append('|' + '|'.join([' --- ' for _ in headers]) + '|')
        # Data row
        table_lines.append('| ' + ' | '.join(row) + ' |')
        tables.append('\n'.join(table_lines))
    return '\n\n'.join(tables)


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
                elif format_type == 'definition':
                    converted = table_to_definition_format(
                        table_data['headers'], 
                        table_data['rows']
                    )
                elif format_type == 'split':
                    converted = table_to_split_format(
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
        print("  'split'      - Each row as separate small table (RECOMMENDED for Word) - DEFAULT")
        print("  'definition' - **Header:** value (bold labels, no headings)")
        print("  'columns'    - ## Header\\nvalue (headers as headings, level 2)")
        print("  'pair'       - ### Header1: Value1 | Header2: Value2 (compact)")
        print("  'list'       - - **Header:** value (bullet list)")
        print()
        print("Example:")
        print("  python tables_to_sections.py docs/ra-03.md docs/ra-03-fixed.md split")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    format_type = sys.argv[3] if len(sys.argv) > 3 else 'split'
    heading_level = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    
    convert_markdown(input_file, output_file, format_type, heading_level)
