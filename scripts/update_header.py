import sys
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def update_header(docx_path, title_text, font_size=14, bold=True, align='center'):
    """
    Update all headers in a Word document with the given title text.

    Args:
        docx_path: Path to the DOCX file
        title_text: Text to insert in the header
        font_size: Font size for the header text (default: 14)
        bold: Whether to make the text bold (default: True)
        align: Text alignment - 'left', 'center', or 'right' (default: 'center')
    """
    # Ensure the docx_path is an absolute path
    docx_path = os.path.abspath(docx_path)

    # Check if the file exists
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Error: Cannot find DOCX file at '{docx_path}'")

    # Load the document
    doc = Document(docx_path)

    # Map alignment strings to constants
    alignment_map = {
        'left': WD_PARAGRAPH_ALIGNMENT.LEFT,
        'center': WD_PARAGRAPH_ALIGNMENT.CENTER,
        'right': WD_PARAGRAPH_ALIGNMENT.RIGHT
    }
    alignment = alignment_map.get(align.lower(), WD_PARAGRAPH_ALIGNMENT.CENTER)

    # Update the headers in all sections
    for section in doc.sections:
        header = section.header

        # Clear all existing paragraphs in the header
        for paragraph in header.paragraphs:
            # Remove all runs to clear formatting
            for run in paragraph.runs:
                run.clear()
            # Clear the paragraph text
            paragraph.clear()

        # Remove all existing paragraphs
        for paragraph in header.paragraphs[:]:
            header._header.remove(paragraph._p)

        # Add a new paragraph with the title
        header_para = header.add_paragraph()
        header_para.text = title_text

        # Apply styling
        for run in header_para.runs:
            run.font.size = Pt(font_size)
            run.font.bold = bold
        header_para.alignment = alignment

    # Save the updated document
    doc.save(docx_path)
    print(f"Successfully updated header in '{docx_path}' with title: '{title_text}'")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_header.py <docx_path> <title_text> [font_size] [bold] [align]")
        print("Example: python update_header.py doc.docx 'My Document Title' 16 True center")
        sys.exit(1)

    docx_path = sys.argv[1]
    title_text = sys.argv[2]

    # Parse optional arguments with defaults
    font_size = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    bold = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else True
    align = sys.argv[5] if len(sys.argv) > 5 else 'center'

    update_header(docx_path, title_text, font_size, bold, align)
