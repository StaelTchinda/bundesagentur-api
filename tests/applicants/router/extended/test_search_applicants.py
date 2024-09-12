import re
from typing import Any, Dict, Iterable, List, Optional, Text
import unittest
import warnings
from anyio import Path
from fastapi.testclient import TestClient
import httpx
from parameterized import parameterized


PROJECT_PATH: Path = Path(__file__).parents[4]
import sys

sys.path.append(str(PROJECT_PATH))

print("PROJECT_PATH", PROJECT_PATH)

from src.applicants.schemas.arbeitsagentur.schemas import BewerberUebersicht, TimePeriod
from src.applicants.schemas.arbeitsagentur.enums import (
    ContractType,
    Disability,
    EducationType,
    LocationRadius,
    OfferType,
    WorkExperience,
    WorkingTime,
)
from src.applicants.schemas.extended.response import SearchApplicantsResponse
from src.start import app
from tests.utils.regex import ignore_case_in_regex, search_regex_in_deep
from tests.utils.values import (
    DEFAULT_PAGE_SIZE,
    EXPERIENCE_YEARS,
    LOCATIONS,
    SEARCH_KEYWORDS,
    GRADUATION_YEARS,
)
from src.applicants.service.extended.db import SearchedApplicantsDb


class TestSearchApplicants(unittest.TestCase):
    API_PATH: Text = "/applicants/search"

    def __init__(self, *args, **kwargs):
        super(TestSearchApplicants, self).__init__(*args, **kwargs)
        self.client = TestClient(app)
        self.db = SearchedApplicantsDb()

    def _test_response_is_valid(
        self, response: httpx.Response
    ) -> SearchApplicantsResponse:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().keys(), SearchApplicantsResponse.model_fields.keys()
        )
        search_response: SearchApplicantsResponse = SearchApplicantsResponse(
            **response.json()
        )
        return search_response

    def test_no_parameters(self):
        response = self.client.get(self.API_PATH)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(
            response
        )
        self.assertGreaterEqual(search_response.maxCount, search_response.count)
        self.assertEqual(search_response.count, len(search_response.applicantRefnrs))
        self.assertEqual(search_response.count, len(search_response.applicantLinks))
        self.assertEqual(search_response.count, len(search_response.applicants))
        self.assertGreater(search_response.count, 0)

    @parameterized.expand(LOCATIONS)
    def test_parameter_location(self, location: Text):
        params: Dict = {"locationKeyword": location, "size": DEFAULT_PAGE_SIZE}
        search_response: SearchApplicantsResponse = self.search_over_all_pages(params)
        for applicant in search_response.applicants:
            self.assertIsNotNone(applicant.lokation)
            if applicant.lokation is not None:
                if applicant.lokation.ort is not None:
                    self.assertRegex(ignore_case_in_regex(applicant.lokation.ort), location)
                elif applicant.lokation.region is not None:
                    self.assertRegex(ignore_case_in_regex(applicant.lokation.region), location)
                else:
                    self.assertIsNot((applicant.lokation.ort, applicant.lokation.region), (None, None))
        # applicantrefnr = [applicant for x in search_response.applicantRefnrs if "a" in x]
        for applicant in self.db.get_all():
            if applicant.refnr not in search_response.applicantRefnrs:
                if applicant.lokation is not None:
                    if applicant.lokation.ort is not None:
                        self.assertNotRegex(applicant.lokation.ort, location)
                    elif applicant.lokation.region is not None:
                        self.assertNotRegex(applicant.lokation.region, location)
                    else:
                        self.assertIsNone(applicant.lokation.ort)
                        self.assertIsNone(applicant.lokation.region)
                        self.assertIsNone(applicant.lokation.plz)
                else:
                    self.assertIsNone(applicant.lokation)

    @parameterized.expand([working_time.value for working_time in WorkingTime])
    def test_parameter_working_time(self, working_time: Text):
        params: Dict = {"workingTime": working_time}
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(
            response
        )
        for applicant in search_response.applicants:
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

    @parameterized.expand(GRADUATION_YEARS)
    def test_parameter_max_graduation_year(self, max_graduation_year: int):
        params: Dict = {"maxGraduationYear": max_graduation_year}
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(
            response
        )

        for applicant in search_response.applicants:
            self.assertIsNotNone(applicant.ausbildungen)
            if applicant.ausbildungen is None:
                return
            graduation_years: List[int] = [
                ausbildung.jahr for ausbildung in applicant.ausbildungen
            ]

            has_graduated_before: bool = any(
                [year <= max_graduation_year for year in graduation_years]
            )
            self.assertTrue(
                has_graduated_before,
                f"None of the graduation years {graduation_years} is before {max_graduation_year}",
            )

    @parameterized.expand(EXPERIENCE_YEARS)
    def test_parameter_min_work_experience_years(self, min_work_experience_years: int):
        params: Dict = {"minWorkExperienceYears": min_work_experience_years}
        response = self.client.get(self.API_PATH, params=params)
        search_response: SearchApplicantsResponse = self._test_response_is_valid(
            response
        )

        for applicant in search_response.applicants:
            self.assertIsNotNone(applicant.erfahrung)
            if applicant.erfahrung is None:
                return

            self.assertIsNot(
                (
                    applicant.erfahrung.gesamterfahrung,
                    applicant.erfahrung.berufsfeldErfahrung,
                ),
                (None, None),
            )

            experience_years: Optional[int] = None
            if applicant.erfahrung.gesamterfahrung is not None:
                total_experience_years: int = TimePeriod(
                    applicant.erfahrung.gesamterfahrung
                ).get_years()
                experience_years = total_experience_years

            if applicant.erfahrung.berufsfeldErfahrung is not None:
                splitted_experience_years: List[int] = []
                for exp in applicant.erfahrung.berufsfeldErfahrung:
                    self.assertIsNotNone(exp.erfahrung)
                    if exp.erfahrung is None:
                        return
                    splitted_experience_years.append(
                        TimePeriod(exp.erfahrung).get_years()
                    )
                total_experience_years = sum(splitted_experience_years)
                if (
                    experience_years is not None
                    and experience_years != total_experience_years
                ):
                    print(
                        f"Sum of splitted experience years: {total_experience_years} = sum({splitted_experience_years}), total experience years: {experience_years}"
                    )
                    experience_years = max(experience_years, total_experience_years)
                else:
                    experience_years = total_experience_years

            self.assertGreaterEqual(experience_years, min_work_experience_years)

    # TODO: Write further tests

    def assertRegexInDeep(
        self, obj: Dict[Text, Any], regex: Text, msg: Optional[Text] = None
    ):
        if msg is None:
            msg = f"Regex {regex} not found in {obj}"

        self.assertTrue(search_regex_in_deep(regex, obj), msg)

    def search_over_all_pages(self, params: Dict) -> SearchApplicantsResponse:
        params_with_page: Dict = params.copy()
        if "page" in params_with_page:
            warnings.warn("page parameter will be ignored")
            del params_with_page["page"]

        if "size" not in params_with_page:
            params_with_page["size"] = DEFAULT_PAGE_SIZE
            warnings.warn(
                f"size parameter not found, using default page size {DEFAULT_PAGE_SIZE}"
            )

        has_reached_last_page: bool = False
        current_page: int = 1
        final_response: SearchApplicantsResponse = None
        while not has_reached_last_page:
            params_with_page["page"] = current_page
            response = self.client.get(self.API_PATH, params=params_with_page)
            search_response: SearchApplicantsResponse = self._test_response_is_valid(
                response
            )
            if final_response is None:
                final_response = search_response
            else:
                final_response = merge_responses([final_response, search_response])
            self.assertGreaterEqual(final_response.maxCount, final_response.count)
            if search_response.count < params_with_page["size"]:
                has_reached_last_page = True
            else:
                current_page += 1
        self.assertEqual(final_response.count, final_response.maxCount)

        return final_response


def get_empty_response() -> SearchApplicantsResponse:
    return SearchApplicantsResponse(
        count=0, maxCount=0, applicantRefnrs=[], applicantLinks=[], applicants=[]
    )


def merge_responses(
    responses: Iterable[SearchApplicantsResponse],
) -> SearchApplicantsResponse:
    merged_response: SearchApplicantsResponse = get_empty_response()
    is_first_response: bool = True
    for response in responses:
        if is_first_response:
            merged_response.maxCount = response.maxCount
            is_first_response = False
        elif response.maxCount != merged_response.maxCount:
            raise ValueError(
                f"Max count of response {response} does not match max count of merged response {merged_response}"
            )
        merged_response.count += response.count
        merged_response.applicantRefnrs.extend(response.applicantRefnrs)
        merged_response.applicantLinks.extend(response.applicantLinks)
        merged_response.applicants.extend(response.applicants)

    return merged_response


if __name__ == "__main__":
    unittest.main()
