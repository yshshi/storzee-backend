from apps.storage_units.models import StorageUnit
from typing import List, Dict, Any, Optional
import math

# ---- Distance helper ----
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# ---- Main function ----
def get_nearby_units(lat: float, lon: float, limit: int = 1, radius_km: Optional[float] = None) -> List[Dict[str, Any]]:
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return [{"success": False, "message": "Invalid coordinates."}]
    if lat == 0.0 and lon == 0.0:
        return [{"success": False, "message": "User doesn't have valid coordinates."}]

    units = StorageUnit.objects.filter(available=True, is_active=True)

    result = []
    for unit in units:
        if unit.latitude is None or unit.longitude is None:
            continue

        distance_km = haversine_km(lat, lon, float(unit.latitude), float(unit.longitude))

        if radius_km is not None and distance_km > float(radius_km):
            continue

        result.append({
            "title": unit.title,
            "description": unit.description,
            "address": unit.address,
            "city": unit.city,
            "price_per_hour": float(unit.price_per_hour or 0),
            "price_per_km": float(unit.price_per_km or 0),
            "rating": unit.rating,
            "benefits": unit.benefits or []
        })

    result.sort(key=lambda x: x.get("distance_km", 1e9))
    return result[:max(1, int(limit))]
