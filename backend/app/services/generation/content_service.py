"""Content writing service."""

import json
from typing import Dict, Any, List, Optional

import anthropic

from app.config import settings


class ContentService:
    """Service for generating written content."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    async def generate_section(
        self,
        section_title: str,
        context: Dict[str, Any],
        tone: str = "professional",
        word_count: int = 500,
    ) -> str:
        """
        Generate content for a section.

        Args:
            section_title: Title of the section.
            context: Context including research, outline, etc.
            tone: Writing tone.
            word_count: Target word count.

        Returns:
            Generated section content.
        """
        research_context = context.get("research", {})
        outline_context = context.get("outline", {})
        topic = context.get("topic", "")
        key_points = context.get("key_points", [])
        include_statistic = context.get("include_statistic", False)

        statistics_instruction = ""
        if include_statistic and research_context.get("statistics"):
            stats = research_context["statistics"][:3]
            statistics_instruction = f"""
Include at least one of these statistics naturally in the content:
{json.dumps(stats, indent=2)}
"""

        tone_descriptions = {
            "professional": "authoritative yet accessible, suitable for C-suite executives",
            "conversational": "friendly and engaging while maintaining expertise",
            "academic": "scholarly and research-focused with citations",
            "persuasive": "compelling and action-oriented, designed to influence decisions",
        }
        tone_desc = tone_descriptions.get(tone, tone_descriptions["professional"])

        prompt = f"""You are an expert content writer creating thought leadership content.

Document Topic: {topic}
Section Title: {section_title}
Target Word Count: {word_count} words
Tone: {tone_desc}

Key Points to Cover:
{json.dumps(key_points, indent=2) if key_points else "Cover the topic comprehensively"}
{statistics_instruction}

Write the content for this section. Requirements:
1. Write in a {tone} tone appropriate for executive readers
2. Include specific insights and actionable takeaways
3. Use subheadings where appropriate for readability
4. Incorporate data and statistics naturally
5. Avoid generic statements - be specific and substantive
6. Target approximately {word_count} words
7. Do not include the section title in your response - start directly with the content

Write compelling, professional content:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=word_count * 2,  # Allow some buffer
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

    async def generate_full_document(
        self,
        outline: Dict[str, Any],
        research: Dict[str, Any],
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """
        Generate the full document content.

        Args:
            outline: Document outline.
            research: Research results.
            tone: Writing tone.

        Returns:
            Full document content structure.
        """
        document = {
            "title": outline.get("title", ""),
            "subtitle": outline.get("subtitle", ""),
            "sections": [],
            "metadata": outline.get("metadata", {}),
        }

        topic = outline.get("title", "")

        # Generate executive summary
        exec_summary = outline.get("executive_summary", {})
        if exec_summary:
            summary_content = await self.generate_section(
                section_title="Executive Summary",
                context={
                    "topic": topic,
                    "research": research,
                    "outline": outline,
                    "key_points": exec_summary.get("key_points", []),
                },
                tone=tone,
                word_count=exec_summary.get("target_word_count", 300),
            )
            document["executive_summary"] = summary_content

        # Generate each main section
        for section in outline.get("sections", []):
            section_content = {
                "id": section.get("id", ""),
                "title": section.get("title", ""),
                "content": "",
                "subsections": [],
            }

            # If section has subsections, generate each
            if section.get("subsections"):
                for subsection in section["subsections"]:
                    sub_content = await self.generate_section(
                        section_title=subsection.get("title", ""),
                        context={
                            "topic": topic,
                            "research": research,
                            "outline": outline,
                            "key_points": subsection.get("key_points", []),
                            "include_statistic": subsection.get("include_statistic", False),
                        },
                        tone=tone,
                        word_count=subsection.get("target_word_count", 400),
                    )
                    section_content["subsections"].append({
                        "id": subsection.get("id", ""),
                        "title": subsection.get("title", ""),
                        "content": sub_content,
                    })
            else:
                # Generate main section content directly
                section_content["content"] = await self.generate_section(
                    section_title=section.get("title", ""),
                    context={
                        "topic": topic,
                        "research": research,
                        "outline": outline,
                        "key_points": [],
                    },
                    tone=tone,
                    word_count=section.get("target_word_count", 500),
                )

            document["sections"].append(section_content)

        # Generate conclusion
        conclusion = outline.get("conclusion", {})
        if conclusion:
            conclusion_content = await self.generate_section(
                section_title="Conclusion",
                context={
                    "topic": topic,
                    "research": research,
                    "outline": outline,
                    "key_points": conclusion.get("key_takeaways", []),
                },
                tone=tone,
                word_count=conclusion.get("target_word_count", 300),
            )
            document["conclusion"] = {
                "content": conclusion_content,
                "call_to_action": conclusion.get("call_to_action", ""),
            }

        return document
