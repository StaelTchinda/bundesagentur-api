from typing import Text
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.arbeitsagentur.models.response import ApplicantSearchResponse
from src.arbeitsagentur.models.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability
from src.arbeitsagentur.models.request import SearchParameters
from src.arbeitsagentur.service import ApplicantApi

import re
import json

router = APIRouter()

#very naive approach to convert durations in the format P5Y3M22D to an integer number of days
#todo: make this not bad
def iso_datestring_to_days(iso_date : str) -> int:
    search = re.search(r"P((\d+)Y)?((\d+)M)?((\d+)D)?", iso_date)
    n_years     = search.group(2)
    n_months    = search.group(4)
    n_days      = search.group(6)

    total = 0
    if(n_years is not None):
        total += 365.25*int(n_years)
    if(n_months is not None):
        total += 30.43*int(n_months)
    if(n_days is not None):
        total += int(n_days)

    return(int(total))

#do a search filtered by the parameters relevant to seniorconnect
#again, this seems to me a bit overly complicated -> can json dict be parsed to object?
@router.get("/applicants/custom_search", response_model=ApplicantSearchResponse)
def custom_search_applicants(
    graduationYear : int = None,
    minWorkExperienceYears : int = None,
    workExperienceJobs : Text = None,
    workingTime : WorkingTime = None,
    locationKeyword : Text = None
):
    search_response = search_applicants(locationKeyword=locationKeyword)
    candidates = search_response["bewerber"]
    _candidates = candidates.copy()

    for candidate in candidates:
        print(candidate["refnr"])

        if(graduationYear is not None):
            #remove candidates that don't match graduationYear
            match = False
            if("ausbildungen" in candidate.keys()):
                for education in candidate["ausbildungen"]:
                    accepted_educations = ["Mittlere Reife / Mittlerer Bildungsabschluss", "Hauptschulabschluss"]
                    print(education["art"])
                    if(education["art"] in accepted_educations and int(education["jahr"]) == graduationYear):
                        match = True
                        break
            
            if(not match):
                _candidates.remove(candidate)
                continue

        if(minWorkExperienceYears is not None):
            #remove candidates that don't match minWorkExperienceDays
            match = False
            if("erfahrung" in candidate.keys()):
                experience_days = iso_datestring_to_days(candidate["erfahrung"]["gesamterfahrung"])
                if(experience_days >= minWorkExperienceYears*365.25):
                    match = True
            
            if(not match):
                _candidates.remove(candidate)
                continue

        if(workExperienceJobs is not None):
            #remove candidates that don't match workExperienceJobs
            match = False
            if("erfahrung" in candidate.keys()):
                if("berufsfeldErfahrung" in candidate["erfahrung"].keys()):
                    for work_field in candidate["erfahrung"]["berufsfeldErfahrung"]:
                        if(work_field["berufsfeld"] in workExperienceJobs):
                            match = True
                            break
            
            if(not match):
                _candidates.remove(candidate)
                continue

        if(workingTime is not None):
            #remove candidates that don't match workingTime
            match = False
            if("arbeitszeitModelle" in candidate.keys()):
                for work_time in candidate["arbeitszeitModelle"]:
                    if(work_time == workingTime):
                        match = True
                        break

            if(not match):
                _candidates.remove(candidate)
                continue

    return(_candidates)


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

