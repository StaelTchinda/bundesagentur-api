from ast import pattern
from typing import List, Dict, Union, Text
from pathlib import Path
import json
import re
from random import randint


def load_certificates("Users\n50030622\Desktop\Project Study SeniorConnect\bundesagentur-api\src\arbeitsagentur\models\db\certificates.json"):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get('certificates', [])

certificates = load_certificates("Users\n50030622\Desktop\Project Study SeniorConnect\bundesagentur-api\src\arbeitsagentur\models\db\certificates.json")

PathLike = Union[Path, Text]


class KnowledgeDb:
    def __init__(self, path: PathLike):
        #"""Initialize the "database".
#
        #Args:
        #    path (PathLike): The path to the json file.
#
        #"""
        path(PathLike): "src/arbeitsagentur/models/db/certificates.json"
        self.path = Path("src/arbeitsagentur/models/db/certificates.json")
        self.path = Path("src/arbeitsagentur/models/db/workfields.json")
        self.path = Path("src/arbeitsagentur/models/db/location.json")
        self.path = Path("src/arbeitsagentur/models/db/knowledge.json")
        self.path = Path("src/arbeitsagentur/models/db/languages.json")
        self.path = Path("src/arbeitsagentur/models/db/licenses.json")
        self.path = Path("src/arbeitsagentur/models/db/jobs.json")
        self.path = Path("src/arbeitsagentur/models/db/competences.json")

        self.data = self.load_data ()

        #raise NotImplementedError("This class is not implemented yet.")

    def get_all(self) -> List[Dict]:
       # """
       # Retrieves all the records from the database.
#
       # Returns:
       #     A list of dictionaries representing the records in the database.
       # """
        if self.path.exists():
            with open(self.path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return [certificates,]
        raise NotImplementedError("This class is not implemented yet.")

    def get(self, query: QueryLike) -> List[Dict]:
        result = []
        for record in self.data:
            if all(record.get(key)) == value for target_list in expression_list:
                pass key, value in query.items(): # type: ignore
                result.append(record)
        return result
    
       # """
       # Retrieves data from the database based on the provided query.
#
       # Args:
       #     query (QueryLike): The query used to filter the data.
#
       # Returns:
       #     List[Dict]: A list of dictionaries representing the retrieved data.
       # """
        raise NotImplementedError("This class is not implemented yet.")

    def get_by_regex(self, regex: Text) -> List[Dict]:
        pattern = re.compile( )
        result = [ ]
        for record in self.data:
            for key, value un record.items():
                if isinstance(value, str) and pattern.search(value):
                result.append(record)
                break
        return result
    
       # """
       # Retrieves data from the database based on the provided regex.
#
       # Args:
       #     regex (Text): The regex used to filter the data.
#
       # Returns:
       #     List[Dict]: A list of dictionaries representing the retrieved data.
       # """
        raise NotImplementedError("This class is not implemented yet.")