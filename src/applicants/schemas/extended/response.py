from typing import List, Text

from pydantic import BaseModel

from src.applicants.schemas.arbeitsagentur.schemas import BewerberUebersicht, BewerberDetail


class FetchDetailedApplicantsResponse(BaseModel):
    count: int
    applicantRefnrs: List[Text]


class FetchApplicantsResponse(BaseModel):
    count: int
    applicantRefnrs: List[Text]


class SearchApplicantsResponse(BaseModel):
    maxCount: int
    count: int
    applicantRefnrs: List[Text]
    applicantLinks: List[Text]
    applicants: List[BewerberUebersicht]
