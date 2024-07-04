import re
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

from src.applicants.schemas.arbeitsagentur.schemas import TimePeriod
from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, LocationRadius, OfferType, WorkExperience, WorkingTime
from src.applicants.schemas.extended.response import SearchApplicantsResponse
from src.start import app
from tests.utils.regex import search_regex_in_deep
from tests.utils.values import EXPERIENCE_YEARS, LOCATIONS, SEARCH_KEYWORDS, GRADUATION_YEARS
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
            "locationKeyword": location
        }
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(response)
        for applicant in search_response.applicants:
            self.assertIsNotNone(applicant.lokation)
            if applicant.lokation is not None:
                self.assertRegex(applicant.lokation.ort, location)
        #applicantrefnr = [applicant for x in search_response.applicantRefnrs if "a" in x]
        for applicant in self.db.get_all():
            if applicant.refnr not in search_response.applicantRefnrs:
                if applicant.lokation is not None: 
                    self.assertNotRegex(applicant.lokation.ort, location)
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
            self.assertIsNotNone(applicant.erfahrung)
            if applicant.erfahrung is None: return

            self.assertIsNot((applicant.erfahrung.gesamterfahrung, applicant.erfahrung.berufsfeldErfahrung), (None, None))

            experience_years: Optional[int] = None
            if applicant.erfahrung.gesamterfahrung is not None:
                total_experience_years: int = TimePeriod(applicant.erfahrung.gesamterfahrung).get_years()
                experience_years = total_experience_years

            if applicant.erfahrung.berufsfeldErfahrung is not None:
                splitted_experience_years: List[int] = []
                for exp in applicant.erfahrung.berufsfeldErfahrung:
                    self.assertIsNotNone(exp.erfahrung)
                    if exp.erfahrung is None: return
                    splitted_experience_years.append(TimePeriod(exp.erfahrung).get_years())
                total_experience_years = sum(splitted_experience_years)
                if experience_years is not None and experience_years != total_experience_years:
                    print(f"Sum of splitted experience years: {total_experience_years} = sum({splitted_experience_years}), total experience years: {experience_years}")
                    experience_years = max(experience_years, total_experience_years)
                else:
                    experience_years = total_experience_years

            self.assertGreaterEqual(experience_years, min_work_experience_years)

    # TODO: Write further tests

    def assertRegexInDeep(self, obj: Dict[Text, Any], regex: Text, msg: Optional[Text] = None):
        if msg is None:
            msg = f"Regex {regex} not found in {obj}"

        self.assertTrue(search_regex_in_deep(regex, obj), msg)


if __name__ == "__main__":
    unittest.main()
