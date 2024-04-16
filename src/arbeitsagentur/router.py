from typing import Optional, Text
from enum import Enum
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.arbeitsagentur.models.response import ApplicantSearchResponse
from src.arbeitsagentur.models.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability
from src.arbeitsagentur.models.request import SearchParameters
from src.arbeitsagentur.service import ApplicantApi

router = APIRouter()


@router.get("/applicants/search", response_model=ApplicantSearchResponse)
def search_applicants(
    searchKeyword: Text = None,
    educationType: EducationType = None,
    locationKeyword: Text = None,
    locationRadius: LocationRadius = None,
    offerType: OfferType = None,
    workingTime: WorkingTime = None,
    workExperience: WorkExperience = None,
    contractType: ContractType = None,
    disability: Disability = None,
    page: int = 1,
    size: int = 10,

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
    )
    api = ApplicantApi()
    api.init()
    return api.search_applicants(search_parameters)


@router.get("/applicants/get", response_class=JSONResponse)
def get_applicant(applicant_id: Text):
    api = ApplicantApi()
    api.init()
    return api.get_applicant(applicant_id)
