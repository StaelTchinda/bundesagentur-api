from re import T
from typing import Callable, Dict, Optional, Text
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tinydb import Query
from tinydb.queries import QueryInstance
import logging

from src.arbeitsagentur.models.db.nosql import SearchedApplicantsDb
from src.arbeitsagentur.models.response import ApplicantSearchResponse, TimePeriod
from src.arbeitsagentur.models.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability
from src.arbeitsagentur.models.request import SearchParameters
from src.arbeitsagentur.service import ApplicantApi
from src.configs import DEFAULT_LOGGING_CONFIG

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
        search_result: ApplicantSearchResponse = ApplicantSearchResponse(**search_result_dict)
        for applicant in search_result.bewerber:
            db.upsert(applicant)
            searched_applicants_refnrs.append(applicant.refnr)
    return db.get(Query().refnr.test(lambda x: x in searched_applicants_refnrs))



@router.get("/applicants/local_search", response_class=JSONResponse)
def search_applicant_resumes(
    minGraduationYear : int | None = None,
    minWorkExperienceYears : int | None = None,
    workExperienceJobs : Text | None = None,
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    locationKeyword: Text | None = None,

    page: int = 1,
    size: int = 25,
):
    db = SearchedApplicantsDb()

    query: Optional[QueryInstance] = None

    # for candidate in _candidates:
    #     if("ausbildungen" in candidate.keys()):
    #         for education in candidate["ausbildungen"]:
    #             accepted_educations = ["Mittlere Reife / Mittlerer Bildungsabschluss", "Hauptschulabschluss"]
    #             print(education["art"])
    #             if(education["art"] in accepted_educations and int(education["jahr"]) == graduationYear):
    #                 match = True
    #                 break

    #     if(not match):
    #         _candidates.remove(candidate)
    #         continue

    if minGraduationYear is not None:
        _applicant = Query()
        _education = Query()
        accepted_educations = ["Mittlere Reife / Mittlerer Bildungsabschluss", "Hauptschulabschluss"]
        subquery = _applicant.ausbildungen.exists() \
                    & _applicant.ausbildungen.any(
                        # _education.art.one_of(accepted_educations) \
                        (_education.jahr >= minGraduationYear)
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


    print(f"Query: {query}")

    if query is not None:
        candidates = db.get(query)
    else:
        candidates = db.get_all()

    candidates = candidates[page*size:page*size+size]

    return candidates