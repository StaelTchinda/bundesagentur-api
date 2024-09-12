



from typing import Optional, Union, List, Text
from applicants.schemas.arbeitsagentur.enums import LocationRadius
from applicants.schemas.arbeitsagentur.request import SearchParameters
from applicants.schemas.arbeitsagentur.schemas import Lokation
from applicants.service.arbeitsagentur import ApplicantApi
from utils.location.openplz import Locality
from utils.location.zip import RadiusLocality
from src.utils.location.openplz import Locality, get_localities
from src.utils.location.zip import CountryCode, RadiusLocality, get_localities_in_radius


class LocationSearchService:

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
    def get_matching_locations_from_ba(
        cls, api: ApplicantApi, location: Union[Text, int], radius: LocationRadius = LocationRadius.ZERO
    ):
        if location is None:
            raise ValueError("Location is None")
        
        request_params: SearchParameters = SearchParameters(
            locationKeyword= location,
            locationRadius= radius,
            size=1,
        )

        search_response = api.search_applicants(request_params)

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

