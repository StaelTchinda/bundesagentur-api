import argparse
import logging
from typing import Dict, Text
from tqdm import tqdm

from src.applicants.schemas.extended.request import FetchParameters
from src.configs import DEFAULT_LOGGING_CONFIG
from src.applicants.router.arbeitsagentur import search_applicants
from src.applicants.schemas.arbeitsagentur.request import SearchParameters
from src.applicants.schemas.arbeitsagentur.schemas import ApplicantSearchResponse
from src.applicants.schemas.arbeitsagentur.enums import ContractType, Disability, EducationType, LocationRadius, OfferType, WorkExperience, InputWorkingTime
from src.applicants.router.extended import fetch_applicants
from src.applicants.schemas.extended.response import FetchApplicantsResponse


logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser("Fetch resumes of applicants from the Arbeitsagentur to the local DB")

    parser.add_argument("--keyword", type=str, help="Keyword to search for", default=None)
    parser.add_argument("--education_type", type=str, choices=[e.value for e in EducationType], help="Education type", default=EducationType.UNDEFINED.param_value)
    parser.add_argument("--location_keyword", type=str, help="Location keyword", default=None)
    parser.add_argument("--location_radius", type=int, help="Location radius", default=LocationRadius.ZERO.param_value)
    parser.add_argument("--offer_type", type=str, choices=[o.param_value for o in OfferType], help="Offer type", default=OfferType.WORKER.param_value)
    parser.add_argument("--working_time", type=str, choices=[w.param_value for w in InputWorkingTime], help="Working time", default=InputWorkingTime.UNDEFINED.param_value)
    parser.add_argument("--work_experience", type=str, choices=[w.param_value for w in WorkExperience], help="Work experience", default=WorkExperience.WITH_EXPERIENCE.param_value)
    parser.add_argument("--contract_type", type=str, choices=[c.param_value for c in ContractType], help="Contract type", default=ContractType.UNDEFINED.param_value)
    parser.add_argument("--disability", type=str, choices=[d.param_value for d in Disability], help="Disability", default=Disability.UNDEFINED.param_value)
    parser.add_argument("--pages_count", type=int, help="Number of pages to fetch", default=10000)
    parser.add_argument("--pages_start", type=int, help="Page size", default=None)
    parser.add_argument("--size", type=int, help="Page size", default=25)

    parser.add_argument("--skip_locations", type=str, nargs="*", help="Skip locations")

    return parser.parse_args()



# TODO: Move to utils
def get_location_counts(search_parameters: SearchParameters) -> Dict[Text, int]:
    if search_parameters.page != 1:
        logger.warning("The page number should be 1 to ensure getting the location counts.")
    if search_parameters.size != 1:
        logger.warning("The size should be 1 to avoid slow responses.")

    response_json: Dict = search_applicants(search_parameters)
    if "facetten" not in response_json:
        logger.error("No facetten in the response. The response may be invalid: " + str(response_json))
        raise Exception("No facetten in the response. The response may be invalid")
    response: ApplicantSearchResponse = ApplicantSearchResponse(**response_json)
    logger.info(f"Found {response.maxErgebnisse} max results with {len(response.facetten.arbeitsorte.counts)} locationscovering {sum(response.facetten.arbeitsorte.counts.values())} applicants.")
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
        workingTime=InputWorkingTime(args.working_time),
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
        print(f"Skipping {len(original_location_counts) - len(location_counts)} locations with {sum(original_location_counts.values()) - sum(location_counts.values())} applicants.")

    candidates_count = sum(location_counts.values())
    global_fetch_pbar = tqdm(range(candidates_count), desc="Searching for applicants over all locations", unit="applicant")
    global_fetch_pbar_postfix: Dict = {"location": "", "location_candidates": {"count": 0, "skipped": 0, "total": 0}, "locations": {"count": 0, "skipped": 0, "total": len(location_counts)}}
    build_postfix_dict_elt_str = lambda postfix_elt: f"{postfix_elt['count']}/{postfix_elt['total']}-{postfix_elt['skipped']}"
    build_postfix_dict = lambda postfix: {"location": postfix["location"], "location_candidates": build_postfix_dict_elt_str(postfix["location_candidates"]), "locations": build_postfix_dict_elt_str(postfix["locations"])}
    try:
        for (location, location_candidate_count) in location_counts.items():
            pages_count: int = max(args.pages_count, location_candidate_count // args.size + 1)
            global_fetch_pbar_postfix["location"] = location
            global_fetch_pbar_postfix["location_candidates"]["count"] = 0
            global_fetch_pbar_postfix["location_candidates"]["total"] = location_candidate_count
            global_fetch_pbar_postfix["locations"]["count"] += 1
            if args.pages_start is not None:
                global_fetch_pbar_postfix["location_candidates"]["skipped"] = args.pages_start * args.size
                global_fetch_pbar.update(args.pages_start * args.size)
            global_fetch_pbar.set_postfix(build_postfix_dict(global_fetch_pbar_postfix))

            pages_start: int = args.pages_start if args.pages_start is not None else 1
            for page_idx in range(pages_start, pages_count):
                fetch_params: FetchParameters = FetchParameters(
                    searchKeyword=args.keyword,
                    educationType=EducationType(args.education_type).value,
                    locationKeyword=args.location_keyword,
                    locationRadius=LocationRadius(args.location_radius).value,
                    offerType=OfferType(args.offer_type).value,
                    workingTime=InputWorkingTime(args.working_time).value,
                    workExperience=WorkExperience(args.work_experience).value,
                    contractType=ContractType(args.contract_type).value,
                    disability=Disability(args.disability).value,
                    pages_count=1,
                    pages_start=page_idx,
                    size=args.size,
                    locations=[location]
                )
                fetch_response_dict: Dict = fetch_applicants(fetch_params)
                fetch_response = FetchApplicantsResponse(**fetch_response_dict)
                global_fetch_pbar_postfix["location_candidates"]["count"] += fetch_response.count
                global_fetch_pbar.update(fetch_response.count)
                global_fetch_pbar.set_postfix(build_postfix_dict(global_fetch_pbar_postfix))
                if fetch_response.count < args.size:
                    break
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        global_fetch_pbar.close()
        print("Finished fetching applicants.")
if __name__ == "__main__":
    main()
