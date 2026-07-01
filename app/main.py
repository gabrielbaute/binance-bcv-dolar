import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import create_app
from app.database import db_manager
from app.config import DolarVzlaLogger, config
from app.scheduler.dolar_scheduler import DolarScheduler

DolarVzlaLogger.setup_logging(logs_dir=config.LOGS_DIR, level=config.LOG_LEVEL)

async def lifespan(app: FastAPI):
    await db_manager.init_db()
    session = db_manager.async_session_maker()
    try:
        scheduler = DolarScheduler(databasesession=session, config=config)
        scheduler.start()
        yield
    finally:
        await session.close()

app = create_app(config=config)
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=config.API_HOST, port=int(config.API_PORT), reload=False)