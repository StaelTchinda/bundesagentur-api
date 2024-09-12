from typing import Dict, List, Text
from fastapi import APIRouter
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
def search_applicants(
    searchKeyword: Text | None = None,
    educationType: EducationType = EducationType.UNDEFINED,
    locationKeyword: Text | None = None,
    locationRadius: LocationRadius = LocationRadius.ZERO,
    offerType: OfferType = OfferType.WORKER,
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    workExperience: WorkExperience = WorkExperience.WITH_EXPERIENCE,
    contractType: ContractType = ContractType.UNDEFINED,
    disability: Disability = Disability.UNDEFINED,
    page: int = 1,
    size: int = 25,
    # Further filter options
    locations: List[Text] = [],
):
    search_parameters = SearchParameters(
        searchKeyword=searchKeyword,
        educationType=educationType,
        locationKeyword=locationKeyword,
        locationRadius=locationRadius,
        offerType=offerType,
        workingTime=workingTime,
        workExperience=workExperience,
        contractType=contractType,
        disability=disability,
        page=page,
        size=size,
        # Further filter options
        locations=locations
    )
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
