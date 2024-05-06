from ast import pattern
from typing import List, Dict, Union, Text
from pathlib import Path
import json
import re
from random import randint
from tinydb import TinyDB
from tinydb.queries import QueryLike



PathLike = Union[Path, Text]

class KnowledgeDb:
    def __init__(self, db_basepath: PathLike = "data/knowledge_base/"):
        self.certificates_db = TinyDB("{}certificates.json".format(db_basepath))
        self.workfields_db = TinyDB("{}workfields.json".format(db_basepath))
        self.location_db = TinyDB("{}location.json".format(db_basepath))
        self.knowledge_db = TinyDB("{}knowledge.json".format(db_basepath))
        self.languages_db = TinyDB("{}languages.json".format(db_basepath))
        self.licenses_db = TinyDB("{}licenses.json".format(db_basepath))
        self.jobs_db = TinyDB("{}jobs.json".format(db_basepath))
        self.competences_db = TinyDB("{}competences.json".format(db_basepath))

        self.dblist: List[TinyDB] = [
            self.certificates_db,
            self.workfields_db,
            self.location_db,
            self.knowledge_db,
            self.languages_db,
            self.licenses_db,
            self.jobs_db,
            self.competences_db
        ]

    """
    Initialize the "database".

    Args: path (PathLike): The path to the json file.
    """

    def get_all(self) -> List[Dict]: 
        resultlist = []
        for db in self.dblist:
            results = db.all()
            resultlist.extend([self._unserealize_object_(result) for result in results]) #use .append or .extend in these cases? 
        return resultlist
    """
    Retrieves all the records from the database.
    Returns:
        A list of dictionaries representing the records in the database.
    """

    
    def get(self, query: QueryLike) -> List[Dict]:
        querylist = []
        for db in self.dblist:
            results = db.search()
            querylist.extend(self._unserealize_object(result) for result in results) # use .append or .extend? #does the argument have to be in suqare brackets?
        return querylist

    """
    Retrieves data from the database based on the provided query.
    Args:
        query (QueryLike): The query used to filter the data.
    Returns:
        List[Dict]: A list of dictionaries representing the retrieved data.
    """

    
    def get_by_regex(self, regex: Text) -> List[Dict]:
        regexlist = []
        pattern = re.compile(regex)
        for db in self.dblist:
            for entry in db.all():
                if any(pattern.search(str(value)) for value in entry.values()):
                    regexlist.extend(entry) # use .append or .extend?
        return regexlist
    
    """
    Retrieves data from the database based on the provided regex.
    Args:
        regex (Text): The regex used to filter the data.
    Returns:
        List[Dict]: A list of dictionaries representing the retrieved data.
    """


#certificates = load_certificates("Users\n50030622\Desktop\Project Study SeniorConnect\bundesagentur-api\src\arbeitsagentur\models\db\certificates.json")