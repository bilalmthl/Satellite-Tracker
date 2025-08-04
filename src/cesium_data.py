# src/cesium_data.py

from skyfield.api import load, EarthSatellite, wgs84
import datetime

def get_orbit_json(sat_name: str, minutes: int = 90):
    try:
        # Use a fixed TLE source that includes the desired satellite
        tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
        satellites = load.tle_file(tle_url)
        satellite_dict = {sat.name: sat for sat in satellites}
        sat = satellite_dict.get(sat_name)

        if not sat:
            raise ValueError(f"Satellite '{sat_name}' not found.")

        ts = load.timescale()
        t0 = ts.now()
        times = ts.utc(t0.utc_datetime() + datetime.timedelta(minutes=i) for i in range(minutes))

        orbit = []
        for t in times:
            geocentric = sat.at(t)
            subpoint = geocentric.subpoint()
            orbit.append({
                "lat": subpoint.latitude.degrees,
                "lon": subpoint.longitude.degrees,
                "alt": subpoint.elevation.km
            })

        return orbit

    except Exception as e:
        print("Cesium orbit error:", e)
        return []
