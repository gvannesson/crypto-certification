import sys
from pathlib import Path

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.settings import logger  # noqa: E402
from src.C5_api.routes import login, ohlcv, trading_pairs, predictions, currencies, exchanges  # noqa: E402

app = FastAPI(
    title="Bloc1 Data API - Classification de Tendance Crypto",
    description="API REST pour la couche données du projet de classification de tendance crypto",
    version="1.0.0",
)

app.include_router(login.router, prefix="/api/v1")
app.include_router(trading_pairs.router, prefix="/api/v1")
app.include_router(ohlcv.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(currencies.router, prefix="/api/v1")
app.include_router(exchanges.router, prefix="/api/v1")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
def root():
    return {"message": "Bloc1 Data API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("Démarrage du serveur API")
    uvicorn.run(
        "src.C5_api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
