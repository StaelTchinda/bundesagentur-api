from typing import Annotated, Dict, List, Optional, Text
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from src.applicants.service.knowledge_base import (
    CompetencesDb,
    JobsDb,
    LanguagesDb,
    LicensesDb,
    LocationDb,
    SkillsDb,
    WorkfieldsDb,
)
from src.applicants.schemas.extended.request import (
    ExtendedDetailedSearchParameters,
    ExtendedSearchParameters,
    FetchParameters,
)
from src.applicants.schemas.extended.response import (
    FetchApplicantsResponse,
    SearchApplicantsResponse,
    SearchCriteriaSuggestion,
)
from src.applicants.service.extended.db import (
    DetailedApplicantsDb,
    SearchedApplicantsDb,
)
from src.applicants.schemas.arbeitsagentur.request import SearchParameters
from src.applicants.schemas.extended.request import FetchApplicantsDetailsRequest
from src.applicants.service.extended.query import (
    build_knowledge_search_query,
    build_search_query,
    build_detailed_search_query,
)
from src.applicants.schemas.arbeitsagentur.response import ApplicantSearchResponse
from src.applicants.schemas.arbeitsagentur.enums import (
    EducationType,
    LocationRadius,
    OfferType,
    WorkingTime,
    WorkExperience,
    ContractType,
    Disability,
)
from src.applicants.schemas.arbeitsagentur.schemas import (
    BewerberDetail,
    BewerberUebersicht,
)
from src.applicants.schemas.extended.response import FetchDetailedApplicantsResponse
from src.applicants.service.arbeitsagentur import ApplicantApi
from src.configs import DEFAULT_LOGGING_CONFIG


arbeitsagentur_router = APIRouter()


router = APIRouter()

logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@router.get("/applicants/fetch", response_model=FetchApplicantsResponse)
def fetch_applicants(params: Annotated[Dict, Depends(FetchParameters)]):
    api = ApplicantApi()
    api.init()
    db = SearchedApplicantsDb()
    searched_applicants_refnrs = []
    extended_search_params: FetchParameters = FetchParameters(**params.__dict__)
    page_start: int = (
        extended_search_params.pages_start
        if extended_search_params.pages_start is not None
        else 0
    )
    for page_idx, search_parameters in enumerate(
        extended_search_params.get_original_search_params()
    ):
        search_result_dict: Dict = api.search_applicants(search_parameters)
        logger.info(
            f"Fetching resumes from page {page_start + page_idx + 1} with keys: {search_result_dict.keys()}"
        )
        if "messages" in search_result_dict:
            logger.warning(
                f"Error while fetching resumes: {search_result_dict['messages']}"
            )
            raise HTTPException(status_code=400, detail=search_result_dict["messages"])
        elif "bewerber" not in search_result_dict:
            logger.warning(f"No applicants found on page {page_start + page_idx + 1}")
            break
        search_result: ApplicantSearchResponse = ApplicantSearchResponse(
            **search_result_dict
        )
        for applicant in search_result.bewerber:
            db.upsert(applicant)
            searched_applicants_refnrs.append(applicant.refnr)

    response = {
        "count": len(searched_applicants_refnrs),
        "applicantRefnrs": searched_applicants_refnrs,
    }

    return response


@router.get("/applicants/search", response_model=SearchApplicantsResponse)
def search_applicants(
    keywords: List[Text] = Query([]),
    maxGraduationYear: int = Query(None),
    minWorkExperienceYears: int = Query(None),
    careerField: Text = Query(None),
    workingTime: WorkingTime = WorkingTime.UNDEFINED,
    locationKeyword: Text = Query(None),
    locationRadius: int = Query(None),
    page: int = 1,
    size: int = 25,
):
    search_parameters = ExtendedSearchParameters(
        keywords=keywords,
        max_graduation_year=maxGraduationYear,
        min_work_experience_years=minWorkExperienceYears,
        career_field=careerField,
        working_time=workingTime,
        location_keyword=locationKeyword,
        location_radius=locationRadius,
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

    applicants = applicants[(page - 1) * size : (page - 1) * size + size]

    response = {
        "maxCount": total_count,
        "count": len(applicants),
        "applicantRefnrs": [candidate.refnr for candidate in applicants],
        "applicantLinks": [
            f"https://www.arbeitsagentur.de/bewerberboerse/bewerberdetail/{candidate.refnr}"
            for candidate in applicants
        ],
        "applicants": applicants,
    }

    return response


@router.post(
    "/applicants/fetch/details", response_model=FetchDetailedApplicantsResponse
)
def fetch_applicant_details(request: FetchApplicantsDetailsRequest):
    applicant_ids: List[Text] = request.applicantIds

    db = DetailedApplicantsDb()
    api = ApplicantApi()
    api.init()

    all_applicants_details: List[BewerberDetail] = []
    for applicant_id in applicant_ids:
        applicant_details_dict: Dict = api.get_applicant(applicant_id)
        if "messages" in applicant_details_dict:
            logger.warning(
                f"Error while fetching details for applicant {applicant_id}: {applicant_details_dict['messages']}"
            )
            raise HTTPException(
                status_code=400, detail=applicant_details_dict["messages"]
            )
        elif "refnr" not in applicant_details_dict:
            logger.warning(f"No details found for applicant {applicant_id}")
            continue
        applicant_detail: BewerberDetail = BewerberDetail(**applicant_details_dict)
        all_applicants_details.append(applicant_detail)
        db.upsert(applicant_detail)

    response = {
        "count": len(all_applicants_details),
        "applicantRefnrs": [applicant.refnr for applicant in all_applicants_details],
    }

    return response


@router.post("/applicants/search/details", response_class=JSONResponse)
def search_applicant_details(
    jobTitle: Optional[Text] = None,
    location: Optional[Text] = None,
    minAvgJobPositionYears: Optional[int] = None,
    minWorkExperienceYears: Optional[int] = None,
    maxSabbaticalTimeYears: Optional[int] = None,
    jobKeywords: List[Text] = Query([]),
    educationKeyword: Optional[Text] = None,
    skills: List[Text] = Query([]),
    languages: List[Text] = Query([]),
    page: int = 1,
    size: int = 25,
):
    search_parameters = ExtendedDetailedSearchParameters(
        job_title=jobTitle,
        location=location,
        min_avg_job_position_years=minAvgJobPositionYears,
        min_work_experience_years=minWorkExperienceYears,
        max_sabbatical_time_years=maxSabbaticalTimeYears,
        job_keywords=jobKeywords,
        education_keyword=educationKeyword,
        skills=skills,
        languages=languages,
    )

    query = build_detailed_search_query(search_parameters)
    logger.info(f"Query: {query}")

    db = DetailedApplicantsDb()

    if query is not None:
        applicants = db.get(query)
    else:
        applicants = db.get_all()

    total_count: int = len(applicants)
    logger.info(f"Found in total {total_count} applicants")

    applicants = applicants[(page - 1) * size : (page - 1) * size + size]

    response = {
        "maxCount": total_count,
        "count": len(applicants),
        "applicantRefnrs": [candidate.refnr for candidate in applicants],
        "applicantLinks": [
            f"https://www.arbeitsagentur.de/bewerberboerse/bewerberdetail/{candidate.refnr}"
            for candidate in applicants
        ],
        "applicants": applicants,
    }

    return response


@router.post("/applicants/suggest_criteria", response_model=SearchCriteriaSuggestion)
def suggest_criteria(job_description: Text = Query()):
    query = build_knowledge_search_query(job_description)
    logger.info(f"Query: {query}")

    competences_db = CompetencesDb()
    competences_results = competences_db.get(query)

    location_db: LocationDb = LocationDb()
    location_results = location_db.get(query)

    jobs_db = JobsDb()
    job_results = jobs_db.get(query)

    skills_db = SkillsDb()
    skills_results = skills_db.get(query)

    licenses_db = LicensesDb()
    licenses_results = licenses_db.get(query)

    languages_db = LanguagesDb()
    languages_results = languages_db.get(query)

    work_fields_db = WorkfieldsDb()
    work_fields_results = work_fields_db.get(query)

    return {
        "locations": location_results,
        "jobTitles": job_results,
        "jobDescriptions": work_fields_results,
        "competences": competences_results,
        "skills": skills_results,
        "licenses": licenses_results,
        "languages": languages_results,
    }
