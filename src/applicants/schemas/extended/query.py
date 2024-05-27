import json
import os
from difflib import get_close_matches
from pathlib import Path
from typing import List, Dict, Union, Text

from arbeitsagentur.models.db.knowledge_base import CompetencesDb, JobsDb, KnowledgeBaseDb, LanguagesDb, LicensesDb, LocationDb, SkillsDb, WorkfieldsDb, CertificatesDb

def build_knowledge_search_query(job_description: str) -> dict:
    db = KnowledgeBaseDb()
    
    def find_matches(KnowledgeBaseDb, job_description):
        matches = get_close_matches(job_description, KnowledgeBaseDb, n=1, cutoff=0.5)
        return matches

    certificates = CertificatesDb()
    competences = CompetencesDb()
    jobs = JobsDb()
    languages = LanguagesDb()
    licenses = LicensesDb()
    locations = LocationDb()
    skills = SkillsDb()
    workfields = WorkfieldsDb()

    certificates_matches = find_matches(certificates, job_description)
    competences_matches = find_matches(competences, job_description)
    jobs_matches = find_matches(jobs, job_description)
    languages_matches = find_matches(languages, job_description)
    licenses_matches = find_matches(licenses, job_description)
    locations_matches = find_matches(locations, job_description)
    skills_matches = find_matches(skills, job_description)
    workfields_matches = find_matches(workfields, job_description)

    query = {
        'certificates': certificates_matches,
        'competences': competences_matches,
        'jobs': jobs_matches,
        'languages': languages_matches,
        'licenses': licenses_matches,
        'location': locations_matches,
        'skills': skills_matches,
        'workfields': workfields_matches,

    }

    return query
