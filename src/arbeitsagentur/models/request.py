from typing import Union, Text, Dict
from pydantic import BaseModel
from src.arbeitsagentur.models.enums import EducationType, LocationRadius, OfferType, WorkingTime, WorkExperience, ContractType, Disability


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
    "size": "size"
}

class DetailedApplicantSearchRequest(BaseModel):
    applicantIds : list[str]