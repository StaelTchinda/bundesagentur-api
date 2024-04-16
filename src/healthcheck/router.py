from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/health/liveness", response_class=PlainTextResponse)
def liveness_probe():
    return "OK"


@router.get("/health/readiness", response_class=PlainTextResponse)
def readiness_probe():
    return "OK"
