import fitz # PyMuPDF
import os

def create_simple_pdf(title: str, content: str, output_path: str):
    """
    Creates a simple PDF document with a title and content.

    :param title: The document title.
    :param content: The main text content of the PDF.
    :param output_path: The path to save the generated PDF file.
    """
    doc = fitz.open() # Create a new empty PDF
    page = doc.new_page() # Add a new page

    # Define positions and fonts
    title_rect = fitz.Rect(50, 50, 550, 100)
    content_rect = fitz.Rect(50, 120, 550, 750)

    # Insert title
    page.insert_textbox(
        title_rect,
        title,
        fontsize=24,
        fontname="helv-b", # Helvetica Bold
        align=fitz.TEXT_ALIGN_CENTER
    )

    # Insert content
    page.insert_textbox(
        content_rect,
        content,
        fontsize=12,
        fontname="helv", # Helvetica
        align=fitz.TEXT_ALIGN_LEFT
    )

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the document
    doc.save(output_path)
    doc.close()

    return output_path
