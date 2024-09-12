from enum import Enum
from typing import Any, Dict, Optional, Text
import requests
import logging

from src.applicants.schemas.arbeitsagentur.enums import ParamEnum
from src.applicants.schemas.arbeitsagentur.request import (
    SearchParameters,
    SEARCH_PARAMETERS_TO_GET_PARAMS,
)


logger = logging.getLogger(__name__)


class ApplicantApi:
    api_base_url: Text = (
        "https://rest.arbeitsagentur.de/jobboerse/bewerbersuche-service/pc/v1"
    )
    api_search_url: Text = f"{api_base_url}/bewerber"
    api_detail_url: Text = f"{api_base_url}/bewerberdetails"
    api_key: Text = "jobboerse-bewerbersuche-ui"

    def __init__(self):
        pass

    def init(self):
        logger.info("Initializing the API")
        response = requests.post(self.token_url, data=self.auth)
        logger.info(f"Received response with status code {response.status_code}")
        self.token = response.json().get("access_token")
        if self.token is None:
            logger.error(f"No token received. Response: {response.json()}")
            raise Exception("No token received")
        pass

    def search_applicants(
        self, search_parameters: Optional[SearchParameters] = None
    ) -> Dict:
        request_params: Dict[Text, Any] = {}
        if search_parameters is not None:
            for key, value in search_parameters.model_dump().items():
                if value is None:
                    continue
                if isinstance(value, ParamEnum):
                    if value.param_value is None:
                        continue
                    request_params[SEARCH_PARAMETERS_TO_GET_PARAMS[key]] = (
                        value.param_value
                    )
                else:
                    request_params[SEARCH_PARAMETERS_TO_GET_PARAMS[key]] = value
        logger.info(
            f"Searching applicants with the following parameters: {request_params}"
        )
        response = requests.get(
            self.api_search_url,
            headers=self.get_headers(),
            params=request_params,
        )
        logger.info(
            f"Received response with status code {response.status_code} and keys {response.json().keys()}"
        )
        return response.json()

    def get_applicant(self, applicant_id: Text) -> Dict:
        api_url = f"{self.api_detail_url}/{applicant_id}"
        response = requests.get(api_url, headers=self.get_headers())
        return response.json()

    def get_headers(self):
        return {"X-API-Key": self.api_key}
