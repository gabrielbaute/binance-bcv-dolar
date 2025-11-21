import uvicorn
from fastapi import FastAPI

from app.config import Config, setup_logging
from app.api.include_routers import include_routers
from app.scheduler.dolar_scheduler import DolarScheduler
from app.database.db_config import init_db

setup_logging(log_dir=Config.LOG_DIR)

app = FastAPI(title="P2P Exchange Rate API")

# Register routers
include_routers(app)

# Init database
init_db(instance_dir=Config.INSTANCE_DIR)

# Init scheduler 
@app.on_event("startup")
def startup_event():
    scheduler = DolarScheduler()
    scheduler.start()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=Config.API_HOST, port=Config.API_PORT, reload=True)
