"""Minimal Trip Budget & Currency Calculator tool for travel-concierge."""

from typing import Any

# Standard exchange rates relative to USD
EXCHANGE_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "JPY": 152.5,
    "GBP": 0.78,
    "CAD": 1.38,
    "PEN": 3.75,   # Peruvian Sol
    "ZAR": 18.2,   # South African Rand
    "AUD": 1.52,
    "CHF": 0.89,
    "HKD": 7.78,   # Hong Kong Dollar
}


def calculate_trip_budget(
    daily_cost_usd: float,
    days: int,
    travelers: int = 1,
    target_currency: str = "USD",
) -> dict[str, Any]:
    """Calculate an estimated trip budget breakdown and convert to target currency.

    Args:
        daily_cost_usd: Average daily budget per person in USD (e.g. 150.0).
        days: Trip length in days (e.g. 5).
        travelers: Number of people traveling (defaults to 1).
        target_currency: Currency code to convert total cost to (USD, EUR, JPY, GBP, CAD, PEN, ZAR, AUD, CHF, HKD). Defaults to 'HKD'.

    Returns:
        A dictionary with total costs, category breakdown, and currency conversion.
    """
    if days <= 0:
        days = 1
    if travelers <= 0:
        travelers = 1

    total_usd = daily_cost_usd * days * travelers

    # Standard travel budget allocation
    breakdown_usd = {
        "accommodation": round(total_usd * 0.45, 2),  # 45%
        "food_and_dining": round(total_usd * 0.25, 2), # 25%
        "activities_and_tours": round(total_usd * 0.20, 2), # 20%
        "local_transport": round(total_usd * 0.10, 2), # 10%
    }

    curr_code = target_currency.upper().strip()
    rate = EXCHANGE_RATES.get(curr_code, 1.0)
    converted_total = round(total_usd * rate, 2)

    return {
        "trip_duration_days": days,
        "travelers_count": travelers,
        "daily_cost_per_person_usd": daily_cost_usd,
        "total_budget_usd": round(total_usd, 2),
        "target_currency": curr_code,
        "exchange_rate_from_usd": rate,
        "total_budget_converted": converted_total,
        "category_breakdown_usd": breakdown_usd,
    }
