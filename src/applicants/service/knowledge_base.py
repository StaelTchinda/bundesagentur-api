import json
from re import RegexFlag
import re
from typing import Any, Callable, List, Dict, Optional, Union, Text
from pathlib import Path
from tinydb import Query, TinyDB
from tinydb.queries import QueryLike
from tinydb.table import Document



PathLike = Union[Path, Text]


class KnowledgeBaseDb:
    
    def __init__(self, db_basepath: PathLike, root_element: Text):
        """
        Initialize the "database".
        Args: path (PathLike): The path to the json file.
        """
        data: Dict[Text, Any] = json.loads(open(db_basepath).read())
        self.db: List[Text] = data[root_element]


    def get_all(self) -> List[Text]: 
        """
        Retrieves all the records from the database.
        Returns:
            A list of dictionaries representing the records in the database.
        """
        return self.db


    def get(self, filter: Callable[[Text], bool]) -> List[Text]:
        """
        Retrieves data from the database based on the provided query.
        
        """
        results: List[Text] = [item for item in self.db if filter(item)]
        return results
    
    def get_by_regex(self, pattern: Text, flags: Union[int, RegexFlag] = 0) -> List[Text]:
        """
        Retrieves data from the database based on the provided query.
        
        """
        return self.get(lambda item: re.search(pattern, item, flags) is not None)

    
    

class CertificatesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/certificates.json"):
        super().__init__(db_basepath, "certificates")

class CompetencesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/competences.json"):
        super().__init__(db_basepath, "competences")

class JobsDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/jobs.json"):
        super().__init__(db_basepath, "jobs")

class SkillsDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/skills.json"):
        super().__init__(db_basepath, "skills")

class LanguagesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/languages.json"):
        super().__init__(db_basepath, "languages")

class LicencesDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/licences.json"):
        super().__init__(db_basepath, "licences")

class LocationDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/location.json"):
        super().__init__(db_basepath, "location")

class WorkfieldsDb(KnowledgeBaseDb):
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/workfields.json"):
        super().__init__(db_basepath, "workfields")
