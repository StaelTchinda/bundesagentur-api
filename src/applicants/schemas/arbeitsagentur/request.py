from typing import List, Optional, Text, Dict
from pydantic import BaseModel
from fastapi import Query
from src.applicants.schemas.arbeitsagentur.enums import (
    EducationType,
    InputWorkingTime,
    LocationRadius,
    OfferType,
    WorkingTime,
    WorkExperience,
    ContractType,
    Disability,
)


class SearchParameters(BaseModel):
    searchKeyword: Optional[Text] = Query(None)
    educationType: EducationType = EducationType.UNDEFINED
    locationKeyword: Optional[Text] = Query(None)
    locationRadius: LocationRadius = LocationRadius.ZERO
    offerType: OfferType = OfferType.WORKER
    workingTime: InputWorkingTime = InputWorkingTime.UNDEFINED
    workExperience: WorkExperience = WorkExperience.WITH_EXPERIENCE
    contractType: ContractType = ContractType.UNDEFINED
    disability: Disability = Disability.UNDEFINED
    page: int = 1
    size: int = 25

    # publicationDateAge: Union[int, None] # Acceptable values: 1, 7, 14, 28
    # accessibility: Union[Accessibiltiy, None] # Params values: E-Mail;Telefon;Post

    # Filter criteria with text values
    # locations: Optional[List[Text]] = Query(None)
    # occupationalFields: Optional[List[Text]] = Query(None)
    # occupations: Optional[List[Text]] = Query(None)
    # ...


SEARCH_PARAMETERS_TO_GET_PARAMS: Dict[Text, Text] = {
    "searchKeyword": "was",
    "educationType": "ausbildungsart",
    "locationKeyword": "wo",
    "locationRadius": "umkreis",
    "offerType": "angebotsart",
    "workingTime": "arbeitszeit",
    "workExperience": "berufserfahrung",
    "contractType": "vertragsart",
    "disability": "behinderung",
    "page": "page",
    "size": "size",
    "locations": "arbeitsorte",
}
