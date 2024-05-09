from typing import Annotated, Dict, List, Optional, Text
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from applicants.schemas.extended.request import ExtendedSearchParameters
from src.applicants.schemas.extended.response import FetchApplicantsResponse, SearchApplicantsResponse
from src.applicants.service.extended.db import DetailedApplicantsDb, SearchedApplicantsDb
from src.applicants.schemas.arbeitsagentur.request import SearchParameters
from src.applicants.schemas.extended.request import FetchApplicantsRequest
from applicants.service.extended.query import build_search_query
from src.applicants.schemas.arbeitsagentur.response import ApplicantSearchResponse
from src.applicants.schemas.arbeitsagentur.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability
from src.applicants.schemas.arbeitsagentur.schemas import BewerberDetail, BewerberUebersicht
from src.applicants.schemas.extended.response import FetchDetailedApplicantsResponse
from src.applicants.service.arbeitsagentur import ApplicantApi
from src.configs import DEFAULT_LOGGING_CONFIG


arbeitsagentur_router = APIRouter()


router = APIRouter()

logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@router.get("/applicants/fetch", response_model=FetchApplicantsResponse)
def fetch_applicants(
    searchKeyword: Text | None = None,
    educationType: EducationType = EducationType.UNDEFINED,
    locationKeyword: Text | None = None,
    locationRadius: LocationRadius = LocationRadius.ZERO,
    offerType: OfferType = OfferType.WORKER,
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    workExperience: WorkExperience = WorkExperience.WITH_EXPERIENCE,
    contractType: ContractType = ContractType.UNDEFINED,
    disability: Disability = Disability.UNDEFINED,
    pages_count: int = 1,
    pages_start: Optional[int] = None,
    size: int = 25,
):
    api = ApplicantApi()
    api.init()
    db = SearchedApplicantsDb()
    searched_applicants_refnrs = []
    start = pages_start or 0
    for page_idx in range(start, pages_count):
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
        search_result_dict: Dict = api.search_applicants(search_parameters)
        logger.info(f"Fetching resumes from page {page_idx + 1} with keys: {search_result_dict.keys()}")
        if "messages" in search_result_dict:
            logger.warning(f"Error while fetching resumes: {search_result_dict['messages']}")
            raise HTTPException(status_code=400, detail=search_result_dict["messages"])
        elif "bewerber" not in search_result_dict:
            logger.warning(f"No applicants found on page {page_idx + 1}")
            break
        search_result: ApplicantSearchResponse = ApplicantSearchResponse(**search_result_dict)
        for applicant in search_result.bewerber:
            db.upsert(applicant)
            searched_applicants_refnrs.append(applicant.refnr)
    
    applicants: List[BewerberUebersicht] = db.get_by_refnrs(searched_applicants_refnrs)
    response = {
        "count": len(applicants),
        "applicantRefnrs": [applicant.refnr for applicant in applicants]
    }

    return response


@router.get("/applicants/search", response_model=SearchApplicantsResponse)
def search_applicants(
    keywords: List[Text] = Query([]),
    maxGraduationYear : int | None = None,
    minWorkExperienceYears : int | None = None,
    careerField : Text | None = None,
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    locationKeyword: Text | None = None,

    page: int = 1,
    size: int = 25,
):
    search_parameters = ExtendedSearchParameters(
        keywords=keywords,
        max_graduation_year=maxGraduationYear,
        min_work_experience_years=minWorkExperienceYears,
        career_field=careerField,
        working_time=workingTime,
        location_keyword=locationKeyword
    )

    query = build_search_query(search_parameters)
    logger.info(f"Query: {query}")

    db = SearchedApplicantsDb()

    if query is not None:
        applicants = db.get(query)
    else:
        applicants = db.get_all()

    total_count: int = len(applicants)
    logger.info(f"Found in total {total_count} applicants")

    applicants = applicants[(page-1)*size:(page-1)*size+size]

    response = {
        "maxCount": total_count,
        "count": len(applicants),
        "applicantRefnrs": [candidate.refnr for candidate in applicants],
        "applicantLinks": [f"https://www.arbeitsagentur.de/bewerberboerse/bewerberdetail/{candidate.refnr}" for candidate in applicants],
        "applicants": applicants
    }

    return response


@router.post("/applicants/fetch/details", response_model=FetchDetailedApplicantsResponse)
def fetch_applicant_details(request: FetchApplicantsRequest):
    applicant_ids: List[Text] = request.applicantIds

    db = DetailedApplicantsDb()
    api = ApplicantApi()
    api.init()
    
    all_applicants_details: List[BewerberDetail] = []
    for applicant_id in applicant_ids:
        applicant_details_dict: Dict = api.get_applicant(applicant_id)
        applicant_detail: BewerberDetail = BewerberDetail(**applicant_details_dict)
        all_applicants_details.append(applicant_detail)
        db.upsert(applicant_detail)

    response = {
        "count": len(all_applicants_details),
        "applicantRefnrs": [applicant.refnr for applicant in all_applicants_details]
    }

    return response


@router.get("/applicants/search/details", response_class=JSONResponse)
def search_applicant_details():
    pass