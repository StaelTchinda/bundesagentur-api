from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import logging

from src.healthcheck.router import router as healthcheck_router
from src.arbeitsagentur.router import router as arbeitsagentur_router

logger = logging.getLogger(__name__)
logger.info("Bundesagentur für Arbeit - API is starting now...")

try:
    app = FastAPI(docs_url="/")
    logger.info("FastAPI app is initialized.")
    app.include_router(arbeitsagentur_router, tags=['Arbeitsagentur Bewerberbörse'])
    logger.info("Arbeitsagentur router is included in FastAPI app.")
    app.include_router(healthcheck_router, tags=['Health check'])
    logger.info("Health check router is included in FastAPI app.")
except Exception as e:
    logger.error(f"Error while initializing FastAPI app: {e}")