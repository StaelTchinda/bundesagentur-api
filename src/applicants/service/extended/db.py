import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Text, Union
from tinydb import TinyDB, Query

from tinydb.queries import QueryLike
from tinydb.table import Document

from src.applicants.schemas.arbeitsagentur.enums import *
from src.applicants.schemas.arbeitsagentur.schemas import BewerberUebersicht, BewerberDetail


PathLike = Union[Path, Text]

class DetailedApplicantsDb:
    def __init__(self, db_path: PathLike = "data/db/applicants_detail.json"):
        self.db = TinyDB(db_path)

    def insert(self, applicant: BewerberDetail):
        query = Query()
        if self.db.contains(query.refnr == applicant.refnr):
            raise ValueError(f"Document with refnr {applicant.refnr} already exists.")
        applicant_serializable_dict = self._serialize_object_(applicant)
        self.db.insert(applicant_serializable_dict)

    def get(self, query: QueryLike) -> List[BewerberDetail]:
        docs: List[Document] = self.db.search(query)
        applicants: List[BewerberDetail] = [self._unserealize_object_(doc) for doc in docs]
        return applicants
    
    def get_by_refnr(self, refnr: Text) -> Optional[BewerberDetail]:
        doc: Optional[Document | List[Document]] = self.db.get(Query().refnr == refnr)
        if doc is None:
            return None
        elif isinstance(doc, list):
            return self._unserealize_object_(doc[0])
        return self._unserealize_object_(doc)

    def _serialize_object_(self, applicant: BewerberDetail) -> Dict:
        applicant_json = json.dumps(applicant.__dict__, default=default_json_dumps)
        applicant_serializable_dict = json.loads(applicant_json)
        return applicant_serializable_dict
    
    def _unserealize_object_(self, applicant_dict: Dict) -> BewerberDetail:
        return BewerberDetail(**applicant_dict)
    
    def upsert(self, applicant: BewerberDetail):
        query = Query()
        if self.db.contains(query.refnr == applicant.refnr):
            serializable_dict = self._serialize_object_(applicant)
            self.db.upsert(serializable_dict, Query().refnr == applicant.refnr)
        else:
            self.insert(applicant)

    def get_all(self) -> List[BewerberDetail]:
        docs: List[Document] = self.db.all()
        applicants: List[BewerberDetail] = [self._unserealize_object_(doc) for doc in docs]
        return applicants


class SearchedApplicantsDb:
    def __init__(self, db_path: PathLike = "data/db/applicants.json"):
        self.db = TinyDB(db_path)

    def insert(self, applicant: BewerberUebersicht):
        query = Query()
        if self.db.contains(query.refnr == applicant.refnr):
            raise ValueError(f"Document with refnr {applicant.refnr} already exists.")
        applicant_serializable_dict = self._serialize_object_(applicant)
        self.db.insert(applicant_serializable_dict)

    def get_by_refnr(self, refnr: Text) -> Optional[BewerberUebersicht]:
        doc: Optional[Document | List[Document]] = self.db.get(Query().refnr == refnr)
        if doc is None:
            return None
        elif isinstance(doc, list):
            return BewerberUebersicht(**doc[0])
        return BewerberUebersicht(**doc)
    
    def get_by_refnrs(self, refnrs: List[Text]) -> List[BewerberUebersicht]:
        docs: List[Document] = self.db.search(Query().refnr.test(lambda x: x in refnrs))
        applicants: List[BewerberUebersicht] = [self._unserealize_object_(doc) for doc in docs]
        return applicants

    def get(self, query: QueryLike) -> List[BewerberUebersicht]:
        docs: List[Document] = self.db.search(query)
        applicants: List[BewerberUebersicht] = [self._unserealize_object_(doc) for doc in docs]
        return applicants

    def get_all(self) -> List[BewerberUebersicht]:
        docs: List[Document] = self.db.all()
        applicants: List[BewerberUebersicht] = [self._unserealize_object_(doc) for doc in docs]
        return applicants

    def update(self, query: QueryLike, data) -> None:
        self.db.update(data, query)

    def upsert(self, applicant: BewerberUebersicht) -> None:
        query = Query()
        if self.db.contains(query.refnr == applicant.refnr):
            serializable_dict = self._serialize_object_(applicant)
            self.db.upsert(serializable_dict, Query().refnr == applicant.refnr)
        else:
            self.insert(applicant)

    def remove(self, query: QueryLike) -> None:
        self.db.remove(query)

    def remove_all(self) -> None:
        self.db.purge()

    def close(self) -> None:
        self.db.close()

    def __del__(self) -> None:
        self.db.close()

    def _serialize_object_(self, applicant: BewerberUebersicht) -> Dict:
        applicant_json = json.dumps(applicant.__dict__, default=default_json_dumps)
        applicant_serializable_dict = json.loads(applicant_json)
        return applicant_serializable_dict
    
    def _unserealize_object_(self, applicant_dict: Dict) -> BewerberUebersicht:
        return BewerberUebersicht(**applicant_dict)


def default_json_dumps(obj: Any):
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return str(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)