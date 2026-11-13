"""Seed script for travel-concierge destinations in Firestore."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-fc2df7c82d43"
COLLECTION_NAME = "destinations"

SEEDED_DESTINATIONS = [
    {
        "id": "kyoto-japan",
        "name": "Kyoto",
        "country": "Japan",
        "region": "East Asia",
        "description": "Historic city famous for classical Buddhist temples, gardens, imperial palaces, Shinto shrines, and traditional wooden houses.",
        "best_season": "Spring (Cherry Blossoms) or Autumn (Foliage)",
        "budget_level": "moderate",
        "avg_daily_cost_usd": 150,
        "tags": ["culture", "temples", "food", "nature", "historic"],
        "top_attractions": ["Fushimi Inari Taisha", "Kinkaku-ji", "Arashiyama Bamboo Grove"],
    },
    {
        "id": "barcelona-spain",
        "name": "Barcelona",
        "country": "Spain",
        "region": "Southern Europe",
        "description": "Vibrant coastal city renowned for Antoni Gaudí architecture, Mediterranean beaches, lively tapas bars, and artistic heritage.",
        "best_season": "May to June or September to October",
        "budget_level": "moderate",
        "avg_daily_cost_usd": 170,
        "tags": ["architecture", "beach", "food", "nightlife", "art"],
        "top_attractions": ["Sagrada Família", "Park Güell", "Gothic Quarter"],
    },
    {
        "id": "banff-canada",
        "name": "Banff National Park",
        "country": "Canada",
        "region": "North America",
        "description": "Breathtaking Canadian Rockies sanctuary featuring turquoise glacial lakes, alpine hikes, hot springs, and wildlife viewing.",
        "best_season": "June to August (hiking) or December to March (skiing)",
        "budget_level": "high",
        "avg_daily_cost_usd": 220,
        "tags": ["mountains", "nature", "hiking", "adventure", "wildlife"],
        "top_attractions": ["Lake Louise", "Moraine Lake", "Banff Gondola"],
    },
    {
        "id": "cusco-peru",
        "name": "Cusco & Sacred Valley",
        "country": "Peru",
        "region": "South America",
        "description": "Gateway to Machu Picchu and ancient Incan empire, blending indigenous Andean traditions with Spanish colonial plazas.",
        "best_season": "May to October (Dry season)",
        "budget_level": "budget",
        "avg_daily_cost_usd": 85,
        "tags": ["history", "hiking", "ancient-ruins", "culture", "mountains"],
        "top_attractions": ["Machu Picchu", "Sacsayhuamán", "Ollantaytambo"],
    },
    {
        "id": "cape-town-south-africa",
        "name": "Cape Town",
        "country": "South Africa",
        "region": "Africa",
        "description": "Dynamic harbor city tucked beneath Table Mountain, known for dramatic coastal roads, wine estates, penguins, and culinary excellence.",
        "best_season": "November to March (Summer)",
        "budget_level": "moderate",
        "avg_daily_cost_usd": 120,
        "tags": ["coastal", "wine", "nature", "hiking", "food"],
        "top_attractions": ["Table Mountain", "Cape Point & Boulders Beach", "Kirstenbosch Botanical Gardens"],
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for dest in SEEDED_DESTINATIONS:
        doc_id = dest["id"]
        doc_ref = collection.document(doc_id)
        doc_ref.set(dest)
        print(f"  ✓ Seeded destination: {dest['name']} ({doc_id})")

    print(f"\nDone! Seeded {len(SEEDED_DESTINATIONS)} destinations into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
