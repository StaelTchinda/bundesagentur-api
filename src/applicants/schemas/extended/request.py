from typing import List, Text, Optional
from pydantic import BaseModel

from src.applicants.schemas.arbeitsagentur.enums import WorkingTime



class FetchApplicantsRequest(BaseModel):
    applicantIds : List[Text]


class ExtendedSearchParameters(BaseModel):
  keywords: Optional[List[Text]] = None
  max_graduation_year: Optional[int] = None
  min_work_experience_years: Optional[int] = None
  career_field: Optional[Text] = None
  working_time: WorkingTime = WorkingTime.UNDEFINED
  location_keyword: Optional[Text] = None


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