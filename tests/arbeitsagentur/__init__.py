# from typing import List, Text
# import logging


# from src.applicants.router.extended import search_applicants
# from src.applicants.schemas.arbeitsagentur.enums import WorkingTime
# from src.applicants.schemas.arbeitsagentur.schemas import TimePeriod
# from src.applicants.service.extended.db import SearchedApplicantsDb
# from src.configs import DEFAULT_LOGGING_CONFIG


# logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
# logger = logging.getLogger(__name__)

# def native_filter(
#     maxGraduationYear : int | None = None,
#     minWorkExperienceYears : int | None = None,
#     careerField : Text | None = None,
#     workingTime: WorkingTime = WorkingTime.UNDEFINED,
#     locationKeyword: Text | None = None,
# ):  
#     logger.info(f"Filtering candidates with the following parameters: {maxGraduationYear}, {minWorkExperienceYears}, {careerField}, {workingTime}, {locationKeyword}")
#     db = SearchedApplicantsDb()

#     candidates = db.get_all()

#     logger.info(f"Found in total {len(candidates)} candidates")
    
#     maxGraduationYear = maxGraduationYear

#     indices_to_remove: List[int] = []

#     for i, candidate in enumerate(candidates):
#         if maxGraduationYear is not None:
#             #remove candidates that don't match graduationYear
#             logger.info(f"Checking candidate {candidate.refnr} for maxGraduationYear")
#             match = False
#             if candidate.ausbildungen is not None:
#                 for education in candidate.ausbildungen:
#                     if education.jahr <= maxGraduationYear:
#                         match = True
#                         break

#             if not match:
#                 logger.info(f"Removing candidate {candidate.refnr}")
#                 indices_to_remove.append(i)
#                 continue

#         if minWorkExperienceYears is not None:
#             #remove candidates that don't match minWorkExperienceDays
#             logger.info(f"Checking candidate {candidate.refnr} for minWorkExperienceYears: {minWorkExperienceYears}, {candidate.erfahrung}")
#             match = False
#             if candidate.erfahrung is not None and candidate.erfahrung.gesamterfahrung is not None:
#                 experience_period = TimePeriod(candidate.erfahrung.gesamterfahrung)
#                 if experience_period.get_years() >= minWorkExperienceYears:
#                     match = True

#             if(not match):
#                 logger.info(f"Removing candidate {candidate.refnr}")
#                 indices_to_remove.append(i)
#                 continue

#         if careerField is not None:
#             #remove candidates that don't match careerField
#             logger.info(f"Checking candidate {candidate.refnr} for careerField")
#             match = False
#             if candidate.erfahrung is not None and candidate.erfahrung.berufsfeldErfahrung is not None:
#                 for work_field in candidate.erfahrung.berufsfeldErfahrung:
#                     if careerField in work_field.berufsfeld:
#                         match = True
#                         break

#             if(not match):
#                 logger.info(f"Removing candidate {candidate.refnr}")
#                 indices_to_remove.append(i)
#                 continue

#         if workingTime is not None and workingTime != WorkingTime.UNDEFINED:
#             logger.info(f"Checking candidate {candidate.refnr} for workingTime")
#             #remove candidates that don't match workingTime
#             match = False
#             if candidate.arbeitszeitModelle is not None:
#                 for work_time in candidate.arbeitszeitModelle:
#                     if(work_time == workingTime):
#                         match = True
#                         break

#             if(not match):
#                 logger.info(f"Removing candidate {candidate.refnr}")
#                 indices_to_remove.append(i)
#                 continue

#         if locationKeyword is not None:
#             logger.info(f"Checking candidate {candidate.refnr} for locationKeyword")
#             #remove candidates that don't match locationKeyword
#             match = False
#             if candidate.lokation is not None:
#                 if candidate.lokation.check_location(locationKeyword):
#                     match = True

#             if(not match):
#                 logger.info(f"Removing candidate {candidate.refnr}")
#                 indices_to_remove.append(i)
#                 continue
    
#     logger.info(f"Removing {len(indices_to_remove)} candidates")
#     for i in sorted(indices_to_remove, reverse=True):
#         del candidates[i]

#     logger.info(f"Found {len(candidates)} candidates that match the criteria")

#     return candidates



# def test_local_search():
#     max_graduation_year = 2015
#     min_work_experience_years = 5
#     career_field = "Software"
#     working_time = WorkingTime.FULL_TIME
#     location_keyword = "Berlin"

#     expected_candidates = native_filter(
#         max_graduation_year,
#         min_work_experience_years,
#         career_field,
#         working_time,
#         location_keyword
#     )

    

#     candidates = search_applicants(
#         None,
#         max_graduation_year,
#         min_work_experience_years,
#         career_field,
#         working_time,
#         location_keyword
#     )

#     assert candidates == expected_candidates


# if __name__ == "__main__":
#     test_local_search()
