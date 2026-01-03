"""Statistics extraction service."""

import json
import re
from typing import List, Dict, Any

import anthropic

from app.config import settings


class StatisticsService:
    """Service for extracting and managing statistics."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    async def extract_statistics(
        self,
        content: str,
        research: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Extract statistics from content and research.

        Args:
            content: Generated content.
            research: Research results.

        Returns:
            List of extracted statistics with sources.
        """
        # Start with statistics from research
        research_stats = research.get("statistics", [])

        prompt = f"""You are a data analyst extracting statistics from content.

Content to analyze:
{content[:5000]}  # Limit content size

Research statistics already available:
{json.dumps(research_stats[:10], indent=2)}

Extract all statistics, numbers, and data points from the content. Return them in this JSON format:
{{
    "statistics": [
        {{
            "value": "The numerical value or percentage",
            "context": "What this statistic represents",
            "source": "Source attribution if mentioned",
            "category": "financial|market|operational|customer|research",
            "highlight_worthy": true,
            "visualization_type": "number|percentage|currency|comparison"
        }}
    ]
}}

Extract 5-15 key statistics that would be impactful for visualizations and callouts."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(response_text[start:end])
                return parsed.get("statistics", [])
        except json.JSONDecodeError:
            pass

        # Fallback: Extract numbers using regex
        extracted = []
        number_patterns = [
            (r"(\d+(?:\.\d+)?%)", "percentage"),
            (r"\$(\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:billion|million|trillion))?)", "currency"),
            (r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:billion|million|trillion)", "large_number"),
        ]

        for pattern, stat_type in number_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:  # Limit per type
                extracted.append({
                    "value": match if isinstance(match, str) else match[0],
                    "context": "Extracted from content",
                    "source": "Document content",
                    "category": "research",
                    "highlight_worthy": True,
                    "visualization_type": stat_type,
                })

        # Add research stats that weren't in content
        for stat in research_stats[:5]:
            extracted.append({
                "value": stat.get("value", ""),
                "context": stat.get("context", ""),
                "source": stat.get("source", "Research"),
                "category": "research",
                "highlight_worthy": True,
                "visualization_type": "number",
            })

        return extracted

    async def format_statistic(
        self,
        statistic: Dict[str, Any],
        style: str = "callout",
    ) -> Dict[str, Any]:
        """
        Format a statistic for display.

        Args:
            statistic: The statistic data.
            style: Display style ('callout', 'inline', 'chart_label').

        Returns:
            Formatted statistic.
        """
        value = statistic.get("value", "")
        context = statistic.get("context", "")
        source = statistic.get("source", "")

        formatted = {
            "value": value,
            "context": context,
            "source": source,
            "original": statistic,
        }

        if style == "callout":
            # Format for a large callout box
            formatted["display"] = {
                "primary": value,
                "secondary": context,
                "attribution": f"Source: {source}" if source else "",
                "css_class": "stat-callout",
            }
        elif style == "inline":
            # Format for inline text mention
            formatted["display"] = {
                "text": f"{value} - {context}",
                "css_class": "stat-inline",
            }
        elif style == "chart_label":
            # Format for chart axis or label
            formatted["display"] = {
                "label": value,
                "description": context[:50] if len(context) > 50 else context,
                "css_class": "chart-label",
            }
        else:
            formatted["display"] = {
                "primary": value,
                "secondary": context,
            }

        return formatted
