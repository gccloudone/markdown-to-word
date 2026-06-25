#!/usr/bin/env python3
"""
Extract metadata from markdown files with YAML frontmatter or plain key:value.

This script reads markdown files and extracts metadata from either:
1. YAML frontmatter (--- ... ---)
2. Plain key:value pairs at the start of the file

Supported formats:

YAML frontmatter:
---
title: "My Document Title"
classification: "UNCLASSIFIED"
version: "1.0"
---

Plain key:value:
title: My Document Title
classification: UNCLASSIFIED
version: 1.0

Content starts after blank line...

Usage:
    python extract_metadata.py <input_file.md>
"""

import sys
import re


def extract_yaml_frontmatter(file_path):
    """
    Extract YAML frontmatter or plain key:value metadata from a markdown file.
    
    Supports both formats:
    1. YAML frontmatter:
       ---
       title: "My Title"
       classification: UNCLASSIFIED
       ---
       
    2. Plain key:value at start:
       title: My Title
       classification: UNCLASSIFIED
       
       (content starts here)
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        dict: Metadata from frontmatter, or empty dict if no metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {}
        
        # Try YAML frontmatter first (--- ... ---)
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            frontmatter = match.group(1)
            # Parse YAML
            try:
                import yaml
                yaml_meta = yaml.safe_load(frontmatter)
                if yaml_meta:
                    metadata.update(yaml_meta)
                return metadata
            except Exception:
                # YAML parsing failed, try simple key: value parsing
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
                return metadata
        
        # Try plain key:value metadata at the start (before first blank line or heading)
        lines = content.split('\n')
        in_metadata = True
        for line in lines:
            stripped = line.strip()
            # Stop if we hit a blank line or a heading
            if not stripped or stripped.startswith('#') or stripped.startswith('---'):
                if not stripped or stripped.startswith('#'):
                    break
                continue
            
            if ':' in stripped:
                key, value = stripped.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
            else:
                # If we hit a line without a colon and we have metadata, stop
                if metadata:
                    break
        
        return metadata
    except Exception as e:
        print(f"Warning: Could not read file {file_path}: {e}")
        return {}


def get_metadata(file_path, defaults=None):
    """
    Get metadata from file, with defaults.
    
    Args:
        file_path: Path to markdown file
        defaults: Default values (dict)
        
    Returns:
        dict: Combined metadata and defaults
    """
    if defaults is None:
        defaults = {}
    
    metadata = extract_yaml_frontmatter(file_path)
    if metadata is None:
        metadata = {}
    
    # Merge with defaults
    result = {**defaults, **metadata}
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_metadata.py <input_file.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    metadata = extract_yaml_frontmatter(file_path)
    
    print("Metadata extracted from", file_path)
    for key, value in metadata.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
