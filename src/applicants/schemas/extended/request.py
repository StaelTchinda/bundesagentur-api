from typing import List, Text
from pydantic import BaseModel



class FetchApplicantsRequest(BaseModel):
    applicantIds : List[Text]


