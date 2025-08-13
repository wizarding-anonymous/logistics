import os
import logging
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailClient:
    """
    A mock email client that renders HTML templates and logs the output
    instead of sending a real email.
    """
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        logging.info("EmailClient initialized.")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renders an HTML template with the given context."""
        template = self.jinja_env.get_template(template_name)
        return template.render(context)

    def send_email(self, to: str, subject: str, html_body: str):
        """
        Simulates sending an email by logging its components.
        In a real application, this method would contain the SMTP logic.
        """
        logging.info("--- MOCK EMAIL SEND ---")
        logging.info(f"TO: {to}")
        logging.info(f"SUBJECT: {subject}")
        logging.info(f"BODY (HTML):\n{html_body}")
        logging.info("-----------------------")
        # Here you would add the actual smtplib or other email library code.
        # For example:
        # with smtplib.SMTP("smtp.example.com", 587) as server:
        #     server.starttls()
        #     server.login("user", "password")
        #     server.sendmail("from@example.com", to, message.as_string())
        print(f"Simulated sending email to {to} with subject '{subject}'")

# Singleton instance of the email client
email_client = EmailClient()
