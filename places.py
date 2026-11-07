import os
import time
from datetime import date, datetime, timezone
import requests

#google places (new) gives us real station-by-station fuel prices
NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
TEXT_URL = "https://places.googleapis.com/v1/places:searchText"
FIELDS = "places.id,places.displayName,places.formattedAddress,places.location,places.fuelOptions"

FUEL_LABELS = {
    "REGULAR_UNLEADED": "Regular",
    "MIDGRADE": "Midgrade",
    "PREMIUM": "Premium",
    "DIESEL": "Diesel",
    "E85": "E85",
}

#every request with fuelOptions is billed at the most expensive tier,
#so we cache results and cap how many calls we make per day
CACHE_SECONDS = 10 * 60
_cache = {}
_usage = {"day": None, "count": 0}


def _daily_limit():
    return int(os.getenv("PLACES_DAILY_LIMIT", "30"))


def _use_quota():
    today = date.today()
    if _usage["day"] != today:
        _usage["day"] = today
        _usage["count"] = 0
    if _usage["count"] >= _daily_limit():
        return False
    _usage["count"] += 1
    return True


def _price_to_float(price):
    return int(price.get("units", 0)) + price.get("nanos", 0) / 1e9


def _days_ago(update_time):
    try:
        updated = datetime.fromisoformat(update_time.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    return (datetime.now(timezone.utc) - updated).days


def _parse_station(place):
    prices = {}
    for fuel in place.get("fuelOptions", {}).get("fuelPrices", []):
        label = FUEL_LABELS.get(fuel.get("type"))
        if not label or "price" not in fuel:
            continue
        prices[label] = {
            "price": round(_price_to_float(fuel["price"]), 2),
            "days_ago": _days_ago(fuel.get("updateTime")),
        }
    location = place.get("location", {})
    return {
        "id": place.get("id"),
        "name": place.get("displayName", {}).get("text", "Gas station"),
        "address": place.get("formattedAddress", ""),
        "lat": location.get("latitude"),
        "lng": location.get("longitude"),
        "prices": prices,
    }


def _request(url, body, cache_key):
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]

    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY not set.")
    if not _use_quota():
        raise RuntimeError("Daily Google Places limit reached, try again tomorrow.")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELDS,
    }
    rsp = requests.post(url, json=body, headers=headers, timeout=15)
    data = rsp.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "Google Places error"))

    stations = [_parse_station(p) for p in data.get("places", [])]
    #don't remember an empty answer, so the next try asks Google again
    if stations:
        _cache[cache_key] = (time.time(), stations)
    return stations


def stations_near(lat, lng, radius_m=5000):
    """Closest gas stations to a coordinate, nearest first."""
    #rounding to ~1km means nearby lookups share the same cached result
    key = ("near", round(lat, 2), round(lng, 2), radius_m)
    body = {
        "includedTypes": ["gas_station"],
        "maxResultCount": 20,
        "rankPreference": "DISTANCE",
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius_m),
            }
        },
    }
    return _request(NEARBY_URL, body, key)


def stations_for_place(query):
    """Gas stations around a zip code or town name, e.g. '10001' or 'Hoboken NJ'."""
    key = ("text", query.strip().lower())
    body = {
        "textQuery": f"gas stations near {query}",
        "includedType": "gas_station",
        "pageSize": 20,
        #the server runs in Oregon, so say which country a bare zip code is in
        "regionCode": "US",
    }
    return _request(TEXT_URL, body, key)


def cheapest(stations, fuel="Regular", limit=5):
    """Stations that report a price for `fuel`, cheapest first."""
    priced = [s for s in stations if fuel in s["prices"]]
    priced.sort(key=lambda s: s["prices"][fuel]["price"])
    return priced[:limit]
