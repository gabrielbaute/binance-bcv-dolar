import uvicorn
from fastapi import FastAPI

from app.config import Config
from app.api.include_routers import include_routers
from app.scheduler.dolar_scheduler import DolarScheduler
from app.database.db_config import init_db

app = FastAPI(title="P2P Exchange Rate API")

# Registrar rutas
include_routers(app)

# Inicializar DB
init_db()

# Iniciar scheduler en el evento startup
@app.on_event("startup")
def startup_event():
    scheduler = DolarScheduler()
    scheduler.start()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=Config.API_HOST, port=Config.API_PORT, reload=True)
