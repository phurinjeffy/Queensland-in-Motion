import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import plotly.graph_objects as go
import xarray as xr

# === Load and interpolate DEM from your .dat file ===
cols = [
    'line', 'dateCode', 'flight', 'survey', 'FID',
    'altitude', 'bearing', 'gpshgt', 'ground', 'lasalt',
    'latitude', 'longitude', 'radalt'
]

df = pd.read_csv("data/P1152-line-elevation.dat", sep=r'\s+', header=None, names=cols)
df.replace([-9999999, -99999999, -999999, -9.999999e+32, -9.9999999999e+32], np.nan, inplace=True)
df.dropna(subset=['latitude', 'longitude', 'ground'], inplace=True)

# Grid
num_points = 200
lon_lin = np.linspace(df['longitude'].min(), df['longitude'].max(), num_points)
lat_lin = np.linspace(df['latitude'].min(), df['latitude'].max(), num_points)
lon_grid, lat_grid = np.meshgrid(lon_lin, lat_lin)

points = df[['longitude', 'latitude']].values
values = df['ground'].values
terrain_data = griddata(points, values, (lon_grid, lat_grid), method='linear')

# === Load Daily Rainfall from NetCDF ===
rain_nc_path = "data/2025.daily_rain.nc"
ds = xr.open_dataset(rain_nc_path)

# Ensure proper variable names
rain_var = [v for v in ds.data_vars][0]  # Automatically detect first variable
rain = ds[rain_var]
times = pd.to_datetime(rain['time'].values)

# Interpolate the entire rainfall dataset to terrain grid
lon_da = xr.DataArray(lon_lin, dims="lon")
lat_da = xr.DataArray(lat_lin, dims="lat")
rain_interp = rain.interp(lon=lon_da, lat=lat_da, method="linear")

rain_surfaces = []
for i in range(len(times)):
    rain_day = rain_interp.isel(time=i).values.astype(np.float32)
    rain_day[rain_day <= -32765] = np.nan
    rain_surfaces.append(rain_day)


# Set consistent rainfall color scale
all_rain_values = np.concatenate([np.nan_to_num(r, nan=0).flatten() for r in rain_surfaces])
rain_cmin = 0
rain_cmax = np.percentile(all_rain_values, 99.5)  # Avoid extreme outliers

# Base figure with terrain
fig = go.Figure()

# === Static base 3D terrain ===
fig.add_trace(
    go.Surface(
        z=terrain_data,
        x=lon_lin,
        y=lat_lin,
        colorscale='Greys',
        showscale=False,
        name='Terrain',
        hovertemplate=
            "Longitude: %{x:.4f}<br>" +
            "Latitude: %{y:.4f}<br>" +
            "Elevation: %{z:.2f} m<extra></extra>",
        opacity=1.0
    ),
)

# === Frames for animation ===
frames = []
for i, rain_surface in enumerate(rain_surfaces):
    frame_data = []

    # Only include rainfall in frame (terrain stays static)
    frame_data.append(
        go.Surface(
            z=terrain_data + 0.5,
            x=lon_lin,
            y=lat_lin,
            surfacecolor=rain_surface,
            cmin=rain_cmin,
            cmax=rain_cmax,
            colorscale='Blues_r',
            reversescale=True,
            opacity=0.6,
            showscale=True,
            colorbar=dict(title='Rainfall Intensity (mm/day)')
        )
    )

    frames.append(go.Frame(data=frame_data, name=str(times[i].date())))


# === Update layout ===
fig.update_layout(
    title="Queensland - Rainfall Animation",
    scene=dict(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Elevation (m)',
        aspectratio=dict(x=1, y=1, z=0.3)
    ),
    width=1200,
    height=800,
    margin=dict(l=20, r=20, t=50, b=20),
    updatemenus=[{
        "type": "buttons",
        "showactive": False,
        "buttons": [
            {
                "label": "Play",
                "method": "animate",
                "args": [None, {
                    "frame": {"duration": 100, "redraw": True},
                    "fromcurrent": True,
                    "transition": {"duration": 0}
                }]
            },
            {
                "label": "Pause",
                "method": "animate",
                "args": [[None], {
                    "frame": {"duration": 0, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 0}
                }]
            }
        ],
        "x": -0.1,
        "xanchor": "left",
        "y": -0.1,
        "yanchor": "top"
    }],
    sliders=[{
        "steps": [
            {
                "method": "animate",
                "label": str(times[i].date()),
                "args": [[str(times[i].date())],
                         {"frame": {"duration": 0, "redraw": True},
                          "mode": "immediate",
                          "transition": {"duration": 0}}]
            } for i in range(len(times))
        ],
        "transition": {"duration": 0},
        "x": 0.1,
        "xanchor": "left",
        "y": 0,
        "yanchor": "top"
    }],
)

fig.frames = frames
fig.write_html("queensland_rainfall.html")
