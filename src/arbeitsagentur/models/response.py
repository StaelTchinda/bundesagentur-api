from enum import Enum
import re
from typing import Any, Dict, List, Optional, Text, Union
from datetime import datetime, date
from dataclasses import dataclass, field

from click import Option
from pydantic import BaseModel, field_validator

from src.arbeitsagentur.models.enums import WorkingTime, JobType

# TODO: better represent optional fields

class TimePeriod(str):
    """ This class is used to represent a time period in the format used by the Arbeitsagentur API.
    It is a string that is in the format PnYnMnD (e.g., P22Y4M23D, P2Y11M23D, P34Y8M24D, etc.)

    Args:
        str (_type_): _description_
    """

    @classmethod
    def _regexp_pattern_(cls) -> str:
        # regex = r'^P(\d+Y)?(\d+M)?(\d+D)?$' # CoPilot
        regex = r"P((\d+)Y)?((\d+)M)?((\d+)D)?" # Jonathan
        return regex
    
    def __new__(cls, value: str):
        if not cls.validate(value):
            raise ValueError(f"Invalid time period format: {value}")
        return str.__new__(cls, value)
    

    @classmethod 
    def validate(cls, value: str) -> bool:
        """This function validates that the input string is a valid time period in the format PnYnMnD.

        Args:
            value (str): The string to validate.

        Returns:
            bool: True if the string is a valid time period, False otherwise.
        """
        reg_exp = cls._regexp_pattern_()
        return re.match(reg_exp, value) is not None
    

    def get_time_dict(self) -> Dict[Text, int]:
        """This function returns the time period as a dictionary.

        Returns:
            Dict[Text, int]: A dictionary with the keys 'years', 'months', and 'days'.
        """
        regex = self._regexp_pattern_() 
        search = re.search(regex, self)
        if search is None:
            raise ValueError(f"Invalid time period format: {self}")
        n_years     = search.group(2)
        n_months    = search.group(4)
        n_days      = search.group(6)
        time_period = {
            'years': 0 if n_years is None else int(n_years),
            'months': 0 if n_months is None else int(n_months),
            'days': 0 if n_days is None else int(n_days)
        }
        return time_period

    def get_years(self) -> int:
        """This function returns the number of years in the time period.

        Returns:
            int: The number of years in the time period.
        """
        return self.get_time_dict()['years']
    
    def get_months(self) -> int:
        """This function returns the number of months in the time period.

        Returns:
            int: The number of months in the time period.
        """
        return self.get_time_dict()['months']
    
    def get_days(self) -> int:
        """This function returns the number of days in the time period.

        Returns:
            int: The number of days in the time period.
        """
        return self.get_time_dict()['days']


    def get_time(self) -> int:
        """This function returns the time period in days.

        Returns:
            int: The time period in days.
        """
        time_period = self.get_time_dict()
        return time_period['years'] * 365 + time_period['months'] * 30 + time_period['days']


    def __lt__(self, value: str) -> bool:
        if not isinstance(value, TimePeriod):
            raise ValueError(f"Cannot compare TimePeriod with {type(value)}")
        return self.get_time() < value.get_time()



class BerufsfeldErfahrung(BaseModel):
    berufsfeld: Text
    erfahrung: Optional[Text] = None  # This appears to be in an ISO 8601 duration format

    @field_validator('erfahrung')
    def validate_berufsfeld(cls, v):
        if v is not None:
            if not TimePeriod.validate(v):
                raise ValueError(f"Invalid time period format: {v}")
        return v

class Erfahrung(BaseModel):
    berufsfeldErfahrung: Optional[List[BerufsfeldErfahrung]] = None
    gesamterfahrung: Optional[Text] = None  # ISO 8601 duration format

    @field_validator('gesamterfahrung')
    def validate_berufsfeld(cls, v):
        if v is not None:
            if not TimePeriod.validate(v):
                raise ValueError(f"Invalid time period format: {v}")
        return v

class LetzteTaetigkeit(BaseModel):
    jahr: Optional[int] = None# TODO: Add validation for year
    bezeichnung: Text
    aktuell: bool

class Ausbildung(BaseModel):
    jahr: int
    art: Text

class Lokation(BaseModel):
    ort: Optional[Text] = None
    plz: Optional[Union[int, Text]] = None
    umkreis: Optional[int] = None
    region: Optional[Text] = None
    land: Optional[Text] = None

class Bewerber(BaseModel):
    refnr: Text
    verfuegbarkeitVon: date  # ISO 8601 date format
    aktualisierungsdatum: datetime  # ISO 8601 date-time format
    veroeffentlichungsdatum: date  # ISO 8601 date format
    stellenart: JobType
    arbeitszeitModelle: Optional[List[WorkingTime]] = None
    berufe: List[Text]
    erfahrung: Optional[Erfahrung] = None
    letzteTaetigkeit: Optional[LetzteTaetigkeit] = None
    ausbildungen: Optional[List[Ausbildung]] = None
    hatEmail: bool
    hatTelefon: bool
    hatAdresse: bool
    lokation: Lokation
    mehrereArbeitsorte: bool
    freierTitelStellengesuch: Optional[Text] = None  # Optional as not all entries have it


class FacettenElement(BaseModel):
    counts: Optional[Dict[Text, int]] = None
    maxCount: int


class Facetten(BaseModel):
    lizenzen: FacettenElement
    reisebereitschaft: FacettenElement
    behinderung: FacettenElement
    berufsfeld: FacettenElement
    arbeitsorte: FacettenElement
    ausbildungsart: FacettenElement
    veroeffentlichtseit: FacettenElement
    erreichbarkeit: FacettenElement
    kenntnisse_grund: FacettenElement
    sprachen_erweitert: FacettenElement
    sprachen_experten: FacettenElement
    berufserfahrung: FacettenElement
    sprachen_grund: FacettenElement
    kenntnisse_experten: FacettenElement
    angebotsart: FacettenElement
    fuehrerscheine: FacettenElement
    arbeitszeit: FacettenElement
    berufe: FacettenElement
    kenntnisse_erweitert: FacettenElement
    topKenntnisse: FacettenElement


class ApplicantSearchResponse(BaseModel):
    bewerber: List[Bewerber]
    maxErgebnisse: int
    page: int
    size: int
    facetten: Facetten
