from typing import Optional
from tinydb import Query
from tinydb.queries import QueryInstance
from src.applicants.schemas.arbeitsagentur.enums import WorkingTime

from src.applicants.schemas.arbeitsagentur.schemas import TimePeriod
from src.applicants.schemas.extended.request import ExtendedSearchParameters


def build_search_query(search_parameters: ExtendedSearchParameters) -> Optional[QueryInstance]:
  query: Optional[QueryInstance] = None

  if search_parameters.keywords is not None and search_parameters.keywords != []:
    for keyword in search_parameters.keywords:
      _applicant = Query()
      subquery = _applicant.refnr.search(keyword) \
                  | _applicant.freierTitelStellengesuch.search(keyword) \
                  | _applicant.berufe.search(keyword) \
                  | _applicant.letzteTaetigkeit.bezeichnung.search(keyword) \
                  | _applicant.erfahrung.berufsfeldErfahrung.any(Query().berufsfeld.search(keyword)) \
                  | _applicant.ausbildungen.any(Query().art.search(keyword))

      if query is None:
        query = subquery
      else:
        query &= subquery

  if search_parameters.max_graduation_year is not None:
    _applicant = Query()
    _education = Query()
    subquery = _applicant.ausbildungen.exists()  \
                & _applicant.ausbildungen.any(
                    (_education.jahr <= search_parameters.max_graduation_year)
                )

    if query is None:
      query = subquery
    else:
      query &= subquery

  if search_parameters.min_work_experience_years is not None:
    _applicant = Query()
    experience_duration_check= lambda x: TimePeriod(x).get_years() >= search_parameters.min_work_experience_years

    subquery = _applicant.erfahrung.exists() \
                & _applicant.erfahrung.gesamterfahrung.exists() \
                & _applicant.erfahrung.gesamterfahrung.test(experience_duration_check)

    if query is None:
      query = subquery
    else:
      query &= subquery

  if search_parameters.career_field is not None:
    _applicant = Query()
    _experience = Query()
    subquery = _applicant.erfahrung.exists() \
                & _applicant.erfahrung.berufsfeldErfahrung.exists() \
                & _applicant.erfahrung.berufsfeldErfahrung.any(
                    (_experience.berufsfeld.search(search_parameters.career_field))
                )

    if query is None:
      query = subquery
    else:
      query &= subquery

  if search_parameters.working_time is not None and search_parameters.working_time != WorkingTime.UNDEFINED:
    _applicant = Query()
    subquery = _applicant.arbeitszeitModelle.any(search_parameters.working_time.value)

    if query is None:
      query = subquery
    else:
      query &= subquery

    if search_parameters.location_keyword is not None:
      _applicant = Query()
      subquery = _applicant.lokation.any(Query().ort.search(search_parameters.location_keyword))

      if query is None:
        query = subquery
      else:
        query &= subquery

  return query