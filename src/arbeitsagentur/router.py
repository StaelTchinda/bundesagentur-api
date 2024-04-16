from typing import Text
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.arbeitsagentur.service import ApplicantApi

router = APIRouter()


@router.get("/applicants/search", response_class=JSONResponse)
def search_applicants():
    api = ApplicantApi()
    api.init()
    return api.search_applicants()


@router.get("/applicants/get", response_class=JSONResponse)
def get_applicant(applicant_id: Text):
    return "OK"
