from typing import Iterable, List, Text, Optional
from fastapi import Query
from pydantic import BaseModel

from src.applicants.schemas.arbeitsagentur.request import SearchParameters
from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, InputWorkingTime, LocationRadius, OfferType, WorkExperience, WorkingTime


class FetchParameters(BaseModel):
    searchKeyword: Optional[Text] = Query(None)
    educationType: EducationType = EducationType.UNDEFINED
    locationKeyword: Optional[Text] = None
    locationRadius: LocationRadius = LocationRadius.ZERO
    offerType: OfferType = OfferType.WORKER
    workingTime: InputWorkingTime = InputWorkingTime.UNDEFINED
    workExperience: WorkExperience = WorkExperience.WITH_EXPERIENCE
    contractType: ContractType = ContractType.UNDEFINED
    disability: Disability = Disability.UNDEFINED
    pages_count: int = 1
    pages_start: int = 1
    size: int = 25

    locations: Optional[List[Text]] = None

    def get_original_search_params(self) -> Iterable[SearchParameters]:
        for page_idx in range(self.pages_start, self.pages_start+self.pages_count):
            params: SearchParameters = SearchParameters(
                searchKeyword=self.searchKeyword,
                educationType=self.educationType,
                locationKeyword=self.locationKeyword,
                locationRadius=self.locationRadius,
                offerType=self.offerType,
                workingTime=self.workingTime,
                workExperience=self.workExperience,
                contractType=self.contractType,
                disability=self.disability,
                page=page_idx,
                size=self.size,
                locations=self.locations
            )
            yield params


class FetchApplicantsDetailsRequest(BaseModel):
    applicantIds : List[Text]


class ExtendedSearchParameters(BaseModel):
    keywords: Optional[List[Text]] = None
    max_graduation_year: Optional[int] = None
    min_work_experience_years: Optional[int] = None
    career_field: Optional[Text] = None
    working_time: WorkingTime = WorkingTime.UNDEFINED
    location_keyword: Optional[Text] = None
    location_radius: Optional[int] = None


class ExtendedDetailedSearchParameters(BaseModel):
   job_title : Optional[Text] = None
   location : Optional[Text] = None
   min_avg_job_position_years : Optional[int] = None
   min_work_experience_years : Optional[int] = None
   max_sabbatical_time_years : Optional[int] = None
   job_keywords : Optional[List[Text]] = None
   education_keyword : Optional[Text] = None
   skills : Optional[List[Text]] = None
   languages : Optional[List[Text]] = None