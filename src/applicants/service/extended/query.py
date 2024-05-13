from datetime import datetime, timedelta
from typing import Optional
from tinydb import Query
from tinydb.queries import QueryInstance
from src.applicants.schemas.arbeitsagentur.enums import WorkingTime

from src.applicants.schemas.arbeitsagentur.schemas import LebenslaufElement, TimePeriod
from src.applicants.schemas.extended.request import ExtendedSearchParameters, ExtendedDetailedSearchParameters


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


def build_detailed_search_query(search_parameters : ExtendedDetailedSearchParameters) -> Optional[QueryInstance]:
    query : Optional[QueryInstance] = None

    if search_parameters.job_title is not None:
      _applicant = Query()
      subquery = _applicant.freierTitelStellengesuch.search(search_parameters.job_title)

      if query is None:
        query = subquery
      else:
        query &= subquery

    if search_parameters.location is not None:
      _applicant = Query()
      subquery = _applicant.lokationen.any(Query().ort.search(search_parameters.location))

      if query is None:
        query = subquery
      else:
        query &= subquery

    if search_parameters.min_avg_job_position_years is not None:
      _applicant = Query()

      #todo: make this into BerufsfeldErfahung objects
      def avg_duration_check(applicantExperience) -> bool:
        avg_job_position_years = 0

        if applicantExperience is not None:
          job_position_time_list = [TimePeriod(x["erfahrung"]).get_time() for x in applicantExperience if x["erfahrung"] is not None]

          if(len(job_position_time_list) > 0):
            avg_job_position_time = sum(job_position_time_list)/len(job_position_time_list)
            avg_job_position_years = int(avg_job_position_time/365.25)

        return (avg_job_position_years >= search_parameters.min_avg_job_position_years)

      subquery = _applicant.erfahrung.exists() \
                  & _applicant.erfahrung.berufsfeldErfahrung.exists() \
                  & _applicant.erfahrung.berufsfeldErfahrung.test(avg_duration_check)

      if query is None:
        query = subquery
      else:
        query &= subquery

    if search_parameters.min_work_experience_years is not None:
      _applicant = Query()
      experience_duration_check = lambda x : TimePeriod(x).get_years() >= search_parameters.min_work_experience_years

      subquery = _applicant.erfahrung.exists() \
                  & _applicant.erfahrung.gesamterfahrung.exists() \
                  & _applicant.erfahrung.gesamterfahrung.test(experience_duration_check)
      
      if query is None:
        query = subquery
      else:
        query &= subquery

    if search_parameters.max_sabbatical_time_years is not None:
      _applicant = Query()

      def max_sabbatical_time_check(werdegang : list[LebenslaufElement]) -> bool:

        if(werdegang is not None):
          sabbatical_time = timedelta(0)
          last_stop = -1

          for lebenslauf_element_dict in werdegang:
            lebenslauf_element = LebenslaufElement(**lebenslauf_element_dict)
            start_date = lebenslauf_element.von

            if(start_date is None or last_stop is None):
              return False
            
            if(last_stop != -1):
              sabbatical_time += (last_stop - start_date)
            
            last_stop = lebenslauf_element.bis

          return (sabbatical_time.days/365.25) <= search_parameters.max_sabbatical_time_years

      subquery = _applicant.werdegang.exists() \
                  & _applicant.werdegang.test(max_sabbatical_time_check)

      if query is None:
        query = subquery
      else:
        query &= subquery

    if(search_parameters.job_titles):
      _applicant = Query()

      subquery = _applicant.berufe.exists() \
                  & _applicant.berufe.any(search_parameters.job_titles)
      
      if query is None:
        query = subquery
      else:
        query &= subquery

    if(search_parameters.job_descriptions):
      _applicant = Query()

      subquery = _applicant.werdegang.exists() \
                  & _applicant.werdegang.any(Query().berufsbezeichnung.one_of(search_parameters.job_descriptions))
      
      if query is None:
        query = subquery
      else:
        query &= subquery

    if(search_parameters.education_keyword is not None):
      _applicant = Query()

      subquery = _applicant.bildung.exists() \
                  & _applicant.bildung.any(Query().ort.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().land.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().lebenslaufart.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().berufsbezeichnung.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().beschreibung.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().lebenslaufartenKategorie.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().nameArtEinrichtung.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().schulAbschluss.search(search_parameters.education_keyword)) \
                  & _applicant.bildung.any(Query().schulart.search(search_parameters.education_keyword))
      
      if query is None:
        query = subquery
      else:
        query &= subquery

    if(search_parameters.skills):
      #todo: does skills mean kenntnisse or softskills? Search both for now
      _applicant = Query()

      subquery = _applicant.kenntnisse.Expertenkenntnisse.any(search_parameters.skills) \
                  | _applicant.kenntnisse.ErweiterteKenntnisse.any(search_parameters.skills) \
                  | _applicant.kenntnisse.Grundkenntnisse.any(search_parameters.skills) \
                  | _applicant.softskills.any(search_parameters.skills)
      
      if query is None:
        query = subquery
      else:
        query &= subquery

    if(search_parameters.languages):
      _applicant = Query()

      subquery =  _applicant.sprachkenntnisse.Expertenkenntnisse.any(search_parameters.languages) \
                  | _applicant.sprachkenntnisse.ErweiterteKenntnisse.any(search_parameters.languages) \
                  | _applicant.sprachkenntnisse.Grundkenntnisse.any(search_parameters.languages)
      
      if query is None:
        query = subquery
      else:
        query &= subquery


    return query