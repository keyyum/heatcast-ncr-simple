"""Builds app/ncr_cities.geojson: the outlines of the 16 cities of Metro Manila (plus Pateros) for the map in the app.

    python app/make_ncr_map.py            # needs an internet connection; the result is already in the repository

Source: Philippine Statistics Authority PSGC administrative boundaries (2023 edition) as published by
https://github.com/faeldon/philippines-json-maps (MIT licence; made from https://github.com/altcoder/philippines-psgc-shapefiles).
The four NCR district files at 10 % detail are merged, the coordinates rounded to 5 decimals (about 1 m), the city names changed to the
names used in the data (for example "City of Manila" -> "Manila", "Quezon City" -> "Quezon"), and the middle point of each outline is added
for the name labels. Pateros is the 17th NCR local government: it is not one of the 16 cities in the data, so the map only shows its outline.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/faeldon/philippines-json-maps/master/2023/geojson/provdists/hires"
DISTRICTS = ["1303900000", "1307400000", "1307500000", "1307600000"]      # NCR first (Manila) to fourth district
OUT = Path(__file__).resolve().parent / "ncr_cities.geojson"
NOT_IN_DATA = {"Pateros"}


def data_name(psa_name: str) -> str:
    """'City of Las Piñas' -> 'Las Piñas', 'Quezon City' -> 'Quezon', 'Pasay City' -> 'Pasay', 'Pateros' -> 'Pateros'."""
    name = psa_name.strip()
    if name.startswith("City of "):
        name = name[len("City of "):]
    if name.endswith(" City"):
        name = name[: -len(" City")]
    return name


def rings(geometry: dict) -> list[list]:
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    return [poly[0] for poly in polygons]                 # the outer ring of every polygon


def centre(geometry: dict) -> tuple[float, float]:
    """Area-weighted middle point of the outer rings (shoelace formula; fine at the size of a city)."""
    a_sum = cx_sum = cy_sum = 0.0
    for ring in rings(geometry):
        for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
            cross = x0 * y1 - x1 * y0
            a_sum += cross
            cx_sum += (x0 + x1) * cross
            cy_sum += (y0 + y1) * cross
    return cx_sum / (3 * a_sum), cy_sum / (3 * a_sum)


def round_coords(node, places=5):
    return round(node, places) if isinstance(node, float) else [round_coords(n, places) for n in node]


def build() -> dict:
    features = []
    for code in DISTRICTS:
        with urllib.request.urlopen(f"{BASE}/municities-provdist-{code}.0.1.json", timeout=60) as r:
            district = json.load(r)
        for f in district["features"]:
            p = f["properties"]
            geometry = {"type": f["geometry"]["type"], "coordinates": round_coords(f["geometry"]["coordinates"])}
            cx, cy = centre(geometry)
            name = data_name(p["adm3_en"])
            features.append({"type": "Feature", "geometry": geometry, "properties": {
                "City": name, "psa_name": p["adm3_en"], "adm3_psgc": p["adm3_psgc"], "area_km2": p["area_km2"],
                "cx": round(cx, 5), "cy": round(cy, 5), "in_data": name not in NOT_IN_DATA}})
    features.sort(key=lambda f: f["properties"]["City"])
    return {"type": "FeatureCollection",
            "attribution": "City boundaries: Philippine Statistics Authority PSGC (2023) via faeldon/philippines-json-maps (MIT) "
                           "and altcoder/philippines-psgc-shapefiles; simplified to 10 %.",
            "features": features}


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{OUT.name}: {len(data['features'])} features, {OUT.stat().st_size / 1024:.0f} KB")
