from typing import Any, Dict, List, Optional, Text
import unittest
from anyio import Path
from fastapi.testclient import TestClient
import httpx
from parameterized import parameterized

PROJECT_PATH: Path = Path(__file__).parents[4]
import sys
sys.path.append(str(PROJECT_PATH))

print("PROJECT_PATH", PROJECT_PATH)

from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, LocationRadius, OfferType, WorkExperience, WorkingTime
from src.applicants.schemas.arbeitsagentur.schemas import ApplicantSearchResponse, BewerberDetail
from src.start import app
from tests.utils.regex import search_regex_in_deep

SEARCH_KEYWORDS: List[Text] = ["Ingenieur", "Manager", "Softwareentwickler", "Krankenschwester", "Lehrer", "Verkäufer"]
LOCATIONS: List[Text] = ["München", "Heilbronn", "Berlin", "Hamburg", "Köln", "Frankfurt am Main"]

class TestSearchApplicants(unittest.TestCase):
    API_PATH: Text = "/applicants/arbeitsagentur/get"

    def __init__(self, *args, **kwargs):
        super(TestSearchApplicants, self).__init__(*args, **kwargs)
        self.client = TestClient(app)

    def _test_response_is_valid(self, response: httpx.Response) -> BewerberDetail:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().keys(), BewerberDetail.model_fields.keys())
        search_response: BewerberDetail = BewerberDetail(**response.json())
        return search_response
    
    def test_applicant_id_is_required(self):
        response = self.client.get(self.API_PATH)
        self.assertEqual(response.status_code, 422)

    @parameterized.expand(["10000-1191185016-B", "10000-1171076518-B", "10000-1198780457-B"])
    def test_applicant_id(self, applicant_id: Text):
        response = self.client.get(self.API_PATH, params={"applicant_id": applicant_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().keys(), BewerberDetail.model_fields.keys())
        applicant: BewerberDetail = BewerberDetail(**response.json())
        self.assertEqual(applicant.refnr, applicant_id)


if __name__ == "__main__":
    unittest.main()
