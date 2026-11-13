"""Firestore tools for travel-concierge destinations catalog and user notes."""

from typing import Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-fc2df7c82d43"
COLLECTION_NAME = "destinations"
NOTES_COLLECTION = "travel_notes"

_db = None


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def search_destinations(query: str = "", region: str = "", max_budget_per_day: float = 0.0) -> list[dict[str, Any]]:
    """Search or list travel destinations from Firestore.

    Args:
        query: Optional keyword to match in destination name, country, description, or tags (e.g., 'temples', 'beach', 'hiking', 'Japan').
        region: Optional region filter (e.g. 'East Asia', 'Southern Europe', 'North America', 'South America', 'Africa').
        max_budget_per_day: Optional maximum average daily cost in USD (e.g. 150.0).

    Returns:
        A list of destination dictionaries matching the criteria.
    """
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()

    results = []
    q_lower = query.lower().strip()
    r_lower = region.lower().strip()

    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue

        if r_lower and data.get("region", "").lower() != r_lower:
            continue

        if max_budget_per_day > 0 and data.get("avg_daily_cost_usd", 0) > max_budget_per_day:
            continue

        if q_lower:
            name = data.get("name", "").lower()
            country = data.get("country", "").lower()
            desc = data.get("description", "").lower()
            tags = [t.lower() for t in data.get("tags", [])]
            attractions = [a.lower() for a in data.get("top_attractions", [])]

            if not (q_lower in name or q_lower in country or q_lower in desc or any(q_lower in t for t in tags) or any(q_lower in a for a in attractions)):
                continue

        results.append(data)

    return results


def get_destination_details(destination_id: str) -> dict[str, Any]:
    """Retrieve detailed information for a specific destination by its ID.

    Args:
        destination_id: The document ID of the destination (e.g., 'kyoto-japan', 'barcelona-spain', 'banff-canada').

    Returns:
        A dictionary with the destination details, or an error message if not found.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(destination_id).get()
    if not doc.exists:
        return {"error": f"Destination with ID '{destination_id}' was not found in catalog."}
    return doc.to_dict() or {}


def save_travel_note(destination_name: str, note: str, traveler_name: str = "guest") -> str:
    """Save a user travel note, wishlist item, or feedback for a destination in Firestore.

    Args:
        destination_name: Name of the destination this note applies to (e.g. 'Kyoto', 'Barcelona').
        note: The note content, recommendation, or itinerary idea to save.
        traveler_name: The traveler's name or username.

    Returns:
        A status string confirming the note was saved.
    """
    db = get_firestore_client()
    import datetime
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_ref = db.collection(NOTES_COLLECTION).document()
    doc_data = {
        "destination_name": destination_name,
        "note": note,
        "traveler_name": traveler_name,
        "created_at": now_iso,
    }
    doc_ref.set(doc_data)
    return f"Successfully saved travel note for '{destination_name}' with ID '{doc_ref.id}'."


def list_travel_notes(traveler_name: str = "guest") -> list[dict[str, Any]]:
    """Retrieve all saved travel notes for a traveler from Firestore.

    Args:
        traveler_name: The traveler's name to fetch notes for (defaults to 'guest').

    Returns:
        A list of saved travel notes.
    """
    db = get_firestore_client()
    query = db.collection(NOTES_COLLECTION).where("traveler_name", "==", traveler_name).stream()
    notes = [doc.to_dict() for doc in query if doc.to_dict()]
    return notes
