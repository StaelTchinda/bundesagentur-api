from pydantic import BaseModel
from typing import List

class SearchCriteriaSuggestions(BaseModel):
    certificates: List[str]
    competences: List[str]
    jobs: List[str]
    languages: List[str]
    licenses: List[str]
    location: List[str]
    skills: List[str]
    workfields: List[str]
