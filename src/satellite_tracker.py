from skyfield.api import load, wgs84

# Load TLE data from Celestrak
stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
print('Loaded', len(satellites), 'satellites')

# Find ISS
by_name = {sat.name: sat for sat in satellites}
iss = by_name['ISS (ZARYA)']

# Get current position
ts = load.timescale()
t = ts.now()
geocentric = iss.at(t)
subpoint = geocentric.subpoint()

print('ISS Position:')
print('Latitude:', subpoint.latitude.degrees)
print('Longitude:', subpoint.longitude.degrees)
print('Altitude:', subpoint.elevation.km, 'km')

