from datetime import datetime, timedelta
from math import log
import re
from typing import Callable, List, Optional, Text, Union
from tinydb import Query
from tinydb.queries import QueryInstance
import logging


from src.applicants.schemas.arbeitsagentur.enums import WorkingTime
from src.applicants.schemas.arbeitsagentur.schemas import (
    LebenslaufElement,
    Lokation,
    TimePeriod,
)
from src.applicants.schemas.extended.request import (
    ExtendedSearchParameters,
    ExtendedDetailedSearchParameters,
)
from src.configs import DEFAULT_LOGGING_CONFIG


logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def search_re_keyword(field: Union[Query, str], keyword: Text) -> QueryInstance:
    query: Query
    if isinstance(field, Query):
        query = field
    elif isinstance(field, str):
        query = Query().__getattr__(field)
    else:
        raise ValueError(f"Invalid field type: {type(field)}")
    return query.matches(f"{keyword}", re.IGNORECASE)


def build_search_query(
    search_parameters: ExtendedSearchParameters,
) -> Optional[QueryInstance]:
    query: Optional[QueryInstance] = None

    if search_parameters.keywords is not None and search_parameters.keywords != []:
        for keyword in search_parameters.keywords:
            _applicant = Query()
            subquery = (
                search_re_keyword(_applicant.refnr, keyword)
                | search_re_keyword(_applicant.freierTitelStellengesuch, keyword)
                | search_re_keyword(_applicant.berufe, keyword)
                | search_re_keyword(_applicant.letzteTaetigkeit.bezeichnung, keyword)
                | _applicant.erfahrung.berufsfeldErfahrung.any(
                    search_re_keyword(Query().berufsfeld, keyword)
                )
                | _applicant.ausbildungen.any(search_re_keyword(Query().art, keyword))
            )

            if query is None:
                query = subquery
            else:
                query &= subquery

    if search_parameters.max_graduation_year is not None:
        _applicant = Query()
        _education = Query()
        subquery = _applicant.ausbildungen.exists() & _applicant.ausbildungen.any(
            (_education.jahr <= search_parameters.max_graduation_year)
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.min_work_experience_years is not None:
        _applicant = Query()
        experience_duration_check = (
            lambda x: search_parameters.min_work_experience_years is not None
            and x is not None
            and search_parameters.min_work_experience_years <= TimePeriod(x).get_years()
        )

        subquery = (
            _applicant.erfahrung.exists()
            & _applicant.erfahrung.gesamterfahrung.exists()
            & _applicant.erfahrung.gesamterfahrung.test(experience_duration_check)
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.career_field is not None:
        _applicant = Query()
        _experience = Query()
        subquery = (
            _applicant.erfahrung.exists()
            & _applicant.erfahrung.berufsfeldErfahrung.exists()
            & _applicant.erfahrung.berufsfeldErfahrung.any(
                (
                    search_re_keyword(
                        _experience.berufsfeld, search_parameters.career_field
                    )
                )
            )
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if (
        search_parameters.working_time is not None
        and search_parameters.working_time != WorkingTime.UNDEFINED
    ):
        _applicant = Query()
        subquery = _applicant.arbeitszeitModelle.any(
            search_parameters.working_time.value
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.location_keyword is not None:
        _applicant = Query()
        location_filter = Lokation.build_location_filter(
            search_parameters.location_keyword, search_parameters.location_radius
        )
        test_location = (
            lambda location: search_parameters.location_keyword is not None
            and location_filter(Lokation(**location))
        )
        subquery = _applicant.lokation.exists() & _applicant.lokation.test(
            test_location
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    return query


def build_detailed_search_query(
    search_parameters: ExtendedDetailedSearchParameters,
) -> Optional[QueryInstance]:
    query: Optional[QueryInstance] = None

    if search_parameters.job_title is not None:
        logger.info(f"Searching for job title: {search_parameters.job_title}")
        _applicant = Query()
        subquery = search_re_keyword(
            _applicant.freierTitelStellengesuch, search_parameters.job_title
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.location is not None:
        logger.info(f"Searching for location: {search_parameters.location}")
        _applicant = Query()
        subquery = _applicant.lokationen.any(
            search_re_keyword(Query().ort, search_parameters.location)
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.min_avg_job_position_years is not None:
        logger.info(
            f"Searching for min_avg_job_position_years: {search_parameters.min_avg_job_position_years}"
        )
        _applicant = Query()

        # todo: make this into BerufsfeldErfahung objects
        def avg_duration_check(applicantExperience) -> bool:
            avg_job_position_years = 0

            if applicantExperience is not None:
                job_position_time_list = [
                    TimePeriod(x["erfahrung"]).get_time()
                    for x in applicantExperience
                    if x["erfahrung"] is not None
                ]

                if len(job_position_time_list) > 0:
                    avg_job_position_time = sum(job_position_time_list) / len(
                        job_position_time_list
                    )
                    avg_job_position_years = int(avg_job_position_time / 365.25)

            return (
                avg_job_position_years >= search_parameters.min_avg_job_position_years
            )

        subquery = (
            _applicant.erfahrung.exists()
            & _applicant.erfahrung.berufsfeldErfahrung.exists()
            & _applicant.erfahrung.berufsfeldErfahrung.test(avg_duration_check)
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.min_work_experience_years is not None:
        logger.info(
            f"Searching for min_work_experience_years: {search_parameters.min_work_experience_years}"
        )
        _applicant = Query()
        experience_duration_check = (
            lambda x: TimePeriod(x).get_years()
            >= search_parameters.min_work_experience_years
        )

        subquery = (
            _applicant.erfahrung.exists()
            & _applicant.erfahrung.gesamterfahrung.exists()
            & _applicant.erfahrung.gesamterfahrung.test(experience_duration_check)
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.max_sabbatical_time_years is not None:
        logger.info(
            f"Searching for max_sabbatical_time_years: {search_parameters.max_sabbatical_time_years}"
        )
        _applicant = Query()

        def max_sabbatical_time_check(werdegang: list[LebenslaufElement]) -> bool:

            if werdegang is not None:
                sabbatical_time = timedelta(0)
                last_stop = -1

                for lebenslauf_element_dict in werdegang:
                    lebenslauf_element = LebenslaufElement(**lebenslauf_element_dict)
                    start_date = lebenslauf_element.von

                    if start_date is None or last_stop is None:
                        return False

                    if last_stop != -1:
                        sabbatical_time += last_stop - start_date

                    last_stop = lebenslauf_element.bis

                return (
                    sabbatical_time.days / 365.25
                ) <= search_parameters.max_sabbatical_time_years

        subquery = _applicant.werdegang.exists() & _applicant.werdegang.test(
            max_sabbatical_time_check
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.job_keywords:
        logger.info(f"Searching for job keywords: {search_parameters.job_keywords}")
        # Search over "werdegang", "berufe", and "erfahrung"
        for keyword in search_parameters.job_keywords:
            _applicant = Query()
            _job_title = Query()
            _experience = Query()
            _career = Query()
            # The field berufe, and erfahrung do not seem to always match with the field erfahrung.
            # It seems like the field berufe has pre-defined values.
            subquery = (
                _applicant.berufe.exists()
                & _applicant.berufe.test(
                    lambda berufe: any(
                        [search_re_keyword(beruf, keyword) for beruf in berufe]
                    )
                )
                | (
                    _applicant.erfahrung.exists()
                    & _applicant.erfahrung.berufsfeldErfahrung.exists()
                    & _applicant.erfahrung.berufsfeldErfahrung.any(
                        (search_re_keyword(_experience.berufsfeld, keyword))
                    )
                )
                | (
                    _applicant.werdegang.exists()
                    & _applicant.werdegang.any(
                        search_re_keyword(_career.berufsbezeichnung, keyword)
                        | search_re_keyword(_career.beschreibung, keyword)
                    )
                )
            )

            if query is None:
                query = subquery
            else:
                query &= subquery

    if search_parameters.education_keyword is not None:
        logger.info(
            f"Searching for education keyword: {search_parameters.education_keyword}"
        )
        _applicant = Query()

        subquery = _applicant.bildung.exists() & (
            _applicant.bildung.any(
                search_re_keyword(Query().ort, search_parameters.education_keyword)
            )
            | _applicant.bildung.any(
                search_re_keyword(Query().land, search_parameters.education_keyword)
            )
            | _applicant.bildung.any(
                search_re_keyword(
                    Query().lebenslaufart, search_parameters.education_keyword
                )
            )
            | _applicant.bildung.any(
                search_re_keyword(
                    Query().berufsbezeichnung, search_parameters.education_keyword
                )
            )
            | _applicant.bildung.any(
                search_re_keyword(
                    Query().beschreibung, search_parameters.education_keyword
                )
            )
            | _applicant.bildung.any(
                search_re_keyword(
                    Query().lebenslaufartenKategorie,
                    search_parameters.education_keyword,
                )
            )
            | _applicant.bildung.any(
                search_re_keyword(
                    Query().nameArtEinrichtung, search_parameters.education_keyword
                )
            )
            | _applicant.bildung.any(
                search_re_keyword(
                    Query().schulAbschluss, search_parameters.education_keyword
                )
            )
            | _applicant.bildung.any(
                search_re_keyword(Query().schulart, search_parameters.education_keyword)
            )
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    if search_parameters.skills:
        logger.info(f"Searching for skills: {search_parameters.skills}")
        # todo: does skills mean kenntnisse or softskills? Search both for now
        _applicant = Query()

        for skill_keyword in search_parameters.skills:
            skill_test = lambda skills: skills is not None and any(
                [re.match(skill_keyword, skill) for skill in skills]
            )
            subquery = (
                _applicant.kenntnisse.Expertenkenntnisse.test(skill_test)
                | _applicant.kenntnisse.ErweiterteKenntnisse.test(skill_test)
                | _applicant.kenntnisse.Grundkenntnisse.test(skill_test)
                | _applicant.softskills.test(skill_test)
            )

            if query is None:
                query = subquery
            else:
                query &= subquery

    if search_parameters.languages:
        logger.info(f"Searching for languages: {search_parameters.languages}")
        _applicant = Query()

        subquery = (
            _applicant.sprachkenntnisse.Expertenkenntnisse.any(
                search_parameters.languages
            )
            | _applicant.sprachkenntnisse.ErweiterteKenntnisse.any(
                search_parameters.languages
            )
            | _applicant.sprachkenntnisse.Grundkenntnisse.any(
                search_parameters.languages
            )
        )

        if query is None:
            query = subquery
        else:
            query &= subquery

    logger.info(f"Query: {query}")

    return query


def build_knowledge_search_query(job_description: Text) -> Callable[[Text], bool]:
    """
    Build a query to search for knowledge in the knowledge base.
    """
    return lambda knowledge: str(knowledge).lower() in job_description.lower()
