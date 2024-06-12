from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import logging
import requests_cache

from src.healthcheck.router import router as healthcheck_router
from src.applicants.router.arbeitsagentur import router as arbeitsagentur_applicants_router
from src.applicants.router.extended import router as extended_applicants_router

logger = logging.getLogger(__name__)
logger.info("Bundesagentur für Arbeit - API is starting now...")

try:
    requests_cache.install_cache('cache/api', expire_after=60*60*24)
    app = FastAPI(docs_url="/")
    logger.info("FastAPI app is initialized.")
    app.include_router(extended_applicants_router, tags=['Extended applicants search'])
    logger.info("Extended applicants search router is included in FastAPI app.")
    app.include_router(arbeitsagentur_applicants_router, tags=['Arbeitsagentur Bewerberbörse'])
    logger.info("Arbeitsagentur router is included in FastAPI app.")
    app.include_router(healthcheck_router, tags=['Health check'])
    logger.info("Health check router is included in FastAPI app.")
except Exception as e:
    logger.error(f"Error while initializing FastAPI app: {e}")