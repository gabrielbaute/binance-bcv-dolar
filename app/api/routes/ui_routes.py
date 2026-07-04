"""
Module defining UI-facing routes (index, robots.txt, sitemap.xml, static files).
"""
from datetime import date
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, Response
from app.config.app_version import __version__

TEMPLATES_DIR = Path("app/ui/templates")

router = APIRouter(tags=["UI"])


@router.get("/", summary="Serve main HTML page")
async def read_index(request: Request):
    """Serve the main index HTML file with dynamic base URL."""
    base_url = str(request.base_url).rstrip("/")
    template_path = TEMPLATES_DIR / "index.html"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.format(base_url=base_url, app_version=__version__)
    return Response(content=content, media_type="text/html")


@router.get("/robots.txt", summary="Serve robots.txt", include_in_schema=False)
async def robots(request: Request):
    """Serve robots.txt file with dynamic sitemap URL."""
    base_url = str(request.base_url).rstrip("/")
    template_path = TEMPLATES_DIR / "robots.txt"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.format(base_url=base_url)
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml", summary="Serve sitemap.xml", include_in_schema=False)
async def sitemap(request: Request):
    """Generate sitemap.xml dynamically with current domain."""
    base_url = str(request.base_url).rstrip("/")
    today = date.today().isoformat()
    template_path = TEMPLATES_DIR / "sitemap.xml"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.format(base_url=base_url, today=today)
    return Response(content=content, media_type="application/xml")