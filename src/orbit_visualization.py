import numpy as np
import plotly.graph_objects as go
from skyfield.api import load

def generate_orbit_plot(satellite_name='ISS (ZARYA)', num_minutes=90):
    # Load TLE data and satellite
    stations_url = 'https://celestrak.com/NORAD/elements/stations.txt'
    satellites = load.tle_file(stations_url)
    satellite = {sat.name: sat for sat in satellites}.get(satellite_name)

    if not satellite:
        raise ValueError(f"Satellite '{satellite_name}' not found.")

    # Time range: one orbit (~90 minutes for ISS)
    ts = load.timescale()
    minutes = np.linspace(0, num_minutes, 100)
    times = ts.utc(2025, 6, 29, 0, minutes)

    # Get positions in km
    positions = satellite.at(times).position.km
    x, y, z = positions

    # Create 3D plot
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(color='royalblue', width=3),
        name='Orbit Path'
    )])

    # Set 3D layout
    fig.update_layout(
        title=f'{satellite_name} Orbit Visualization',
        scene=dict(
            xaxis_title='X (km)',
            yaxis_title='Y (km)',
            zaxis_title='Z (km)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig
