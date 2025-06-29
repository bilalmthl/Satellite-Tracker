import plotly.graph_objects as go
import numpy as np
from skyfield.api import load

# Load ISS TLE
stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
iss = {sat.name: sat for sat in satellites}['ISS (ZARYA)']

# Compute orbit positions
ts = load.timescale()
minutes = np.linspace(0, 92, 100)  # One ISS orbit (~92 minutes)
times = ts.utc(2024, 6, 29, 0, minutes)
positions = iss.at(times).position.km

fig = go.Figure(data=[go.Scatter3d(
    x=positions[0], y=positions[1], z=positions[2],
    mode='lines',
    line=dict(width=2, color='blue'),
    name='ISS Orbit'
)])

fig.update_layout(
    title='ISS Orbit Visualization',
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)'
    )
)

fig.show()
