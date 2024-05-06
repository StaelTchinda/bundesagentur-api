from typing import List, Dict, Union, Text
from pathlib import Path
from tinydb import Query, TinyDB
from tinydb.queries import QueryLike



PathLike = Union[Path, Text]


class KnowledgeBaseDb:

    def __init__(self, db_basepath: PathLike):
        """
        Initialize the "database".
        Args: path (PathLike): The path to the json file.
        """
        self.db = TinyDB(db_basepath)


    def get_all(self) -> List[Text]: 
        """
        Retrieves all the records from the database.
        Returns:
            A list of dictionaries representing the records in the database.
        """
        results = self.db.all()
        return results

    
    def get(self, query: QueryLike) -> List[Dict]:
        """
        Retrieves data from the database based on the provided query.
        Args:
            query (QueryLike): The query used to filter the data.
        Returns:
            List[Dict]: A list of dictionaries representing the retrieved data.
        """
        results = self.db.search(query)
        return results

    
    def get_by_regex(self, regex: Text) -> List[Dict]:
        """
        Retrieves data from the database based on the provided regex.
        Args:
            regex (Text): The regex used to filter the data.
        Returns:
            List[Dict]: A list of dictionaries representing the retrieved data.
        """
        return self.get(Query().search(regex))
    

class CertificatesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/certificates.json"):
        super.__init__(db_basepath)

class CompetencesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/competences.json"):
        super.__init__(db_basepath)

class JobsDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/jobs.json"):
        super.__init__(db_basepath)

class SkillsDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/skills.json"):
        super.__init__(db_basepath)

class LanguagesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/languages.json"):
        super.__init__(db_basepath)

class LicencesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/licences.json"):
        super.__init__(db_basepath)

class LocationDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/location.json"):
        super.__init__(db_basepath)

class WorkfieldsDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/workfields.json"):
        super.__init__(db_basepath)
