import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from datetime import date
from pathlib import Path

from app.config import Config, setup_logging
from app.api.include_routers import include_routers
from app.scheduler.dolar_scheduler import DolarScheduler
from app.database.db_config import init_db

setup_logging(log_dir=str(Config.LOG_DIR))

# Definir lifespan
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Inicializar DB
    init_db(instance_dir=Config.INSTANCE_DIR)

    # Inicializar scheduler
    scheduler = DolarScheduler()
    scheduler.start()

    # yield mantiene la app viva hasta que se cierre
    yield

# Crear app con lifespan
app = FastAPI(title="P2P Exchange Rate API", lifespan=lifespan)

# Templates directory
TEMPLATES_DIR = Path("app/ui/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

# Register API routers
include_routers(app)


# Serve the main HTML file
@app.get("/", tags=["UI"])
async def read_index(request: Request):
    """Serve the main index HTML file with dynamic base URL."""
    base_url = str(request.base_url).rstrip("/")
    template_path = TEMPLATES_DIR / "index.html"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.format(base_url=base_url)
    return Response(content=content, media_type="text/html")


# Serve robots.txt
@app.get("/robots.txt", tags=["UI"])
async def robots(request: Request):
    """Serve robots.txt file with dynamic sitemap URL."""
    base_url = str(request.base_url).rstrip("/")
    template_path = TEMPLATES_DIR / "robots.txt"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.format(base_url=base_url)
    return Response(content=content, media_type="text/plain")


# Serve sitemap.xml
@app.get("/sitemap.xml", tags=["UI"])
async def sitemap(request: Request):
    """Generate sitemap.xml dynamically with current domain."""
    base_url = str(request.base_url).rstrip("/")
    today = date.today().isoformat()
    template_path = TEMPLATES_DIR / "sitemap.xml"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.format(base_url=base_url, today=today)
    return Response(content=content, media_type="application/xml")


# Init database
init_db(instance_dir=Config.INSTANCE_DIR)


# Init scheduler
@app.on_event("startup")
def startup_event():
    """Start the DolarScheduler on application startup."""
    scheduler = DolarScheduler()
    scheduler.start()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=Config.API_HOST, port=int(Config.API_PORT), reload=True)