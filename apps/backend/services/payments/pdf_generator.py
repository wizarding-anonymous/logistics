import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def create_pdf_from_template(template_name: str, context: dict, output_path: str) -> str:
    """
    Renders an HTML template with the given context and converts it to a PDF.

    :param template_name: The name of the HTML template file.
    :param context: A dictionary with data to render in the template.
    :param output_path: The path to save the generated PDF file.
    """
    # Set up Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)

    # Render the HTML template
    html_out = template.render(context)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Generate PDF from HTML
    HTML(string=html_out).write_pdf(output_path)

    return output_path
