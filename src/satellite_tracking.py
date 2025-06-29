from skyfield.api import load

TLE_URL = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle'

def get_available_satellites():
    satellites = load.tle_file(TLE_URL)
    return sorted([sat.name for sat in satellites])

def get_satellite_position(satellite_name='ISS (ZARYA)'):
    ts = load.timescale()
    t = ts.now()
    satellites = load.tle_file(TLE_URL)
    sat = {s.name: s for s in satellites}.get(satellite_name)

    if not sat:
        raise ValueError("Satellite not found in current TLE set.")

    geocentric = sat.at(t)
    subpoint = geocentric.subpoint()
    return subpoint.latitude.degrees, subpoint.longitude.degrees, subpoint.elevation.km
