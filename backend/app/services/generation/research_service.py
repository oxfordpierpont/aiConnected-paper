"""Research service for web research and analysis."""

import json
from typing import List, Dict, Any

import anthropic

from app.config import settings


class ResearchService:
    """Service for conducting web research on topics."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    async def research_topic(
        self,
        topic: str,
        keywords: List[str],
        depth: str = "standard",
    ) -> Dict[str, Any]:
        """
        Research a topic using AI-powered web analysis.

        Args:
            topic: The main topic to research.
            keywords: Related keywords to explore.
            depth: Research depth ('shallow', 'standard', 'deep').

        Returns:
            Research results including sources, key findings, statistics.
        """
        depth_tokens = {"shallow": 1000, "standard": 2000, "deep": 4000}
        max_tokens = depth_tokens.get(depth, 2000)

        prompt = f"""You are a research analyst creating thought leadership content. Research the following topic comprehensively.

Topic: {topic}
Keywords to incorporate: {', '.join(keywords) if keywords else 'None specified'}

Provide research findings in the following JSON structure:
{{
    "key_findings": [
        {{"finding": "...", "importance": "high|medium|low", "source_type": "industry_report|study|expert_opinion"}}
    ],
    "statistics": [
        {{"value": "...", "context": "...", "source": "...", "year": "..."}}
    ],
    "trends": [
        {{"trend": "...", "direction": "growing|stable|declining", "impact": "..."}}
    ],
    "challenges": [
        {{"challenge": "...", "affected_stakeholders": ["..."], "potential_solutions": ["..."]}}
    ],
    "opportunities": [
        {{"opportunity": "...", "potential_impact": "...", "timeline": "short|medium|long"}}
    ],
    "expert_perspectives": [
        {{"perspective": "...", "source_type": "..."}}
    ],
    "recommended_sources": [
        {{"type": "...", "description": "...", "relevance": "..."}}
    ]
}}

Provide substantive, specific research findings that would be valuable for executive-level thought leadership content. Generate realistic but clearly marked as AI-generated statistics and insights."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Parse JSON from response
        try:
            # Try to extract JSON from the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass

        # Return structured default if parsing fails
        return {
            "key_findings": [{"finding": response_text[:500], "importance": "high", "source_type": "ai_analysis"}],
            "statistics": [],
            "trends": [],
            "challenges": [],
            "opportunities": [],
            "expert_perspectives": [],
            "recommended_sources": [],
            "raw_response": response_text,
        }

    async def analyze_industry(
        self,
        industry: str,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Analyze industry context for a topic.

        Args:
            industry: The industry to analyze.
            topic: The topic being researched.

        Returns:
            Industry analysis including trends, challenges, opportunities.
        """
        prompt = f"""You are an industry analyst. Provide a comprehensive analysis of the {industry} industry as it relates to the topic: "{topic}".

Provide your analysis in the following JSON structure:
{{
    "industry_overview": {{
        "name": "{industry}",
        "market_size": "...",
        "growth_rate": "...",
        "key_players": ["..."]
    }},
    "current_trends": [
        {{"trend": "...", "impact": "...", "adoption_rate": "..."}}
    ],
    "challenges": [
        {{"challenge": "...", "severity": "high|medium|low", "affected_areas": ["..."]}}
    ],
    "opportunities": [
        {{"opportunity": "...", "potential": "high|medium|low", "barriers": ["..."]}}
    ],
    "regulatory_landscape": {{
        "key_regulations": ["..."],
        "upcoming_changes": ["..."],
        "compliance_considerations": ["..."]
    }},
    "competitive_dynamics": {{
        "market_structure": "...",
        "competitive_intensity": "high|medium|low",
        "differentiation_factors": ["..."]
    }},
    "future_outlook": {{
        "short_term": "...",
        "medium_term": "...",
        "long_term": "...",
        "key_uncertainties": ["..."]
    }}
}}

Provide realistic industry insights suitable for executive-level content."""

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
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass

        return {
            "industry_overview": {"name": industry},
            "current_trends": [],
            "challenges": [],
            "opportunities": [],
            "regulatory_landscape": {},
            "competitive_dynamics": {},
            "future_outlook": {},
            "raw_response": response_text,
        }
