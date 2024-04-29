import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Text, Union
from tinydb import TinyDB, Query

from tinydb.queries import QueryLike
from tinydb.table import Document

from src.arbeitsagentur.models.enums import *
from src.arbeitsagentur.models.response import Bewerber


PathLike = Union[Path, Text]


class SearchedApplicantsDb:
    def __init__(self, db_path: PathLike = "data/db/applicants.json"):
        self.db = TinyDB(db_path)

    def insert(self, applicant: Bewerber):
        query = Query()
        if self.db.contains(query.refnr == applicant.refnr):
            raise ValueError(f"Document with refnr {applicant.refnr} already exists.")
        applicant_serializable_dict = self._serialize_object_(applicant)
        self.db.insert(applicant_serializable_dict)

    def get_by_refnr(self, refnr: Text) -> Optional[Bewerber]:
        doc: Optional[Document | List[Document]] = self.db.get(Query().refnr == refnr)
        if doc is None:
            return None
        elif isinstance(doc, list):
            return Bewerber(**doc[0])
        return Bewerber(**doc)

    def get(self, query: QueryLike):
        return self.db.search(query)

    def get_all(self):
        results = self.db.all()
        return [self._unserealize_object_(result) for result in results]

    def update(self, query: QueryLike, data):
        self.db.update(data, query)

    def upsert(self, applicant: Bewerber):
        query = Query()
        if self.db.contains(query.refnr == applicant.refnr):
            serializable_dict = self._serialize_object_(applicant)
            self.db.upsert(serializable_dict, Query().refnr == applicant.refnr)
        else:
            self.insert(applicant)

    def remove(self, query: QueryLike):
        self.db.remove(query)

    def remove_all(self):
        self.db.purge()

    def close(self):
        self.db.close()

    def __del__(self):
        self.db.close()

    def _serialize_object_(self, applicant: Bewerber) -> Dict:
        def default_json_dumps(obj: Any):
            if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
                return str(obj)
            elif isinstance(obj, Enum):
                return obj.value
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            return str(obj)
        applicant_json = json.dumps(applicant.__dict__, default=default_json_dumps)
        applicant_serializable_dict = json.loads(applicant_json)
        return applicant_serializable_dict
    
    def _unserealize_object_(self, applicant_dict: Dict) -> Bewerber:
        return Bewerber(**applicant_dict)


class LocalSearchParameters:
    searchKeyword: Union[Text, None]
    educationType: Union[EducationType, None]
    locationKeyword: Union[Text, None]
    locationRadius: Union[LocationRadius, None]
    offerType: Union[OfferType, None]
    workingTime: Union[WorkingTime, None]
    workExperience: Union[WorkExperience, None]
    contractType: Union[ContractType, None]
    disability: Union[Disability, None]
    page: Union[int, None]
    size: Union[int, None]