from typing import List, Text
from pydantic import BaseModel

from applicants.schemas.arbeitsagentur.enums import WorkingTime



class FetchApplicantsRequest(BaseModel):
    applicantIds : List[Text]


class ExtendedSearchParameters(BaseModel):
  keywords: Optional[List[Text]] = None
  max_graduation_year: Optional[int] = None
  min_work_experience_years: Optional[int] = None
  career_field: Optional[Text] = None
  working_time: WorkingTime = WorkingTime.UNDEFINED
  location_keyword: Optional[Text] = None


