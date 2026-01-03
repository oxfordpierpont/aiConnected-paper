"""PDF generation service."""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS


class PDFService:
    """Service for PDF generation using WeasyPrint."""

    def __init__(self, templates_path: str = "app/templates"):
        self.templates_path = Path(templates_path)
        self.env = Environment(loader=FileSystemLoader(str(self.templates_path)))

        # Default branding colors
        self.default_branding = {
            "primary_color": "#1a4a6e",
            "secondary_color": "#b8860b",
            "accent_color": "#2980b9",
            "text_color": "#333333",
            "background_color": "#ffffff",
            "font_family": "Inter, sans-serif",
        }

    def render_html(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render HTML from a template."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    async def generate_pdf(
        self,
        content: Dict[str, Any],
        template_id: Optional[UUID] = None,
        branding: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Generate a PDF from document content.

        Args:
            content: The document content with sections, statistics, charts.
            template_id: Optional template ID for styling.
            branding: Optional branding configuration.

        Returns:
            PDF as bytes.
        """
        # Merge branding with defaults
        brand = {**self.default_branding, **(branding or {})}

        # Build the PDF context
        context = {
            "title": content.get("title", "Untitled Document"),
            "subtitle": content.get("subtitle", ""),
            "executive_summary": content.get("executive_summary", ""),
            "sections": content.get("sections", []),
            "conclusion": content.get("conclusion", {}),
            "statistics": content.get("statistics", []),
            "metadata": content.get("metadata", {}),
            "branding": brand,
        }

        # Handle charts (convert bytes to base64 for embedding)
        charts = []
        for chart in content.get("charts", []):
            if isinstance(chart.get("data"), bytes):
                chart_base64 = base64.b64encode(chart["data"]).decode("utf-8")
                charts.append({
                    "type": chart.get("type"),
                    "title": chart.get("title"),
                    "data_uri": f"data:image/png;base64,{chart_base64}",
                })
        context["charts"] = charts

        # Determine template
        template_name = "documents/thought_leadership.html"

        # Check if template exists, fall back to default
        try:
            html_content = self.render_html(template_name, context)
        except Exception:
            # Use inline template if file doesn't exist
            html_content = self._generate_default_html(context)

        # Generate CSS with branding
        css_content = self._generate_branded_css(brand)

        # Generate PDF
        html = HTML(string=html_content)
        stylesheets = [CSS(string=css_content)]

        return html.write_pdf(stylesheets=stylesheets)

    def _generate_default_html(self, context: Dict[str, Any]) -> str:
        """Generate default HTML if template doesn't exist."""
        sections_html = ""
        for section in context.get("sections", []):
            section_html = f"<section class='section'><h2>{section.get('title', '')}</h2>"
            if section.get("content"):
                section_html += f"<div class='content'>{section['content']}</div>"
            for subsection in section.get("subsections", []):
                section_html += f"<h3>{subsection.get('title', '')}</h3>"
                section_html += f"<div class='content'>{subsection.get('content', '')}</div>"
            section_html += "</section>"
            sections_html += section_html

        charts_html = ""
        for chart in context.get("charts", []):
            charts_html += f"""
            <div class="chart">
                <h4>{chart.get('title', '')}</h4>
                <img src="{chart.get('data_uri', '')}" alt="{chart.get('title', '')}">
            </div>
            """

        stats_html = ""
        highlight_stats = [s for s in context.get("statistics", []) if s.get("highlight_worthy")][:3]
        for stat in highlight_stats:
            stats_html += f"""
            <div class="stat-box">
                <div class="stat-value">{stat.get('value', '')}</div>
                <div class="stat-context">{stat.get('context', '')}</div>
            </div>
            """

        conclusion = context.get("conclusion", {})
        conclusion_html = ""
        if conclusion:
            conclusion_html = f"""
            <section class="conclusion">
                <h2>Conclusion</h2>
                <div class="content">{conclusion.get('content', '')}</div>
                {f"<div class='cta'>{conclusion.get('call_to_action', '')}</div>" if conclusion.get('call_to_action') else ''}
            </section>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{context.get('title', '')}</title>
        </head>
        <body>
            <header class="document-header">
                <h1 class="title">{context.get('title', '')}</h1>
                {f"<p class='subtitle'>{context.get('subtitle', '')}</p>" if context.get('subtitle') else ''}
            </header>

            {f"<section class='executive-summary'><h2>Executive Summary</h2><div class='content'>{context.get('executive_summary', '')}</div></section>" if context.get('executive_summary') else ''}

            <div class="stats-container">{stats_html}</div>

            <main>{sections_html}</main>

            <div class="charts-container">{charts_html}</div>

            {conclusion_html}

            <footer class="document-footer">
                <p>Generated by Paper by aiConnected</p>
            </footer>
        </body>
        </html>
        """

    def _generate_branded_css(self, brand: Dict[str, Any]) -> str:
        """Generate CSS with branding colors."""
        return f"""
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
            @bottom-center {{
                content: counter(page);
                font-size: 10pt;
                color: {brand.get('text_color', '#333')};
            }}
        }}

        body {{
            font-family: {brand.get('font_family', 'Inter, sans-serif')};
            color: {brand.get('text_color', '#333')};
            background-color: {brand.get('background_color', '#fff')};
            line-height: 1.6;
            font-size: 11pt;
        }}

        .document-header {{
            text-align: center;
            margin-bottom: 2cm;
            padding-bottom: 1cm;
            border-bottom: 3px solid {brand.get('primary_color', '#1a4a6e')};
        }}

        .title {{
            font-size: 28pt;
            color: {brand.get('primary_color', '#1a4a6e')};
            margin-bottom: 0.5cm;
            font-weight: 700;
        }}

        .subtitle {{
            font-size: 14pt;
            color: {brand.get('secondary_color', '#b8860b')};
            font-style: italic;
        }}

        h2 {{
            font-size: 18pt;
            color: {brand.get('primary_color', '#1a4a6e')};
            margin-top: 1.5cm;
            margin-bottom: 0.5cm;
            border-bottom: 1px solid {brand.get('accent_color', '#2980b9')};
            padding-bottom: 0.3cm;
        }}

        h3 {{
            font-size: 14pt;
            color: {brand.get('accent_color', '#2980b9')};
            margin-top: 1cm;
            margin-bottom: 0.3cm;
        }}

        .executive-summary {{
            background-color: #f8f9fa;
            padding: 1cm;
            border-left: 4px solid {brand.get('secondary_color', '#b8860b')};
            margin-bottom: 1.5cm;
        }}

        .stats-container {{
            display: flex;
            justify-content: space-between;
            gap: 1cm;
            margin: 1.5cm 0;
        }}

        .stat-box {{
            flex: 1;
            background-color: {brand.get('primary_color', '#1a4a6e')};
            color: white;
            padding: 1cm;
            text-align: center;
            border-radius: 0.2cm;
        }}

        .stat-value {{
            font-size: 24pt;
            font-weight: 700;
            color: {brand.get('secondary_color', '#b8860b')};
        }}

        .stat-context {{
            font-size: 10pt;
            margin-top: 0.3cm;
        }}

        .section {{
            margin-bottom: 1cm;
            page-break-inside: avoid;
        }}

        .content {{
            text-align: justify;
        }}

        .content p {{
            margin-bottom: 0.5cm;
        }}

        .charts-container {{
            margin: 1.5cm 0;
        }}

        .chart {{
            margin: 1cm 0;
            text-align: center;
            page-break-inside: avoid;
        }}

        .chart img {{
            max-width: 100%;
            height: auto;
        }}

        .chart h4 {{
            color: {brand.get('primary_color', '#1a4a6e')};
            font-size: 12pt;
            margin-bottom: 0.5cm;
        }}

        .conclusion {{
            margin-top: 2cm;
            padding-top: 1cm;
            border-top: 2px solid {brand.get('primary_color', '#1a4a6e')};
        }}

        .cta {{
            background-color: {brand.get('secondary_color', '#b8860b')};
            color: white;
            padding: 0.8cm;
            text-align: center;
            margin-top: 1cm;
            border-radius: 0.2cm;
            font-weight: 600;
        }}

        .document-footer {{
            margin-top: 2cm;
            text-align: center;
            font-size: 9pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 0.5cm;
        }}
        """

    def generate_pdf_sync(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: str,
        base_url: str = None,
    ) -> str:
        """Generate a PDF from a template (synchronous)."""
        html_content = self.render_html(template_name, context)

        stylesheets = []
        base_css_path = self.templates_path / "base" / "styles.css"
        if base_css_path.exists():
            stylesheets.append(CSS(filename=str(base_css_path)))

        html = HTML(string=html_content, base_url=base_url)
        html.write_pdf(output_path, stylesheets=stylesheets)

        return output_path

    def generate_pdf_bytes_sync(
        self,
        template_name: str,
        context: Dict[str, Any],
        base_url: str = None,
    ) -> bytes:
        """Generate a PDF and return as bytes (synchronous)."""
        html_content = self.render_html(template_name, context)

        stylesheets = []
        base_css_path = self.templates_path / "base" / "styles.css"
        if base_css_path.exists():
            stylesheets.append(CSS(filename=str(base_css_path)))

        html = HTML(string=html_content, base_url=base_url)
        return html.write_pdf(stylesheets=stylesheets)
