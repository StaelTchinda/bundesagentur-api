from enum import Enum
from typing import Any, Dict, Optional, Text
import requests
import logging

from src.arbeitsagentur.models.enums import ParamEnum
from src.arbeitsagentur.models.request import SearchParameters, SEARCH_PARAMETERS_TO_GET_PARAMS

logger = logging.getLogger(__name__)

class ApplicantApi:
    api_base_url: Text = "https://rest.arbeitsagentur.de/jobboerse/bewerbersuche-service/pc/v1"
    api_search_url: Text = f"{api_base_url}/bewerber"
    api_detail_url: Text = f"{api_base_url}/bewerberdetails"
    token_url: Text = "https://rest.arbeitsagentur.de/oauth/gettoken_cc"
    auth: Dict[Text, Text] = {'client_id':'919b0af7-6e5f-4542-a7f5-04268b8bae2e', 'client_secret':'93fce94c-5be2-4dc8-b040-c62818a4b003', 'grant_type':'client_credentials'}

    def __init__(self):
        self.token: Optional[Text] = None
        pass
    
    def init(self):
        response = requests.post(self.token_url, data=self.auth)
        self.token = response.json().get("access_token")

    def search_applicants(self, search_parameters: Optional[SearchParameters] = None):
        request_params: Dict[Text, Any] = {}
        if search_parameters is not None:
            for key, value in search_parameters.dict().items():
                if value is None:
                    continue
                if isinstance(value, ParamEnum):
                    request_params[SEARCH_PARAMETERS_TO_GET_PARAMS[key]] = value.param_value
                else:
                    request_params[SEARCH_PARAMETERS_TO_GET_PARAMS[key]] = value
        logger.info(f"Searching applicants with the following parameters: {request_params}")
        response = requests.get(self.api_search_url, headers={'OAuthAccessToken': self.token}, params=request_params)
        logger.info(f"Received response: {response.json()}")
        return response.json()

    def get_applicant(self, applicant_id: Text):
        api_url = f"{self.api_detail_url}/{applicant_id}"
        response = requests.get(api_url, headers={'OAuthAccessToken': self.token})
        return response.json()
