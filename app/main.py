import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# Mount static files
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

# Register API routers
include_routers(app)

# Serve the main HTML file
@app.get("/")
async def read_index():
    return FileResponse('app/ui/index.html')

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=Config.API_HOST, port=int(Config.API_PORT), reload=True)