from typing import List, Union, Text, Dict
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
    searchKeyword: Union[Text, None]
    educationType: Union[EducationType, None]
    locationKeyword: Union[Text, None]
    locationRadius: Union[LocationRadius, None]
    offerType: Union[OfferType, None]
    workingTime: Union[WorkingTime, None]
    workExperience: Union[WorkExperience, None]
    contractType: Union[ContractType, None]
    disability: Union[Disability, None]
    page: Union[int, None]
    size: Union[int, None]
    # publicationDateAge: Union[int, None] # Acceptable values: 1, 7, 14, 28
    # accessibility: Union[Accessibiltiy, None] # Params values: E-Mail;Telefon;Post

    # Filter criteria with text values
    locations: Union[List[Text], None]
    # occupationalFields: Union[List[Text], None]
    # occupations: Union[List[Text], None]
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
