"""Outline generation service."""

import json
from typing import Dict, Any, List, Optional

from openai import OpenAI

from app.config import settings


class OutlineService:
    """Service for generating document outlines."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.model = settings.OPENROUTER_MODEL

    async def generate_outline(
        self,
        topic: str,
        research: Dict[str, Any],
        template_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a document outline.

        Args:
            topic: The document topic.
            research: Research results.
            template_config: Template-specific configuration.

        Returns:
            Document outline structure.
        """
        # Extract key research points for context
        key_findings = research.get("key_findings", [])[:5]
        statistics = research.get("statistics", [])[:5]
        trends = research.get("trends", [])[:3]

        template_guidance = ""
        if template_config:
            template_guidance = f"""
Template specifications:
- Style: {template_config.get('style', 'professional')}
- Target length: {template_config.get('target_pages', 8)} pages
- Sections required: {template_config.get('required_sections', 'executive summary, introduction, main content, conclusion')}
"""

        prompt = f"""You are a content strategist creating a thought leadership document outline.

Topic: {topic}

Key Research Findings:
{json.dumps(key_findings, indent=2)}

Relevant Statistics:
{json.dumps(statistics, indent=2)}

Industry Trends:
{json.dumps(trends, indent=2)}
{template_guidance}

Create a comprehensive document outline in the following JSON structure:
{{
    "title": "Compelling document title",
    "subtitle": "Supporting subtitle",
    "executive_summary": {{
        "key_points": ["..."],
        "target_word_count": 300
    }},
    "sections": [
        {{
            "id": "section_1",
            "title": "Section Title",
            "purpose": "What this section accomplishes",
            "subsections": [
                {{
                    "id": "subsection_1_1",
                    "title": "Subsection Title",
                    "key_points": ["..."],
                    "target_word_count": 400,
                    "include_statistic": true,
                    "include_chart": false
                }}
            ],
            "target_word_count": 800
        }}
    ],
    "conclusion": {{
        "key_takeaways": ["..."],
        "call_to_action": "...",
        "target_word_count": 300
    }},
    "metadata": {{
        "estimated_total_words": 3500,
        "estimated_pages": 8,
        "reading_time_minutes": 15,
        "difficulty_level": "executive"
    }}
}}

Create an outline that would result in a compelling, executive-quality thought leadership document with 6-10 main sections."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://paper.aiconnected.com",
                "X-Title": "Paper by aiConnected",
            },
        )

        response_text = response.choices[0].message.content

        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass

        # Return a basic outline structure if parsing fails
        return {
            "title": topic,
            "subtitle": "",
            "executive_summary": {"key_points": [], "target_word_count": 300},
            "sections": [
                {
                    "id": "section_1",
                    "title": "Introduction",
                    "purpose": "Introduce the topic",
                    "subsections": [],
                    "target_word_count": 500,
                }
            ],
            "conclusion": {"key_takeaways": [], "call_to_action": "", "target_word_count": 300},
            "metadata": {"estimated_total_words": 2000, "estimated_pages": 5},
            "raw_response": response_text,
        }

    async def refine_outline(
        self,
        outline: Dict[str, Any],
        feedback: str,
    ) -> Dict[str, Any]:
        """
        Refine an outline based on feedback.

        Args:
            outline: Current outline.
            feedback: Refinement feedback.

        Returns:
            Refined outline.
        """
        prompt = f"""You are a content strategist refining a document outline based on feedback.

Current Outline:
{json.dumps(outline, indent=2)}

Feedback for refinement:
{feedback}

Please refine the outline based on the feedback and return the updated outline in the same JSON structure. Maintain all fields and improve based on the specific feedback provided."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://paper.aiconnected.com",
                "X-Title": "Paper by aiConnected",
            },
        )

        response_text = response.choices[0].message.content

        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass

        # Return original outline if refinement fails
        return outline
