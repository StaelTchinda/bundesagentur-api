import logging
from typing import Callable, List, Optional, Union, Text, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, AliasChoices
import re
import json

from pydantic import BaseModel

from src.applicants.schemas.arbeitsagentur.enums import JobType, WorkingTime
from src.utils.location.openplz import Locality, get_localities
from src.utils.location.zip import CountryCode, RadiusLocality, get_localities_in_radius
from src.configs import DEFAULT_LOGGING_CONFIG


logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# TODO: better represent optional fields


class TimePeriod(str):
    """This class is used to represent a time period in the format used by the Arbeitsagentur API.
    It is a string that is in the format PnYnMnD (e.g., P22Y4M23D, P2Y11M23D, P34Y8M24D, etc.)

    Args:
        str (_type_): _description_
    """

    @classmethod
    def _regexp_pattern_(cls) -> str:
        regex = r"P((\d+)Y)?((\d+)M)?((\d+)D)?"  # Jonathan
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
        n_years = search.group(2)
        n_months = search.group(4)
        n_days = search.group(6)
        time_period = {
            "years": 0 if n_years is None else int(n_years),
            "months": 0 if n_months is None else int(n_months),
            "days": 0 if n_days is None else int(n_days),
        }
        return time_period

    def get_years(self) -> int:
        """This function returns the number of years in the time period.

        Returns:
            int: The number of years in the time period.
        """
        return self.get_time_dict()["years"]

    def get_months(self) -> int:
        """This function returns the number of months in the time period.

        Returns:
            int: The number of months in the time period.
        """
        return self.get_time_dict()["months"]

    def get_days(self) -> int:
        """This function returns the number of days in the time period.

        Returns:
            int: The number of days in the time period.
        """
        return self.get_time_dict()["days"]

    def get_time(self) -> int:
        """This function returns the time period in days.

        Returns:
            int: The time period in days.
        """
        time_period = self.get_time_dict()
        return (
            time_period["years"] * 365
            + time_period["months"] * 30
            + time_period["days"]
        )

    @classmethod
    def from_time(cls, time: int) -> str:
        """This function creates a TimePeriod object from a time period in days.

        Args:
            time (int): The time period in days.

        Returns:
            str: The TimePeriod object.
        """
        years: int = time // 365
        time %= 365
        months: int = time // 30
        time %= 30
        days: int = time
        return TimePeriod(f"P{years}Y{months}M{days}D")

    def __lt__(self, value: str) -> bool:
        if not isinstance(value, TimePeriod):
            raise ValueError(f"Cannot compare TimePeriod with {type(value)}")
        return self.get_time() < value.get_time()

    # Create function to sum two TimePeriods
    def __add__(self, value: str) -> str:
        if not isinstance(value, TimePeriod):
            raise ValueError(f"Cannot add TimePeriod with {type(value)}")
        time_period: int = self.get_time() + value.get_time()
        return TimePeriod.from_time(time_period)


class BerufsfeldErfahrung(BaseModel):
    berufsfeld: Text
    erfahrung: Optional[Text] = (
        None  # This appears to be in an ISO 8601 duration format
    )

    @field_validator("erfahrung")
    def validate_berufsfeld(cls, v):
        if v is not None:
            if not TimePeriod.validate(v):
                raise ValueError(f"Invalid time period format: {v}")
        return v


class Erfahrung(BaseModel):
    berufsfeldErfahrung: Optional[List[BerufsfeldErfahrung]] = None
    gesamterfahrung: Optional[Text] = None  # ISO 8601 duration format

    @field_validator("gesamterfahrung")
    def validate_berufsfeld(cls, v):
        if v is not None:
            if not TimePeriod.validate(v):
                raise ValueError(f"Invalid time period format: {v}")
        return v


class LetzteTaetigkeit(BaseModel):
    jahr: Optional[int] = None  # TODO: Add validation for year
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

    @classmethod
    def _map_locality_(cls, locality: Locality) -> "Lokation":
        return Lokation(
            ort=locality.name,
            plz=locality.postalCode,
            region=locality.district.name,
            land=locality.federalState.name,  # TODO: Check if this is the correct value
        )

    @classmethod
    def _map_radius_locality_(cls, radius_locality: RadiusLocality) -> "Lokation":
        return Lokation(
            ort=radius_locality.place_name,
            plz=radius_locality.postal_code,
            region=radius_locality.state,
            land=radius_locality.country_code.value,  # TODO: Check if this is the correct value
        )

    @classmethod
    def get_matching_locations(
        cls, location: Union[Text, int], radius: Optional[int] = None
    ) -> List["Lokation"]:
        if location is None:
            raise ValueError("Location is None")

        main_localities: List[Locality]
        if isinstance(location, int) or (
            isinstance(location, Text) and location.isdigit()
        ):
            main_localities = get_localities(postalCode=int(location))
        else:
            main_localities = get_localities(name=location)

        radius_localities: List[RadiusLocality] = []
        if radius is not None:
            for locality in main_localities:
                radius_localities.extend(
                    get_localities_in_radius(
                        CountryCode.DE, locality.postalCode, radius
                    )
                )

        matching_locations: List[Lokation] = []

        for locality in main_localities:
            matching_locations.append(cls._map_locality_(locality))

        for radius_locality in radius_localities:
            matching_locations.append(cls._map_radius_locality_(radius_locality))

        return matching_locations

    @classmethod
    def _build_basic_location_filter_(
        cls, location: "Lokation", location_keyword: Text
    ) -> bool:
        if location.ort is not None and re.search(
            location_keyword, location.ort, re.IGNORECASE
        ):
            return True
        elif location.plz is not None and re.search(
            location_keyword, str(location.plz), re.IGNORECASE
        ):
            return True
        elif location.region is not None and re.search(
            location_keyword, location.region, re.IGNORECASE
        ):
            return True
        elif location.land is not None and re.search(
            location_keyword, location.land, re.IGNORECASE
        ):
            return True
        else:
            return False

    @classmethod
    def build_location_filter(
        cls, location_keyword: Text, location_radius: Optional[int] = None
    ) -> Callable[["Lokation"], bool]:
        if location_radius is None or location_radius == 0:
            logger.info(f"Filtering by location: {location_keyword}")
            return lambda location: cls._build_basic_location_filter_(
                location, location_keyword
            )
        else:
            logger.info(
                f"Filtering by location: {location_keyword} with radius: {location_radius}"
            )
            matching_locations = cls.get_matching_locations(
                location_keyword, location_radius
            )
            matching_location_orts = set(
                [location.ort for location in matching_locations]
            )
            matching_location_plzs = set(
                [location.plz for location in matching_locations]
            )
            matching_location_regions = set(
                [location.region for location in matching_locations]
            )
            logger.info(
                f"Matching locations: {matching_location_orts}, {matching_location_plzs}, {matching_location_regions}"
            )

            def is_in(location: "Lokation") -> bool:
                if location.ort is not None:
                    return location.ort in matching_location_orts
                elif location.plz is not None:
                    return location.plz in matching_location_plzs
                elif location.region is not None:
                    return location.region in matching_location_regions
                else:
                    return False

            return is_in


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


class LebenslaufElement(BaseModel):
    von: Optional[date] = None
    bis: Optional[date] = None
    ort: Optional[Text] = None
    land: Optional[Text] = None
    lebenslaufart: Text
    berufsbezeichnung: Optional[Text] = None
    beschreibung: Optional[Text] = None
    istAbgeschlossen: Optional[Text] = None
    lebenslaufartenKategorie: Optional[Text] = None
    nameArtEinrichtung: Optional[Text] = None
    schulAbschluss: Optional[Text] = None
    schulart: Optional[Text] = None


class Kenntnisse(BaseModel):
    Expertenkenntnisse: Optional[List[Text]] = Field(
        validation_alias=AliasChoices("Expertenkenntnisse", "Verhandlungssicher"),
        default=None,
    )
    ErweiterteKenntnisse: Optional[List[Text]] = Field(
        validation_alias=AliasChoices("Erweiterte Kenntnisse"), default=None
    )
    Grundkenntnisse: Optional[List[Text]] = None


class Lizenz(BaseModel):
    bezeichnung: Text
    gueltigVon: Optional[Text] = None


class Mobilitaet(BaseModel):
    reisebereitschaft: Optional[Text] = None
    fuehrerscheine: Optional[List[Text]] = None
    fahrzeugVorhanden: Optional[bool] = None


class GenericBewerber(BaseModel):
    refnr: Text
    verfuegbarkeitVon: date  # ISO 8601 date format
    aktualisierungsdatum: datetime  # ISO 8601 date-time format
    veroeffentlichungsdatum: date  # ISO 8601 date format
    stellenart: JobType
    arbeitszeitModelle: Optional[List[WorkingTime]] = None
    berufe: List[Text]
    erfahrung: Optional[Erfahrung] = None
    ausbildungen: Optional[List[Ausbildung]] = None
    freierTitelStellengesuch: Optional[Text] = (
        None  # Optional as not all entries have it
    )


class BewerberUebersicht(GenericBewerber):
    letzteTaetigkeit: Optional[LetzteTaetigkeit] = None
    hatEmail: bool
    hatTelefon: bool
    hatAdresse: bool
    lokation: Lokation
    mehrereArbeitsorte: bool


class BewerberDetail(GenericBewerber):
    erwartungAnDieStelle: Optional[Text] = None
    abschluss: Optional[Text] = None
    sucheNurSchwerbehinderung: bool
    entfernungMaxKriterium: Text
    vertragsdauer: Text
    suchtGeringfuegigeBeschaeftigung: Optional[Text] = None
    lokationen: Optional[List[Lokation]] = None
    werdegang: Optional[List[LebenslaufElement]] = None
    bildung: Optional[List[LebenslaufElement]] = None
    mobilitaet: Optional[Mobilitaet] = None  # not sure what elements are possible here
    sprachkenntnisse: Optional[Kenntnisse] = None
    kenntnisse: Optional[Kenntnisse] = None
    softskills: Optional[List[Text]] = None
    lizenzen: Optional[List[Lizenz]] = None


class ApplicantSearchResponse(BaseModel):
    bewerber: List[BewerberUebersicht]
    maxErgebnisse: int
    page: int
    size: int
    facetten: Facetten
