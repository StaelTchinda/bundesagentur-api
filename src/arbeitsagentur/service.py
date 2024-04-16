from typing import Optional, Text
import requests

class ApplicantApi:
    api_url =  "https://rest.arbeitsagentur.de/jobboerse/bewerbersuche-service/pc/v1/bewerber"
    auth = {'client_id':'919b0af7-6e5f-4542-a7f5-04268b8bae2e', 'client_secret':'93fce94c-5be2-4dc8-b040-c62818a4b003', 'grant_type':'client_credentials'}

    def __init__(self):
        self.token: Optional[Text] = None
        pass
    
    def init(self):
        response = requests.post("https://rest.arbeitsagentur.de/oauth/gettoken_cc", data=self.auth)
        self.token = response.json().get("access_token")

    def search_applicants(self):
        response = requests.get(self.api_url, headers={'OAuthAccessToken': self.token})
        return response.json()

    def get_applicant(self, applicant_id: Text):
        return "OK"