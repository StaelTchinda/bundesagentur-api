from typing import Dict, Optional, Text
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tinydb import Query

from src.arbeitsagentur.models.db.nosql import SearchedApplicantsDb
from src.arbeitsagentur.models.response import ApplicantSearchResponse
from src.arbeitsagentur.models.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability
from src.arbeitsagentur.models.request import SearchParameters
from src.arbeitsagentur.service import ApplicantApi

router = APIRouter()


@router.get("/applicants/search", response_model=ApplicantSearchResponse)
def search_applicants(
    searchKeyword: Text | None = None,
    educationType: EducationType = EducationType.undefined,
    locationKeyword: Text | None = None,
    locationRadius: LocationRadius = LocationRadius.zero,
    offerType: OfferType = OfferType.ar,
    workingTime: WorkingTime = WorkingTime.undefined,
    workExperience: WorkExperience = WorkExperience.mb,
    contractType: ContractType = ContractType.undefined,
    disability: Disability = Disability.undefined,
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
    search_result_dict: Dict = api.search_applicants(search_parameters)
    search_result: ApplicantSearchResponse = ApplicantSearchResponse(**search_result_dict)
    return search_result


@router.get("/applicants/get", response_class=JSONResponse)
def get_applicant(applicant_id: Text):
    api = ApplicantApi()
    api.init()
    return api.get_applicant(applicant_id)


@router.get("/applicants/fetch_resumes", response_class=JSONResponse)
def fetch_applicant_resumes(
    searchKeyword: Optional[Text] = None,
    educationType: Optional[EducationType] = None,
    locationKeyword: Optional[Text] = None,
    locationRadius: Optional[LocationRadius] = None,
    offerType: Optional[OfferType] = None,
    workingTime: Optional[WorkingTime] = None,
    workExperience: Optional[WorkExperience] = None,
    contractType: Optional[ContractType] = None,
    disability: Optional[Disability] = None,
    pages_count: int = 10,
    size: int = 10,
):
    api = ApplicantApi()
    api.init()
    db = SearchedApplicantsDb()
    searched_applicants_refnrs = []
    for page_idx in range(pages_count):
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
            page=page_idx + 1,
            size=size,
        )
        searched_applicants = api.search_applicants(search_parameters)
        for applicant in searched_applicants.bewerber:
            db.insert(applicant)
            searched_applicants_refnrs.append(applicant.refnr)
    return db.get(Query().refnr.test(lambda x: x in searched_applicants_refnrs))