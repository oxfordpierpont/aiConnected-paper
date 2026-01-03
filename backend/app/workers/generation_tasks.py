"""Content generation Celery tasks."""

import asyncio
from typing import Optional

from celery import shared_task

from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.services.generation_service import GenerationService
from app.services.document_service import DocumentService
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService
from app.config import settings


def run_async(coro):
    """Run an async function in a sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="generate_content_task", max_retries=3)
def generate_content_task(self, job_id: str):
    """
    Generate content for a document.

    Args:
        job_id: The generation job ID.
    """
    return run_async(_generate_content_async(self, job_id))


async def _generate_content_async(task, job_id: str):
    """Async implementation of content generation."""
    async with AsyncSessionLocal() as db:
        # Get job
        from sqlalchemy import select
        from app.models import GenerationJob, Document, Client

        result = await db.execute(
            select(GenerationJob).where(GenerationJob.id == job_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            return {"error": "Job not found"}

        # Get document
        result = await db.execute(
            select(Document).where(Document.id == job.document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            await GenerationService.fail_job(db, job, "Document not found")
            return {"error": "Document not found"}

        # Get client
        result = await db.execute(
            select(Client).where(Client.id == document.client_id)
        )
        client = result.scalar_one_or_none()

        try:
            # Start job
            job = await GenerationService.start_job(db, job)

            # Step 1: Topic Analysis (5%)
            job = await GenerationService.update_progress(
                db, job, "researching", "topic_analysis", 10,
                {"topic_analysis": {"status": "completed", "topic": document.topic}}
            )

            # Step 2: Keyword Research (15%)
            keywords = await _generate_keywords(document.topic, client)
            job = await GenerationService.update_progress(
                db, job, "researching", "keyword_research", 20,
                {**job.steps, "keyword_research": {"status": "completed", "keywords": keywords}}
            )

            # Step 3: Web Research (30%)
            research_data = await _perform_research(document.topic, keywords)
            job = await GenerationService.update_progress(
                db, job, "researching", "web_research", 35,
                {**job.steps, "web_research": {"status": "completed"}}
            )

            # Step 4: Outline Generation (40%)
            outline = await _generate_outline(document.topic, research_data, client)
            job = await GenerationService.update_progress(
                db, job, "writing", "outline_generation", 45,
                {**job.steps, "outline_generation": {"status": "completed"}}
            )

            # Step 5: Content Writing (70%)
            content = await _generate_content(outline, research_data, client)
            job = await GenerationService.update_progress(
                db, job, "writing", "content_writing", 75,
                {**job.steps, "content_writing": {"status": "completed"}}
            )

            # Step 6: Statistics & Charts (85%)
            statistics = await _extract_statistics(content, research_data)
            job = await GenerationService.update_progress(
                db, job, "rendering", "statistics_extraction", 85,
                {**job.steps, "statistics": {"status": "completed", "count": len(statistics)}}
            )

            # Step 7: PDF Rendering (95%)
            pdf_bytes = await _render_pdf(document, content, statistics, client)
            storage_service = StorageService()
            pdf_path = await storage_service.save_file(
                pdf_bytes,
                folder=f"documents/{document.agency_id}",
                filename=f"{document.slug}.pdf",
            )

            # Update document
            document.content_json = {
                "outline": outline,
                "sections": content,
                "statistics": statistics,
                "sources": research_data.get("sources", []),
            }
            document.pdf_url = pdf_path
            document.status = "ready"
            document.word_count = sum(len(s.get("content", "").split()) for s in content)
            document.statistics_count = len(statistics)
            document.sources_count = len(research_data.get("sources", []))
            await db.commit()

            # Complete job
            job = await GenerationService.complete_job(db, job)

            return {"status": "completed", "document_id": document.id}

        except Exception as e:
            await GenerationService.fail_job(db, job, str(e))
            document.status = "failed"
            await db.commit()
            raise


async def _generate_keywords(topic: str, client) -> list:
    """Generate keywords for the topic."""
    # In production, this would use Claude API
    # For now, return mock keywords
    base_keywords = topic.lower().split()[:5]
    if client and client.keywords:
        base_keywords.extend(client.keywords[:3])
    return list(set(base_keywords))


async def _perform_research(topic: str, keywords: list) -> dict:
    """Perform web research on the topic."""
    # In production, this would perform actual web searches
    return {
        "sources": [
            {"title": f"Research on {topic}", "url": "https://example.com/1", "relevance": 0.95},
            {"title": f"Industry trends: {topic}", "url": "https://example.com/2", "relevance": 0.87},
        ],
        "key_findings": [
            f"Key insight about {topic}",
            "Industry growth statistics",
            "Expert recommendations",
        ],
    }


async def _generate_outline(topic: str, research_data: dict, client) -> list:
    """Generate document outline."""
    return [
        {"title": "Executive Summary", "type": "introduction"},
        {"title": f"Understanding {topic}", "type": "section"},
        {"title": "Key Industry Trends", "type": "section"},
        {"title": "Strategic Recommendations", "type": "section"},
        {"title": "Conclusion", "type": "conclusion"},
    ]


async def _generate_content(outline: list, research_data: dict, client) -> list:
    """Generate content for each section."""
    sections = []
    for item in outline:
        sections.append({
            "title": item["title"],
            "type": item["type"],
            "content": f"Content for {item['title']}. This section provides valuable insights and analysis. "
                      f"Our research indicates significant opportunities in this area. "
                      f"Key stakeholders should consider the implications discussed here.",
        })
    return sections


async def _extract_statistics(content: list, research_data: dict) -> list:
    """Extract or generate statistics."""
    return [
        {"value": "73%", "label": "of executives prioritize this area", "source": "Industry Report 2024"},
        {"value": "2.5x", "label": "average ROI improvement", "source": "Case Study Analysis"},
        {"value": "$4.2B", "label": "projected market size by 2025", "source": "Market Research"},
    ]


async def _render_pdf(document, content: list, statistics: list, client) -> bytes:
    """Render the document as PDF."""
    pdf_service = PDFService()

    context = {
        "document": document,
        "content": content,
        "statistics": statistics,
        "client": client,
        "branding": {
            "primary_color": "#1a4a6e",
            "secondary_color": "#b8860b",
        },
    }

    try:
        return pdf_service.generate_pdf_bytes(
            template_name="professional/document.html",
            context=context,
        )
    except Exception:
        # Fallback to simple HTML if template not found
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #1a4a6e; }}
                h2 {{ color: #2980b9; border-bottom: 2px solid #b8860b; }}
                .stat {{ background: #f5f5f5; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>{document.title}</h1>
            {"".join(f"<h2>{s['title']}</h2><p>{s['content']}</p>" for s in content)}
            <h2>Key Statistics</h2>
            {"".join(f"<div class='stat'><strong>{s['value']}</strong> - {s['label']}</div>" for s in statistics)}
        </body>
        </html>
        """
        from weasyprint import HTML
        return HTML(string=html).write_pdf()


@celery_app.task(bind=True, name="render_pdf_task")
def render_pdf_task(self, document_id: str):
    """
    Re-render PDF for a document.

    Args:
        document_id: The document ID.
    """
    return run_async(_render_pdf_async(document_id))


async def _render_pdf_async(document_id: str):
    """Async implementation of PDF rendering."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from app.models import Document, Client

        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document or not document.content_json:
            return {"error": "Document not found or no content"}

        result = await db.execute(
            select(Client).where(Client.id == document.client_id)
        )
        client = result.scalar_one_or_none()

        content = document.content_json.get("sections", [])
        statistics = document.content_json.get("statistics", [])

        pdf_bytes = await _render_pdf(document, content, statistics, client)

        storage_service = StorageService()
        pdf_path = await storage_service.save_file(
            pdf_bytes,
            folder=f"documents/{document.agency_id}",
            filename=f"{document.slug}.pdf",
        )

        document.pdf_url = pdf_path
        await db.commit()

        return {"status": "completed", "pdf_url": pdf_path}


@celery_app.task(bind=True, name="generate_cover_image")
def generate_cover_image(self, document_id: str, query: str = None):
    """
    Generate or fetch cover image for a document.

    Args:
        document_id: The document ID.
        query: Optional search query for image.
    """
    # TODO: Implement with Freepik API integration
    pass
