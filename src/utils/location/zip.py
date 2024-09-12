from pydantic import BaseModel
from enum import Enum
from typing import Dict, List, Text, Union

import requests
import logging
from src.configs import DEFAULT_LOGGING_CONFIG

logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class CountryCode(Enum):
    DE = "DE"
    AT = "AT"
    CH = "CH"
    CZ = "CZ"
    # ...


class DistanceUnit(Enum):
    KM = "km"
    M = "m"
    # ...


class RadiusLocality(BaseModel):
    country_code: CountryCode
    postal_code: Text
    state: Text
    place_name: Text
    lat: float
    lng: float
    distance: float
    unit: DistanceUnit


ZIP_BASE_URL: Text = "https://zip-api.eu/api/v1/radius"


def get_localities_in_radius(
    country_code: CountryCode,
    postal_code: Union[Text, int],
    distance: int,
    unit: DistanceUnit = DistanceUnit.KM,
) -> List[RadiusLocality]:
    url = f"{ZIP_BASE_URL}/{country_code.value}-{postal_code}/{distance}/{unit.value}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"HTTP error! status: {response.status_code}")
    json_response: Union[Dict, List[Dict]] = response.json()
    logger.info(f"Received response with keys: {json_response}")
    # Check if the response is a list of localities
    localities_data: List[Dict]
    if isinstance(json_response, dict):
        localities_data = [json_response]
    else:
        localities_data = json_response
    localities: List[RadiusLocality] = [
        RadiusLocality(**locality) for locality in localities_data
    ]
    return localities
