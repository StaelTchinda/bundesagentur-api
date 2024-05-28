from typing import Any, Dict, Optional, Text
import unittest
from anyio import Path
from fastapi.testclient import TestClient
import httpx
from parameterized import parameterized

PROJECT_PATH: Path = Path(__file__).parents[4]
import sys
sys.path.append(str(PROJECT_PATH))

print("PROJECT_PATH", PROJECT_PATH)

from src.applicants.schemas.extended.response import FetchApplicantsResponse
from src.applicants.service.extended.db import SearchedApplicantsDb
from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, LocationRadius, OfferType, WorkExperience, WorkingTime
from src.applicants.schemas.arbeitsagentur.schemas import BewerberUebersicht
from src.start import app
from tests.utils.regex import search_regex_in_deep
from tests.utils.values import LOCATIONS, SEARCH_KEYWORDS

class TestFetchApplicants(unittest.TestCase):
    API_PATH: Text = "/applicants/fetch"

    def __init__(self, *args, **kwargs):
        super(TestFetchApplicants, self).__init__(*args, **kwargs)
        self.client = TestClient(app)

    def _test_response_is_valid(self, response: httpx.Response) -> FetchApplicantsResponse:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().keys(), FetchApplicantsResponse.model_fields.keys())
        search_response: FetchApplicantsResponse = FetchApplicantsResponse(**response.json())
        return search_response

    def test_no_parameters(self):
        response = self.client.get(self.API_PATH)
        search_response: FetchApplicantsResponse = self._test_response_is_valid(response)
        self.assertEqual(search_response.count, len(search_response.applicantRefnrs))
        self.assertGreater(search_response.count, 0)
    
    @parameterized.expand(LOCATIONS)
    def test_parameter_location(self, location: Text):
        params: Dict = {
            "locationKeyword": location
        }
        response = self.client.get(self.API_PATH, params=params)
        search_response: FetchApplicantsResponse = self._test_response_is_valid(response)
        for applicant_refnr in search_response.applicantRefnrs:
            applicant: Optional[BewerberUebersicht] = self.get_applicant_resume(applicant_refnr)
            self.assertIsNotNone(applicant)
            if applicant is None: return
            self.assertIsNotNone(applicant.lokation)
            if applicant.lokation.ort is None: return
            self.assertRegex(applicant.lokation.ort, location)

    @parameterized.expand([working_time.value for working_time in WorkingTime]) 
    def test_parameter_working_time(self, working_time: Text):
        params: Dict = {
            "workingTime": working_time
        }
        response = self.client.get(self.API_PATH, params=params)
        search_response: FetchApplicantsResponse = self._test_response_is_valid(response)
        for applicant_refnr in search_response.applicantRefnrs:
            applicant: Optional[BewerberUebersicht] = self.get_applicant_resume(applicant_refnr)
            self.assertIsNotNone(applicant)
            if applicant is None: continue
            self.assertIsNotNone(applicant.arbeitszeitModelle)
            if applicant.arbeitszeitModelle is None: continue
            self.assertGreater(len(applicant.arbeitszeitModelle), 0)
            if working_time != WorkingTime.UNDEFINED.value:
                self.assertIn(working_time, [arbeitszeit.value for arbeitszeit in applicant.arbeitszeitModelle])

    @parameterized.expand(SEARCH_KEYWORDS)
    def test_parameter_search_keyword(self, keyword: Text):
        params: Dict = {
            "searchKeyword": keyword
        }
        response = self.client.get("/applicants/arbeitsagentur/search", params=params)
        search_response: FetchApplicantsResponse = self._test_response_is_valid(response)
        for applicant_refnr in search_response.applicantRefnrs:
            applicant: Optional[BewerberUebersicht] = self.get_applicant_resume(applicant_refnr)
            self.assertIsNotNone(applicant)
            if applicant is None: return
            self.assertRegexInDeep(applicant.__dict__, keyword)

    # TODO: make test faster
    # @parameterized.expand([(search_keyword, education_type.value, location, location_radius.value, offer_type.value, working_time.value, work_experience.value, contract_type.value, disability.value, page, size)
    #                       for search_keyword in [None] + SEARCH_KEYWORDS[:2]
    #                       for education_type in [EducationType.UNDEFINED]
    #                       for location in [None] + LOCATIONS[:2]
    #                       for location_radius in LocationRadius
    #                       for offer_type in [OfferType.UNDEFINED, OfferType.WORKER]
    #                       for working_time in [WorkingTime.UNDEFINED, WorkingTime.FULL_TIME]
    #                       for work_experience in [WorkExperience.WITH_EXPERIENCE]
    #                       for contract_type in [ContractType.UNDEFINED]
    #                       for disability in [Disability.UNDEFINED]
    #                       for page in range(1, 2)
    #                       for size in range(25, 100, 25)])
    # def test_multiple_parameters(self,
    #                              search_keyword: Optional[Text] = None,
    #                              education_type: EducationType = EducationType.UNDEFINED,
    #                              location: Optional[Text] = None,
    #                              location_radius: LocationRadius = LocationRadius.ZERO,
    #                              offer_type: OfferType = OfferType.UNDEFINED,
    #                              working_time: WorkingTime = WorkingTime.UNDEFINED,
    #                              work_experience: WorkExperience = WorkExperience.UNDEFINED,
    #                              contract_type: OfferType = OfferType.UNDEFINED,
    #                              disability: OfferType = OfferType.UNDEFINED,
    #                              page: int = 1,
    #                              size: int = 25):
    #     params: Dict = {
    #         "searchKeyword": search_keyword,
    #         "educationType": education_type,
    #         "locationKeyword": location,
    #         "locationRadius": location_radius,
    #         "offerType": offer_type,
    #         "workingTime": working_time,
    #         "workExperience": work_experience,
    #         "contractType": contract_type,
    #         "disability": disability,
    #         "page": page,
    #         "size": size
    #     }
    #     response = self.client.get("/applicants/arbeitsagentur/search", params=params)
    #     search_response: FetchApplicantsResponse = self._test_response_is_valid(response)
    #     for applicant_refnr in search_response.applicantRefnrs:
    #         applicant: Optional[BewerberUebersicht] = self.get_applicant_resume(applicant_refnr)

    #         self.assertIsNotNone(applicant)
    #         if applicant is None: return

    #         if search_keyword is not None:
    #             self.assertRegexInDeep(applicant.__dict__, search_keyword)
    #         if location is not None:
    #             self.assertIsNotNone(applicant.lokation)
    #             if applicant.lokation is None: return
    #             self.assertIsNotNone(applicant.lokation.ort)
    #             if applicant.lokation.ort is None: return
    #             self.assertRegex(applicant.lokation.ort, location)
    #         if working_time != WorkingTime.UNDEFINED:
    #             self.assertIsNotNone(applicant.arbeitszeitModelle)
    #             if applicant.arbeitszeitModelle is None: return
    #             self.assertIn(working_time.value, [arbeitszeit.value for arbeitszeit in applicant.arbeitszeitModelle])

    def assertRegexInDeep(self, obj: Dict[Text, Any], regex: Text, msg: Optional[Text] = None):
        if msg is None:
            msg = f"Regex {regex} not found in {obj}"

        self.assertTrue(search_regex_in_deep(regex, obj), msg)

    
    def get_applicant_resume(self, applicant_refnr: Text) -> Optional[BewerberUebersicht]:
        db = SearchedApplicantsDb()
        applicant: Optional[BewerberUebersicht] = db.get_by_refnr(applicant_refnr)
        return applicant
        


if __name__ == "__main__":
    unittest.main()
