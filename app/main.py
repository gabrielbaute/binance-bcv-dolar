"""
Main application entry point configuring lifespan handlers, schedules and logging structures.
"""
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import DolarVzlaLogger, config
from app.database import db_manager
from app.api import create_app, register_error_handlers
from app.scheduler.dolar_scheduler import DolarScheduler

DolarVzlaLogger.setup_logging(logs_dir=config.LOGS_DIR, level=config.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous lifecycle manager handling initial database synchronization and background tasks.
    
    Args:
        app (FastAPI): Active application instance context.
    """
    await db_manager.init_db()
    
    session = db_manager.async_session_maker()
    try:
        scheduler = DolarScheduler(databasesession=session, config=config)
        scheduler.start()
        
        yield
        
    finally:
        await session.aclose()

app = create_app(config=config)

app.router.lifespan_context = lifespan

register_error_handlers(app=app)
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host=config.API_HOST, 
        port=int(config.API_PORT), 
        reload=False
    )