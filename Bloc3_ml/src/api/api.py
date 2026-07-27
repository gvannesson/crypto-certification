"""API FastAPI pour la classification à la demande (ml-api, port 8002)."""

import sys
from pathlib import Path

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.settings import logger
from src.api.routes import classify, login

app = FastAPI(
    title="Bloc3 ML API - Classification de Tendance Crypto",
    description="API pour classifier la tendance crypto (UP/DOWN/STABLE) à la demande",
    version="1.0.0",
)

app.include_router(login.router, prefix="/api/v1")
app.include_router(classify.router, prefix="/api/v1")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
def root():
    return {"message": "Bloc3 ML API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("Démarrage du serveur ML API")
    uvicorn.run("src.api.api:app", host="0.0.0.0", port=8002, reload=False)
