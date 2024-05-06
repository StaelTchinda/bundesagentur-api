from re import T
from typing import Annotated, Callable, Dict, Optional, Text, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from tinydb import Query
from tinydb.queries import QueryInstance
import logging

from src.arbeitsagentur.models.db.nosql import SearchedApplicantsDb, DetailedApplicantsDb
from src.arbeitsagentur.models.response import ApplicantSearchResponse, TimePeriod, Lokation, BewerberDetail, DetailedApplicantSearchResponse
from src.arbeitsagentur.models.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability
from src.arbeitsagentur.models.request import SearchParameters
from src.arbeitsagentur.service import ApplicantApi
from src.configs import DEFAULT_LOGGING_CONFIG

import fastapi

router = APIRouter()

logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@router.get("/applicants/search", response_model=ApplicantSearchResponse)
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
        logger.info(f"Fetching resumes from page {page_idx + 1}: {search_result_dict}")
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
    return db.get(Query().refnr.test(lambda x: x in searched_applicants_refnrs))




@router.get("/applicants/local_search", response_class=JSONResponse)
def local_search(
    maxGraduationYear : int | None = None,
    minWorkExperienceYears : int | None = None,
    careerField : Text | None = None,
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    locationKeyword: Text | None = None,

    page: int = 1,
    size: int = 25,
):
    candidates = local_filter(maxGraduationYear, minWorkExperienceYears, careerField, workingTime, locationKeyword)

    logger.info(f"Found in total {len(candidates)} candidates")

    candidates = candidates[(page-1)*size:page*size+size]

    return candidates


def local_filter(
    maxGraduationYear : int | None = None,
    minWorkExperienceYears : int | None = None,
    careerField : Text | None = None,
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    locationKeyword: Text | None = None,
):
    db = SearchedApplicantsDb()

    query: Optional[QueryInstance] = None

    if maxGraduationYear is not None:
        _applicant = Query()
        _education = Query()
        subquery = _applicant.ausbildungen.exists()  \
                    & _applicant.ausbildungen.any(
                        (_education.jahr <= maxGraduationYear)
                    )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if minWorkExperienceYears is not None:
        _applicant = Query()
        experience_duration_check= lambda x: TimePeriod(x).get_years() >= minWorkExperienceYears

        subquery = _applicant.erfahrung.exists() \
                    & _applicant.erfahrung.gesamterfahrung.exists() \
                    & _applicant.erfahrung.gesamterfahrung.test(experience_duration_check)
        
        if query is None:
            query = subquery
        else:
            query &= subquery

    if careerField is not None:
        _applicant = Query()
        _experience = Query()
        subquery = _applicant.erfahrung.exists() \
                    & _applicant.erfahrung.berufsfeldErfahrung.exists() \
                    & _applicant.erfahrung.berufsfeldErfahrung.any(
                        (_experience.berufsfeld.search(careerField))
                    )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if workingTime is not None and workingTime != WorkingTime.UNDEFINED:
        _applicant = Query()
        subquery = _applicant.arbeitszeitModelle.any(workingTime.value)

        if query is None:
            query = subquery
        else:
            query &= subquery

    if locationKeyword is not None:
        _applicant = Query()
        subquery = _applicant.lokation.exists() \
                    & _applicant.lokation.test(lambda x: Lokation(**x).check_location(locationKeyword))

        if query is None:
            query = subquery
        else:
            query &= subquery


    logger.info(f"Query: {query}")

    if query is not None:
        candidates = db.get(query)
    else:
        candidates = db.get_all()

    return candidates




@router.get("/applicants/fetch_detailed_resumes", response_class=JSONResponse)
def fetch_applicant_details(applicant_ids: str):
    #for some reason the input won't display as a list in the doc gui, so we'll just have to go with comma separated list for now
    db = DetailedApplicantsDb()
    
    resumelist : List = []
    applicant_ids = applicant_ids.split(",")
    for applicant_id in applicant_ids:
        applicant_detail = BewerberDetail(**get_applicant(applicant_id=applicant_id))
        resumelist.append(applicant_detail)
        db.upsert(applicant_detail)

    response = {
        "count": len(resumelist),
        "applicants": resumelist
    }

    return response