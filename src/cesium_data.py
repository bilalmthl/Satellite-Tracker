from skyfield.api import load
import datetime

def get_orbit_json(satellite_name, minutes=90):
    tle_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle'
    sats = load.tle_file(tle_url)
    sat_dict = {sat.name: sat for sat in sats}

    if satellite_name not in sat_dict:
        raise ValueError(f"{satellite_name} not found.")

    sat = sat_dict[satellite_name]
    ts = load.timescale()
    t0 = ts.now()
    t1 = ts.utc(t0.utc_datetime() + datetime.timedelta(minutes=minutes))
    times = ts.linspace(t0, t1, minutes)

    positions = sat.at(times).subpoint()
    lats = positions.latitude.degrees
    lons = positions.longitude.degrees
    alts = positions.elevation.km

    return [{"lat": lat, "lon": lon, "alt": alt} for lat, lon, alt in zip(lats, lons, alts)]
