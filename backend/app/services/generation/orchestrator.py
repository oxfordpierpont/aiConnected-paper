"""Generation orchestrator - main content generation flow."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document, GenerationJob
from app.services.generation.research_service import ResearchService
from app.services.generation.outline_service import OutlineService
from app.services.generation.content_service import ContentService
from app.services.generation.statistics_service import StatisticsService
from app.services.generation.chart_service import ChartService
from app.services.pdf_service import PDFService


class GenerationOrchestrator:
    """Orchestrates the content generation pipeline."""

    STEPS = [
        "topic_analysis",
        "keyword_research",
        "web_research",
        "industry_analysis",
        "outline_generation",
        "content_writing",
        "statistics_extraction",
        "chart_generation",
        "pdf_rendering",
    ]

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.research_service = ResearchService()
        self.outline_service = OutlineService()
        self.content_service = ContentService()
        self.statistics_service = StatisticsService()
        self.chart_service = ChartService()
        self.pdf_service = PDFService()

    async def generate(
        self,
        document: Document,
        job: GenerationJob,
        options: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Execute the full content generation pipeline.

        Steps:
        1. Topic Analysis
        2. Keyword Research
        3. Web Research
        4. Industry Analysis
        5. Outline Generation
        6. Content Writing
        7. Statistics Extraction
        8. Chart Generation
        9. PDF Rendering

        Args:
            document: The document to generate content for.
            job: The generation job for tracking progress.
            options: Optional generation options.

        Returns:
            The updated document with generated content.
        """
        options = options or {}
        topic = document.topic
        keywords = options.get("keywords", [])
        tone = options.get("tone", "professional")
        industry = options.get("industry", "general")

        try:
            # Step 1: Topic Analysis (5%)
            await self._update_job_progress(job, "topic_analysis", 5)
            # Topic is already provided, minimal analysis needed

            # Step 2: Keyword Research (10%)
            await self._update_job_progress(job, "keyword_research", 10)
            if not keywords:
                keywords = self._extract_keywords(topic)

            # Step 3: Web Research (25%)
            await self._update_job_progress(job, "web_research", 25)
            research = await self.research_service.research_topic(
                topic=topic,
                keywords=keywords,
                depth=options.get("research_depth", "standard"),
            )

            # Step 4: Industry Analysis (35%)
            await self._update_job_progress(job, "industry_analysis", 35)
            industry_analysis = await self.research_service.analyze_industry(
                industry=industry,
                topic=topic,
            )
            research["industry_analysis"] = industry_analysis

            # Step 5: Outline Generation (45%)
            await self._update_job_progress(job, "outline_generation", 45)
            template_config = options.get("template_config", {})
            outline = await self.outline_service.generate_outline(
                topic=topic,
                research=research,
                template_config=template_config,
            )

            # Step 6: Content Writing (70%)
            await self._update_job_progress(job, "content_writing", 70)
            content = await self.content_service.generate_full_document(
                outline=outline,
                research=research,
                tone=tone,
            )

            # Step 7: Statistics Extraction (80%)
            await self._update_job_progress(job, "statistics_extraction", 80)
            # Compile all content text for statistics extraction
            all_content = self._compile_content_text(content)
            statistics = await self.statistics_service.extract_statistics(
                content=all_content,
                research=research,
            )
            content["statistics"] = statistics

            # Step 8: Chart Generation (90%)
            await self._update_job_progress(job, "chart_generation", 90)
            chart_suggestions = await self.chart_service.suggest_visualizations(statistics)
            charts = []
            for suggestion in chart_suggestions[:3]:  # Limit to 3 charts
                if suggestion["type"] not in ["callout"]:  # Skip non-chart types
                    chart_data = suggestion.get("data", {})
                    if "labels" in chart_data and "values" in chart_data:
                        chart_bytes = await self.chart_service.generate_chart(
                            chart_type=suggestion["type"],
                            data=chart_data,
                            style={"title": suggestion.get("title", "")},
                        )
                        charts.append({
                            "type": suggestion["type"],
                            "title": suggestion.get("title", ""),
                            "data": chart_bytes,  # PNG bytes
                        })
            content["charts"] = charts

            # Step 9: PDF Rendering (100%)
            await self._update_job_progress(job, "pdf_rendering", 95)
            pdf_bytes = await self.pdf_service.generate_pdf(
                content=content,
                template_id=document.template_id,
                branding=options.get("branding", {}),
            )

            # Update document with generated content
            document.content = content
            document.pdf_path = await self._save_pdf(document.id, pdf_bytes)
            document.status = "completed"
            document.word_count = self._count_words(all_content)
            document.page_count = len(pdf_bytes) // 50000 + 1  # Rough estimate
            document.updated_at = datetime.utcnow()

            # Mark job as complete
            await self._update_job_progress(job, "completed", 100)
            job.status = "completed"
            job.completed_at = datetime.utcnow()

            if self.db:
                await self.db.commit()

            return document

        except Exception as e:
            await self._handle_failure(job, e)
            raise

    def _extract_keywords(self, topic: str) -> list:
        """Extract basic keywords from topic."""
        # Simple keyword extraction - split on common delimiters
        words = topic.lower().replace(",", " ").replace(":", " ").split()
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        return [w for w in words if w not in stop_words and len(w) > 2][:10]

    def _compile_content_text(self, content: Dict[str, Any]) -> str:
        """Compile all content into a single text string."""
        parts = []

        if content.get("executive_summary"):
            parts.append(content["executive_summary"])

        for section in content.get("sections", []):
            if section.get("content"):
                parts.append(section["content"])
            for subsection in section.get("subsections", []):
                if subsection.get("content"):
                    parts.append(subsection["content"])

        if content.get("conclusion", {}).get("content"):
            parts.append(content["conclusion"]["content"])

        return "\n\n".join(parts)

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    async def _save_pdf(self, document_id: str, pdf_bytes: bytes) -> str:
        """Save PDF to storage and return path."""
        from app.config import settings
        import os

        storage_path = settings.STORAGE_LOCAL_PATH
        documents_dir = os.path.join(storage_path, "documents")
        os.makedirs(documents_dir, exist_ok=True)

        filename = f"{document_id}.pdf"
        filepath = os.path.join(documents_dir, filename)

        with open(filepath, "wb") as f:
            f.write(pdf_bytes)

        return filepath

    async def _update_job_progress(
        self,
        job: GenerationJob,
        step: str,
        progress: int,
    ) -> None:
        """Update job progress."""
        job.current_step = step
        job.progress_percent = progress
        job.updated_at = datetime.utcnow()

        if self.db:
            await self.db.commit()

    async def _handle_failure(
        self,
        job: GenerationJob,
        error: Exception,
    ) -> None:
        """Handle generation failure."""
        job.status = "failed"
        job.error_message = str(error)
        job.completed_at = datetime.utcnow()

        if self.db:
            await self.db.commit()
