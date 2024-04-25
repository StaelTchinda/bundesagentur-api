from enum import Enum
from typing import Any, Dict, List, Optional, Text
from datetime import datetime, date
from dataclasses import dataclass

from click import Option
from pydantic import BaseModel

from src.arbeitsagentur.models.enums import WorkingTime, JobType

# TODO: better represent optional fields

class BerufsfeldErfahrung(BaseModel):
    berufsfeld: Text
    erfahrung: Text  # This appears to be in an ISO 8601 duration format

class Erfahrung(BaseModel):
    berufsfeldErfahrung: Optional[List[BerufsfeldErfahrung]] = None
    gesamterfahrung: Optional[Text] = None  # ISO 8601 duration format

class LetzteTaetigkeit(BaseModel):
    jahr: Optional[int] = None# TODO: Add validation for year
    bezeichnung: Text
    aktuell: bool

class Ausbildung(BaseModel):
    jahr: int
    art: Text

class Lokation(BaseModel):
    ort: Optional[Text] = None
    plz: Optional[int] = None
    umkreis: Optional[int] = None
    region: Optional[Text] = None
    land: Text

class Bewerber(BaseModel):
    refnr: Text
    verfuegbarkeitVon: date  # ISO 8601 date format
    aktualisierungsdatum: datetime  # ISO 8601 date-time format
    veroeffentlichungsdatum: date  # ISO 8601 date format
    stellenart: JobType
    arbeitszeitModelle: List[WorkingTime]
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
