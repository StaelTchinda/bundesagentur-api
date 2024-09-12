import enum
import logging
from pydantic import BaseModel
from typing import List, Optional, Text
import requests

from src.configs import DEFAULT_LOGGING_CONFIG

logging.basicConfig(**DEFAULT_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class DistrictType(enum.Enum):
    NoneType = "None"
    Kreisfreie_Stadt = "Kreisfreie_Stadt"
    Stadtkreis = "Stadtkreis"
    Kreis = "Kreis"
    Landkreis = "Landkreis"
    Regionalverband = "Regionalverband"


class MunicipalityType(enum.Enum):
    NoneType = "None"
    Markt = "Markt"
    Kreisfreie_Stadt = "Kreisfreie_Stadt"
    Stadtkreis = "Stadtkreis"
    Stadt = "Stadt"
    Kreisangehörige_Gemeinde = "Kreisangehörige_Gemeinde"
    Gemeindefreies_Gebiet_Bewohnt = "Gemeindefreies_Gebiet_Bewohnt"
    Gemeindefreies_Gebiet_Unbewohnt = "Gemeindefreies_Gebiet_Unbewohnt"
    Große_Kreisstadt = "Große_Kreisstadt"


class District(BaseModel):
    key: Text
    name: Text
    type: DistrictType


class FederalState(BaseModel):
    key: Text
    name: Text


class Municipality(BaseModel):
    key: Text
    name: Text
    type: MunicipalityType


class Locality(BaseModel):
    district: District
    federalState: FederalState
    municipality: Municipality
    name: Text
    postalCode: Text


def get_postal_codes(city: Text) -> List[Text]:
    localities = get_localities(name=city)
    return [locality.postalCode for locality in localities]


def get_localities(
    postalCode: Optional[int] = None,
    name: Optional[Text] = None,
    page: int = 1,
    page_size: int = 10,
) -> List[Locality]:
    base_url = "https://openplzapi.org/de/Localities"

    params = {
        "postalCode": postalCode,
        "name": name,
        "page": page,
        "page_size": page_size,
    }

    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"HTTP error! status: {response.status_code}")

    localities_data = response.json()
    localities: List[Locality] = [Locality(**locality) for locality in localities_data]
    return localities


# Example usage:
# async def main():
#     postal_codes = await get_postal_codes("Berlin")
#     print(postal_codes)

# asyncio.run(main())
