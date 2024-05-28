from typing import List, Optional, Text

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


class SearchCriteriaSuggestion(BaseModel):
    locations: List[Text]
    jobTitles: List[Text]
    jobDescriptions: List[Text]
    competences: List[Text]
    skills: List[Text]
    licences: List[Text]
    languages: List[Text]
