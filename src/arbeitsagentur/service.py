from typing import Dict, Optional, Text
import requests

from src.arbeitsagentur.models.request import SearchParameters

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

    def search_applicants(self, search_parameters: SearchParameters):
        request_params = search_parameters.dict()
        response = requests.get(self.api_search_url, headers={'OAuthAccessToken': self.token}, params=request_params)
        return response.json()

    def get_applicant(self, applicant_id: Text):
        api_url = f"{self.api_detail_url}/{applicant_id}"
        response = requests.get(api_url, headers={'OAuthAccessToken': self.token})
        return response.json()
