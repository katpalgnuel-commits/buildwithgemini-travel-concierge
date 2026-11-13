"""Google Maps Geocoding and Places API (New) tools for travel-concierge."""

import os
from typing import Any
import requests

GEOCODING_ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_NEARBY_ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"


def _get_api_key() -> str:
    """Retrieve Google Maps API key from environment."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY is not set in the environment or .env file.")
    return api_key


def geocode_address(address: str) -> dict[str, Any]:
    """Turn an address or destination name into latitude and longitude coordinates.

    Args:
        address: The address, place name, or landmark to geocode (e.g. 'Sagrada Familia, Barcelona' or 'Kyoto, Japan').

    Returns:
        A dictionary with the formatted address and location coordinates ({'latitude': float, 'longitude': float}),
        or an error message if not found.
    """
    try:
        api_key = _get_api_key()
    except ValueError as e:
        return {"error": str(e)}

    params = {
        "address": address,
        "key": api_key,
    }

    try:
        response = requests.get(GEOCODING_ENDPOINT, params=params, timeout=10)
        data = response.json()
        if data.get("status") != "OK" or not data.get("results"):
            return {
                "error": f"Could not geocode '{address}'. Status: {data.get('status', 'UNKNOWN')}",
                "details": data.get("error_message", ""),
            }

        first_result = data["results"][0]
        geometry_loc = first_result.get("geometry", {}).get("location", {})
        return {
            "query": address,
            "formatted_address": first_result.get("formatted_address", ""),
            "location": {
                "latitude": geometry_loc.get("lat"),
                "longitude": geometry_loc.get("lng"),
            },
            "place_id": first_result.get("place_id", ""),
        }
    except Exception as exc:
        return {"error": f"Geocoding request failed: {exc}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 3000.0,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Find nearby places of a given type around coordinates using Places API (New).

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'museum', 'lodging', 'cafe', 'park').
        radius_meters: Search radius in meters (default 3000m, max 50000m).
        max_results: Maximum number of results to return (1-20, default 5).

    Returns:
        A list of place dictionaries containing name, formatted_address, and location.
    """
    try:
        api_key = _get_api_key()
    except ValueError as e:
        return [{"error": str(e)}]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }

    body = {
        "includedTypes": [place_type],
        "maxResultCount": min(max(int(max_results), 1), 20),
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        response = requests.post(PLACES_NEARBY_ENDPOINT, headers=headers, json=body, timeout=10)
        if response.status_code != 200:
            return [{"error": f"Places API returned status {response.status_code}: {response.text}"}]

        data = response.json()
        places = data.get("places", [])
        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown")
            loc = p.get("location", {})
            results.append({
                "name": display_name,
                "address": p.get("formattedAddress", ""),
                "location": {
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                },
            })
        return results
    except Exception as exc:
        return [{"error": f"Places request failed: {exc}"}]
