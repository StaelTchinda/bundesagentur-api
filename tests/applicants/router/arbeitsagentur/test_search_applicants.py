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

from src.applicants.schemas.arbeitsagentur.enums import (
    ContractType,
    Disability,
    EducationType,
    LocationRadius,
    OfferType,
    WorkExperience,
    WorkingTime,
)
from src.applicants.schemas.arbeitsagentur.schemas import ApplicantSearchResponse
from src.start import app
from tests.utils.regex import search_regex_in_deep
from tests.utils.values import LOCATIONS, SEARCH_KEYWORDS


class TestSearchApplicants(unittest.TestCase):
    API_PATH: Text = "/applicants/arbeitsagentur/search"

    def __init__(self, *args, **kwargs):
        super(TestSearchApplicants, self).__init__(*args, **kwargs)
        self.client = TestClient(app)

    def _test_response_is_valid(
        self, response: httpx.Response
    ) -> ApplicantSearchResponse:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().keys(), ApplicantSearchResponse.model_fields.keys()
        )
        search_response: ApplicantSearchResponse = ApplicantSearchResponse(
            **response.json()
        )
        return search_response

    def test_no_parameters(self):
        response = self.client.get(self.API_PATH)
        search_response: ApplicantSearchResponse = self._test_response_is_valid(
            response
        )
        self.assertGreater(len(search_response.bewerber), 0)

    @parameterized.expand(LOCATIONS)
    def test_parameter_location(self, location: Text):
        params: Dict = {"locationKeyword": location}
        response = self.client.get(self.API_PATH, params=params)
        search_response: ApplicantSearchResponse = self._test_response_is_valid(
            response
        )
        for applicant in search_response.bewerber:
            self.assertIsNotNone(applicant.lokation)
            if applicant.lokation.ort is not None:
                self.assertRegex(applicant.lokation.ort, location)
                self.assertRegex

    @parameterized.expand([working_time.value for working_time in WorkingTime])
    def test_parameter_working_time(self, working_time: Text):
        params: Dict = {"workingTime": working_time}
        response = self.client.get(self.API_PATH, params=params)
        search_response: ApplicantSearchResponse = self._test_response_is_valid(
            response
        )
        for applicant in search_response.bewerber:
            self.assertIsNotNone(applicant.arbeitszeitModelle)
            if applicant.arbeitszeitModelle is not None:
                self.assertGreater(len(applicant.arbeitszeitModelle), 0)
                if working_time != WorkingTime.UNDEFINED.value:
                    self.assertIn(
                        working_time,
                        [
                            arbeitszeit.value
                            for arbeitszeit in applicant.arbeitszeitModelle
                        ],
                    )

    @parameterized.expand(SEARCH_KEYWORDS)
    def test_parameter_keyword(self, keyword: Text):
        params: Dict = {"searchKeyword": keyword}
        response = self.client.get(self.API_PATH, params=params)
        search_response: ApplicantSearchResponse = self._test_response_is_valid(
            response
        )
        for applicant in search_response.bewerber:
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
    #     response = self.client.get(self.API_PATH, params=params)
    #     search_response: ApplicantSearchResponse = self._test_response_is_valid(response)
    #     for applicant in search_response.bewerber:
    #         if search_keyword is not None:
    #             self.assertRegexInDeep(applicant.__dict__, search_keyword)
    #         if location is not None:
    #             self.assertIsNotNone(applicant.lokation)
    #             if applicant.lokation.ort is not None:
    #                 self.assertRegex(applicant.lokation.ort, location)
    #         if working_time != WorkingTime.UNDEFINED:
    #             self.assertIsNotNone(applicant.arbeitszeitModelle)
    #             if applicant.arbeitszeitModelle is not None:
    #                 self.assertIn(working_time.value, [arbeitszeit.value for arbeitszeit in applicant.arbeitszeitModelle])

    def assertRegexInDeep(
        self, obj: Dict[Text, Any], regex: Text, msg: Optional[Text] = None
    ):
        if msg is None:
            msg = f"Regex {regex} not found in {obj}"

        self.assertTrue(search_regex_in_deep(regex, obj), msg)


if __name__ == "__main__":
    unittest.main()
