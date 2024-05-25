from typing import Annotated, Dict, Text
from fastapi import APIRouter, Depends
import logging

from src.applicants.schemas.arbeitsagentur.response import ApplicantSearchResponse
from src.applicants.schemas.arbeitsagentur.schemas import BewerberDetail
from src.applicants.schemas.arbeitsagentur.request import SearchParameters
from src.applicants.service.arbeitsagentur import ApplicantApi
from src.configs import DEFAULT_LOGGING_CONFIG

router = APIRouter()

logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@router.get("/applicants/arbeitsagentur/search", response_model=ApplicantSearchResponse)
def search_applicants(props: Annotated[Dict, Depends(SearchParameters)]):
    search_parameters = SearchParameters(**props.__dict__)
    api = ApplicantApi()
    api.init()
    search_result_dict: Dict = api.search_applicants(search_parameters)
    return search_result_dict


@router.get("/applicants/arbeitsagentur/get", response_model=BewerberDetail)
def get_applicant(applicant_id: Text):
    api = ApplicantApi()
    api.init()
    applicant = api.get_applicant(applicant_id)
    return applicant


