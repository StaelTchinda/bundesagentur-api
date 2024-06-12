import re
from typing import Any, Dict, Iterable, List, Optional, Text
import unittest
from anyio import Path
from fastapi.testclient import TestClient
import httpx
from parameterized import parameterized


PROJECT_PATH: Path = Path(__file__).parents[4]
import sys
sys.path.append(str(PROJECT_PATH))

print("PROJECT_PATH", PROJECT_PATH)

from src.applicants.schemas.arbeitsagentur.schemas import BewerberUebersicht, TimePeriod
from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, LocationRadius, OfferType, WorkExperience, WorkingTime
from src.applicants.schemas.extended.response import SearchApplicantsResponse
from src.start import app
from tests.utils.regex import ignore_case_in_regex, search_regex_in_deep
from tests.utils.values import DEFAULT_PAGE_SIZE, EXPERIENCE_YEARS, LOCATIONS, SEARCH_KEYWORDS, GRADUATION_YEARS
from src.applicants.service.extended.db import SearchedApplicantsDb

class TestSearchApplicants(unittest.TestCase):
    API_PATH: Text = "/applicants/search"

    def __init__(self, *args, **kwargs):
        super(TestSearchApplicants, self).__init__(*args, **kwargs)
        self.client = TestClient(app)
        self.db = SearchedApplicantsDb()

    def _test_response_is_valid(self, response: httpx.Response) -> SearchApplicantsResponse:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().keys(), SearchApplicantsResponse.model_fields.keys())
        search_response: SearchApplicantsResponse = SearchApplicantsResponse(**response.json())
        return search_response

    def test_no_parameters(self):
        response = self.client.get(self.API_PATH)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(response)
        self.assertGreaterEqual(search_response.maxCount, search_response.count)
        self.assertEqual(search_response.count, len(search_response.applicantRefnrs))
        self.assertEqual(search_response.count, len(search_response.applicantLinks))
        self.assertEqual(search_response.count, len(search_response.applicants))
        self.assertGreater(search_response.count, 0)

    @parameterized.expand(LOCATIONS)
    def test_parameter_location(self, location: Text):
        params: Dict = {
            "locationKeyword": location,
            "size": DEFAULT_PAGE_SIZE
        }
        all_matching_applicant_refnrs: List[Text] = []
        next_page: Optional[int] = 1
        while next_page is not None:
            params.update({"page": next_page})
            response = self.client.get(self.API_PATH, params=params)
            search_response: SearchApplicantsResponse = self._test_response_is_valid(response)

            for candidate in search_response.applicants:
                self.assertIsNotNone(candidate.lokation)
                if candidate.lokation is not None:
                    self.assertRegex(ignore_case_in_regex(candidate.lokation.ort), location)

            all_matching_applicant_refnrs.extend(search_response.applicantRefnrs)
            if DEFAULT_PAGE_SIZE * next_page < search_response.maxCount:
                next_page += 1
            else:
                next_page = None  

        for applicant in self.db.get_all():
            if applicant.refnr not in all_matching_applicant_refnrs:
                if applicant.lokation is not None:
                    if applicant.lokation.ort is not None:
                        self.assertNotRegex(applicant.lokation.ort, location)
                    else:
                        self.assertIsNone(applicant.lokation.ort)
                else:
                    self.assertIsNone(applicant.lokation)


    @parameterized.expand([working_time.value for working_time in WorkingTime]) 
    def test_parameter_working_time(self, working_time: Text):
        params: Dict = {
            "workingTime": working_time
        }
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(response)
        for applicant in search_response.applicants:
            self.assertIsNotNone(applicant.arbeitszeitModelle)
            if applicant.arbeitszeitModelle is not None:
                self.assertGreater(len(applicant.arbeitszeitModelle), 0)
                if working_time != WorkingTime.UNDEFINED.value:
                    self.assertIn(working_time, [arbeitszeit.value for arbeitszeit in applicant.arbeitszeitModelle])

    @parameterized.expand(GRADUATION_YEARS)
    def test_parameter_max_graduation_year(self, max_graduation_year: int):
        params: Dict = {
            "maxGraduationYear": max_graduation_year
        }
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(response)

        for applicant in search_response.applicants:
            self.assertIsNotNone(applicant.ausbildungen)
            if applicant.ausbildungen is None: return
            graduation_years: List[int] = [ausbildung.jahr for ausbildung in applicant.ausbildungen]
            
            has_graduated_before: bool = any([year <= max_graduation_year for year in graduation_years])
            self.assertTrue(has_graduated_before, f"None of the graduation years {graduation_years} is before {max_graduation_year}")

    @parameterized.expand(EXPERIENCE_YEARS)
    def test_parameter_min_work_experience_years(self, min_work_experience_years: int):
        params: Dict = {
            "minWorkExperienceYears": min_work_experience_years
        }
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(response)

        for applicant in search_response.applicants:
            graduation_years: List[int] = []
            self.assertIsNotNone(applicant.erfahrung)
            if applicant.erfahrung is None: return

            self.assertIsNotNone(applicant.erfahrung.gesamterfahrung)
            if applicant.erfahrung.gesamterfahrung is None: return
            total_experience_years: int = TimePeriod(applicant.erfahrung.gesamterfahrung).get_years()

            self.assertIsNotNone(applicant.erfahrung.berufsfeldErfahrung)
            if applicant.erfahrung.berufsfeldErfahrung is None: return
            experience_years: List[int] = []
            for exp in applicant.erfahrung.berufsfeldErfahrung:
                self.assertIsNotNone(exp.erfahrung)
                if exp.erfahrung is None: return
                experience_years.append(TimePeriod(exp.erfahrung).get_years())

            self.assertEqual(total_experience_years, sum(experience_years))
            self.assertGreaterEqual(total_experience_years, min_work_experience_years)

    # TODO: Write further tests

    def assertRegexInDeep(self, obj: Dict[Text, Any], regex: Text, msg: Optional[Text] = None):
        if msg is None:
            msg = f"Regex {regex} not found in {obj}"

        self.assertTrue(search_regex_in_deep(regex, obj), msg)


if __name__ == "__main__":
    unittest.main()
