import requests
from skyfield.api import load

TLE_URL = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle'

# In-memory cache of image URLs to avoid repeated API calls
_IMAGE_CACHE: dict[str, str | None] = {}


def get_available_satellites() -> list[dict]:
    """
    Download the latest TLE and return a list of dicts:
      [ { "name": <satellite name>, "type": <classified type> }, … ]
    """
    sats = load.tle_file(TLE_URL)
    result = []
    for sat in sats:
        name = sat.name
        result.append({
            "name": name,
            "type": classify_satellite_type(name)
        })
    # sort alphabetically by name
    return sorted(result, key=lambda m: m["name"])


def get_satellite_position(satellite_name: str = 'ISS (ZARYA)') -> tuple[float, float, float]:
    """
    Return (latitude_deg, longitude_deg, altitude_km) for the given satellite.
    Raises ValueError if the satellite is not found.
    """
    ts = load.timescale()
    t = ts.now()
    sats = load.tle_file(TLE_URL)
    sat = {s.name: s for s in sats}.get(satellite_name)
    if not sat:
        raise ValueError(f"Satellite {satellite_name!r} not found in TLE data.")
    subpt = sat.at(t).subpoint()
    return subpt.latitude.degrees, subpt.longitude.degrees, subpt.elevation.km


def get_satellite_metadata(satellite_name: str) -> dict:
    """
    Returns metadata for a satellite:
      - 'type':      one of the classified types
      - 'image_url': URL of a representative image (or None)
    """
    # classify type
    typ = classify_satellite_type(satellite_name)

    # fetch or reuse cached image URL
    if satellite_name not in _IMAGE_CACHE:
        _IMAGE_CACHE[satellite_name] = _fetch_wikipedia_image(satellite_name)

    return {
        "type": typ,
        "image_url": _IMAGE_CACHE[satellite_name]
    }


def classify_satellite_type(name: str) -> str:
    """
    Simple classifier based on name substrings.
    """
    n = name.upper()
    if "STARLINK" in n:
        return "Starlink"
    if "NAVSTAR" in n or "GPS" in n:
        return "GPS/NAVSTAR"
    if "ISS" in n:
        return "ISS"
    if any(x in n for x in ["TIANHE", "CSS", "SHENZHOU"]):
        return "Chinese Station"
    if "FREGAT" in n or "DEB" in n:
        return "Debris"
    return "Other"


def _fetch_wikipedia_image(title: str) -> str | None:
    """
    1. Try to fetch the main image for the exact page `title`.
    2. If none, perform a search for `title`, take the first result,
       and fetch its main image.
    Returns the URL of the image or None if not found.
    """
    session = requests.Session()
    API_URL = "https://en.wikipedia.org/w/api.php"

    def get_image_for_page(page_title: str) -> str | None:
        params = {
            "action": "query",
            "titles": page_title,
            "prop": "pageimages",
            "piprop": "original",
            "format": "json",
        }
        resp = session.get(API_URL, params=params, timeout=5)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for pg in pages.values():
            if "original" in pg:
                return pg["original"]["source"]
        return None

    # 1) Exact-title lookup
    try:
        img = get_image_for_page(title)
        if img:
            return img
    except Exception:
        pass

    # 2) Fallback: search for title, take first result
    try:
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": title,
            "srlimit": 1,
            "format": "json",
        }
        r = session.get(API_URL, params=search_params, timeout=5)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        if results:
            first_title = results[0]["title"]
            return get_image_for_page(first_title)
    except Exception:
        pass

    # nothing found
    return None