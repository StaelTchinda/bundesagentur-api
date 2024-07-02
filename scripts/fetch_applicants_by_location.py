import argparse
import logging
from tkinter import E
from typing import Dict, List, Text, Union
from tinydb import Query
from tqdm import tqdm
import os

from src.configs import DEFAULT_LOGGING_CONFIG
from src.applicants.router.arbeitsagentur import search_applicants
from src.applicants.schemas.arbeitsagentur.request import SearchParameters
from src.applicants.schemas.arbeitsagentur.schemas import ApplicantSearchResponse, FacettenElement
from src.applicants.service.extended.db import DetailedApplicantsDb
from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, LocationRadius, OfferType, WorkExperience, WorkingTime
from src.applicants.router.extended import fetch_applicant_details, fetch_applicants
from src.applicants.schemas.extended.request import FetchApplicantsRequest
from src.applicants.schemas.extended.response import FetchApplicantsResponse, FetchDetailedApplicantsResponse, SearchApplicantsResponse


logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser("Fetch resumes of applicants from the Arbeitsagentur to the local DB")

    # searchKeyword: Text | None = None,
    # educationType: EducationType = EducationType.UNDEFINED,
    # locationKeyword: Text | None = None,
    # locationRadius: LocationRadius = LocationRadius.ZERO,
    # offerType: OfferType = OfferType.WORKER,
    # workingTime: WorkingTime = WorkingTime.UNDEFINED,
    # workExperience: WorkExperience = WorkExperience.WITH_EXPERIENCE,
    # contractType: ContractType = ContractType.UNDEFINED,
    # disability: Disability = Disability.UNDEFINED,
    # page: int = 1,
    # size: int = 25,

    # Add the arguments from the above class to the parser
    parser.add_argument("--keyword", type=str, help="Keyword to search for", default=None)
    parser.add_argument("--education_type", type=str, choices=[e.value for e in EducationType], help="Education type", default=EducationType.UNDEFINED.param_value)
    parser.add_argument("--location_keyword", type=str, help="Location keyword", default=None)
    parser.add_argument("--location_radius", type=int, help="Location radius", default=LocationRadius.ZERO.param_value)
    parser.add_argument("--offer_type", type=str, choices=[o.param_value for o in OfferType], help="Offer type", default=OfferType.WORKER.param_value)
    parser.add_argument("--working_time", type=str, choices=[w.param_value for w in WorkingTime], help="Working time", default=WorkingTime.UNDEFINED.param_value)
    parser.add_argument("--work_experience", type=str, choices=[w.param_value for w in WorkExperience], help="Work experience", default=WorkExperience.WITH_EXPERIENCE.param_value)
    parser.add_argument("--contract_type", type=str, choices=[c.param_value for c in ContractType], help="Contract type", default=ContractType.UNDEFINED.param_value)
    parser.add_argument("--disability", type=str, choices=[d.param_value for d in Disability], help="Disability", default=Disability.UNDEFINED.param_value)
    parser.add_argument("--pages_count", type=int, help="Number of pages to fetch", default=100)
    parser.add_argument("--pages_start", type=int, help="Page size", default=None)
    parser.add_argument("--size", type=int, help="Page size", default=25)

    parser.add_argument("--skip_locations", action="store_true", help="Skip locations")

    return parser.parse_args()



# TODO: Move to utils
def get_location_counts(search_parameters: SearchParameters) -> Dict[Text, int]:
    _search_parameters = SearchParameters(**search_parameters.model_dump())
    if _search_parameters.page != 1:
        logger.warning("The page number should be 1 to ensure getting the location counts.")
    if _search_parameters.size != 1:
        logger.error("The size should be 1 to avoid slow responses.")

    response_json: Dict = search_applicants(
        searchKeyword=_search_parameters.searchKeyword,
        educationType=_search_parameters.educationType,
        locationKeyword=_search_parameters.locationKeyword,
        locationRadius=_search_parameters.locationRadius,
        offerType=_search_parameters.offerType,
        workingTime=_search_parameters.workingTime,
        workExperience=_search_parameters.workExperience,
        contractType=_search_parameters.contractType,
        disability=_search_parameters.disability,
        page=1,
        size=1,
        locations=search_parameters.locations
    )
    if "facetten" not in response_json:
        logger.error("No facetten in the response. The response may be invalid: " + str(response_json))
        raise Exception("No facetten in the response. The response may be invalid")
    response: ApplicantSearchResponse = ApplicantSearchResponse(**response_json)
    locations: Dict[Text, int] = response.facetten.arbeitsorte.counts
    return locations


def main():
    args = parse_args()

    search_parameters = SearchParameters(
        searchKeyword=args.keyword,
        educationType=EducationType(args.education_type),
        locationKeyword=args.location_keyword,
        locationRadius=LocationRadius(args.location_radius),
        offerType=OfferType(args.offer_type),
        workingTime=WorkingTime(args.working_time),
        workExperience=WorkExperience(args.work_experience),
        contractType=ContractType(args.contract_type),
        disability=Disability(args.disability),
        page=1,
        size=1,
        locations=None
    )
    location_counts: Dict[Text, int] = get_location_counts(search_parameters)

    print(f"Found in total {sum(location_counts.values())} applicants spread across {len(location_counts)} locations.")
    logger.info(f"Found in total {sum(location_counts.values())} applicants spread across {len(location_counts)} locations: {location_counts}")

    if args.skip_locations:
        original_location_counts = location_counts.copy()
        location_counts = {k: v for k, v in location_counts.items() if k not in args.skip_locations}
        print(f"Skipping {len(original_location_counts) - len(location_counts)} locations")

    global_fetch_pbar = tqdm(list(location_counts.keys()), desc="Searching for applicants over all locations", unit="locations")
    global_fetch_pbar_postfix: Dict = {"location": "", "candidates_count": 0}
    for location in global_fetch_pbar:
        pages_count: int = max(args.pages_count, location_counts[location] // args.size + 1)
        fetch_pbar = tqdm(range(pages_count), desc="Searching for applicants in location", unit="page")
        fetch_pbar_postfix: Dict = {"location": location, "candidates_count": 0}
        if args.pages_start is not None:
            fetch_pbar.update(args.pages_start)
        for page_idx in fetch_pbar:
            # search for applicants
            fetch_response_dict: Dict = fetch_applicants(
                searchKeyword=args.keyword,
                educationType=EducationType(args.education_type),
                locationKeyword=location,
                locationRadius=LocationRadius(args.location_radius),
                offerType=OfferType(args.offer_type),
                workingTime=WorkingTime(args.working_time),
                workExperience=WorkExperience(args.work_experience),
                contractType=ContractType(args.contract_type),
                disability=Disability(args.disability),
                pages_count=1,
                pages_start=page_idx,
                size=args.size
            )
            fetch_response = FetchApplicantsResponse(**fetch_response_dict)
            fetch_pbar_postfix["candidates_count"] += fetch_response.count
            fetch_pbar.set_postfix(fetch_pbar_postfix)
        fetch_pbar.close()
        global_fetch_pbar_postfix["location"] = location
        global_fetch_pbar_postfix["candidates_count"] += fetch_pbar_postfix["candidates_count"]
        global_fetch_pbar.set_postfix(global_fetch_pbar_postfix)

if __name__ == "__main__":
    main()