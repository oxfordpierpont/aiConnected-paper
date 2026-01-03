"""PDF generation service."""

from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS


class PDFService:
    """Service for PDF generation using WeasyPrint."""

    def __init__(self, templates_path: str = "app/templates"):
        self.templates_path = Path(templates_path)
        self.env = Environment(loader=FileSystemLoader(str(self.templates_path)))

    def render_html(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render HTML from a template."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def generate_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: str,
        base_url: str = None,
    ) -> str:
        """Generate a PDF from a template."""
        html_content = self.render_html(template_name, context)

        # Load base styles
        stylesheets = []
        base_css_path = self.templates_path / "base" / "styles.css"
        if base_css_path.exists():
            stylesheets.append(CSS(filename=str(base_css_path)))

        # Generate PDF
        html = HTML(string=html_content, base_url=base_url)
        html.write_pdf(output_path, stylesheets=stylesheets)

        return output_path

    def generate_pdf_bytes(
        self,
        template_name: str,
        context: Dict[str, Any],
        base_url: str = None,
    ) -> bytes:
        """Generate a PDF and return as bytes."""
        html_content = self.render_html(template_name, context)

        # Load base styles
        stylesheets = []
        base_css_path = self.templates_path / "base" / "styles.css"
        if base_css_path.exists():
            stylesheets.append(CSS(filename=str(base_css_path)))

        # Generate PDF
        html = HTML(string=html_content, base_url=base_url)
        return html.write_pdf(stylesheets=stylesheets)
