import argparse
from tkinter import E
from typing import Dict, List, Text
from tinydb import Query
from tqdm import tqdm

from src.applicants.service.extended.db import DetailedApplicantsDb
from src.applicants.schemas.arbeitsagentur.enums import WorkingTime
from src.applicants.router.extended import fetch_applicant_details, search_applicants
from src.applicants.schemas.extended.request import FetchApplicantsRequest
from src.applicants.schemas.extended.response import FetchDetailedApplicantsResponse, SearchApplicantsResponse


def parse_args():
    parser = argparse.ArgumentParser("Search applicants in the local DB and fetch details from Arbeitsagentur API")

    parser.add_argument("--keywords", type=str, nargs="+", help="Keywords to search for", default=[])
    parser.add_argument("--max_graduation_year", type=int, help="Maximum graduation year", default=None)
    parser.add_argument("--min_work_experience_years", type=int, help="Minimum work experience years", default=None)
    parser.add_argument("--career_field", type=str, help="Career field", default=None)
    parser.add_argument("--working_time", type=str, help="Working time", default="UNDEFINED")
    parser.add_argument("--location_keyword", type=str, help="Location keyword", default=None)

    parser.add_argument("--pages_count", type=int, help="Number of pages to fetch", default=1)
    parser.add_argument("--page_size", type=int, help="Page size", default=100)

    parser.add_argument("--skip_existing", action="store_true", help="Skip existing applicants in the DB")

    return parser.parse_args()


def main():
    args = parse_args()

    all_search_responses: List[SearchApplicantsResponse] = []
    search_pbar = tqdm(range(args.pages_count), desc="Searching for applicants", unit="page")
    for page_idx in search_pbar:
        # search for applicants
        search_response_dict: Dict = search_applicants(
            keywords=args.keywords,
            maxGraduationYear=args.max_graduation_year,
            minWorkExperienceYears=args.min_work_experience_years,
            careerField=args.career_field,
            workingTime=WorkingTime[args.working_time],
            locationKeyword=args.location_keyword,
            page=page_idx+1,
            size=args.page_size
        )
        search_response = SearchApplicantsResponse(**search_response_dict)
        all_search_responses.append(search_response)

    print(f"Found in total {sum([response.count for response in all_search_responses])} applicants")

    applicant_refnrs: List[Text] = [applicant_refnr for response in all_search_responses for applicant_refnr in response.applicantRefnrs]

    if args.skip_existing:
        # TODO: create an endpoint to get existing applicants from the local DB based on the refnr
        db = DetailedApplicantsDb()
        existing_applicant_refnrs: List[Text] = [applicant.refnr for applicant in db.get(Query().refnr.one_of(applicant_refnrs))]
        applicant_refnrs = [refnr for refnr in applicant_refnrs if refnr not in existing_applicant_refnrs]

        print(f"Skipping {len(existing_applicant_refnrs)} existing applicants in the DB")

    all_fetch_responses: List[FetchDetailedApplicantsResponse] = []
    fetch_pbar = tqdm(applicant_refnrs, desc="Fetching details", unit="applicant")
    fetch_pbar_postfix: Dict = {"refnr": "", "failed_count": 0}
    failed_refnrs: List[Text] = []
    errors: List[Exception] = []
    for applicant_refnr in fetch_pbar:
        try:
            fetch_response_dict: Dict = fetch_applicant_details(FetchApplicantsRequest(applicantIds=[applicant_refnr]))
        except Exception as e:
            fetch_pbar_postfix["refnr"] = applicant_refnr
            fetch_pbar_postfix["failed_count"] += 1
            fetch_pbar.set_postfix(fetch_pbar_postfix)
            failed_refnrs.append(applicant_refnr)
            errors.append(e)
            continue
        fetch_response = FetchDetailedApplicantsResponse(**fetch_response_dict)
        all_fetch_responses.append(fetch_response)

    print(f"Successfully fetched details for {len(all_fetch_responses)} applicants")
    if len(failed_refnrs) > 0:
        print(f"Failed to fetch details for {len(failed_refnrs)} applicants: {failed_refnrs}")
        print(f"Errors: \n{"\n\t".join([str(error) for error in errors])}")


if __name__ == "__main__":
    main()