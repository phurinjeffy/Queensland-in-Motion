import numpy as np
import pandas as pd
import xarray as xr
import plotly.graph_objects as go

# === Load and interpolate DEM ===
cols = [
    'line', 'dateCode', 'flight', 'survey', 'FID',
    'altitude', 'bearing', 'gpshgt', 'ground', 'lasalt',
    'latitude', 'longitude', 'radalt'
]
df = pd.read_csv("data/P1152-line-elevation.dat", sep=r'\s+', header=None, names=cols)
df.replace([-9999999, -99999999, -999999, -9.999999e+32, -9.9999999999e+32], np.nan, inplace=True)
df.dropna(subset=['latitude', 'longitude', 'ground'], inplace=True)

# Define interpolation grid (matching Queensland)
num_points = 200
lon_lin = np.linspace(df['longitude'].min(), df['longitude'].max(), num_points)
lat_lin = np.linspace(df['latitude'].min(), df['latitude'].max(), num_points)

# === Load and interpolate solar radiation ===
radiation_ds = xr.open_dataset("data/2025.radiation.nc")
rad_var = list(radiation_ds.data_vars)[0]  # auto-detect variable
radiation = radiation_ds[rad_var]
times = pd.to_datetime(radiation['time'].values)

# Interpolate to same grid
lon_da = xr.DataArray(lon_lin, dims="lon")
lat_da = xr.DataArray(lat_lin, dims="lat")
radiation_interp = radiation.interp(lon=lon_da, lat=lat_da, method="linear")

# Compute monthly averages
radiation_surfaces = []
month_labels = []
for month in range(1, 13):
    month_idxs = np.where(times.month == month)[0]
    if len(month_idxs) == 0:
        continue
    month_data = radiation_interp.isel(time=month_idxs).mean(dim='time', skipna=True)
    radiation_surfaces.append(month_data.values)
    month_labels.append(pd.Timestamp(f"2025-{month:02d}-01").strftime('%B'))

# Compute consistent color scale limits
fixed_zmin = np.min([np.nanmin(surface) for surface in radiation_surfaces])
fixed_zmax = np.max([np.nanmax(surface) for surface in radiation_surfaces])

custom_colorscale = [
    [0.0,  "rgb(70,130,180)"],    # steel blue (low radiation)
    [0.3,  "rgb(173,216,230)"],   # light blue
    [0.5,  "rgb(255,255,150)"],   # soft warm yellow
    [0.7,  "rgb(255,165,0)"],     # orange
    [1.0,  "rgb(255,69,0)"]       # red (high radiation)
]

# === City coordinates for annotations ===
city_locs = {
    "Brisbane":   {"lon": 153.0351, "lat": -27.4550},
    "Gold Coast": {"lon": 153.4482, "lat": -28.0815},
    "Townsville": {"lon": 146.7700, "lat": -19.2499},
    "Cairns":     {"lon": 145.7633, "lat": -16.8878}
}

# Preprocess hover text
z_data = radiation_surfaces[0]
custom_text = np.empty(z_data.shape, dtype=object)

for i in range(z_data.shape[0]):
    for j in range(z_data.shape[1]):
        val = z_data[i, j]
        if np.isnan(val):
            custom_text[i, j] = (
                f"Longitude: {lon_lin[j]:.3f}°<br>" +
                f"Latitude: {lat_lin[i]:.3f}°<br>" +
                "Radiation: NaN MJ/m²"
            )
        else:
            custom_text[i, j] = (
                f"Longitude: {lon_lin[j]:.3f}°<br>" +
                f"Latitude: {lat_lin[i]:.3f}°<br>" +
                f"Radiation: {val:.2f} MJ/m²"
            )

# === Plotting ===
initial_heat = go.Heatmap(
    z=z_data,
    x=lon_lin,
    y=lat_lin,
    colorscale=custom_colorscale,
    zmin=fixed_zmin,
    zmax=fixed_zmax,
    colorbar=dict(title="Solar Radiation (MJ/m²)"),
    showscale=True,
    text=custom_text,
    hovertemplate="%{text}<extra></extra>"
)

fig = go.Figure(data=[initial_heat])

for city, coords in city_locs.items():
    fig.add_trace(
        go.Scatter(
            x=[coords["lon"]],
            y=[coords["lat"]],
            mode="markers+text",
            marker=dict(color="black", size=6, symbol="circle"),
            text=[city],
            textposition="top center",
            textfont=dict(size=12, color="black"),
            showlegend=False,
            hoverinfo="skip"
        )
    )

# Add dropdown with full trace override for monthly surfaces
fig.update_layout(
    title="Monthly Average Solar Radiation in Queensland (2025)",
    xaxis_title="Longitude",
    yaxis_title="Latitude",
    height=800,
    width=1000,
    updatemenus=[{
        "buttons": [
            {
                "label": label,
                "method": "update",
                "args": [
                    {"z": [radiation_surfaces[i]]},
                    {"shapes": []}
                ]
            } for i, label in enumerate(month_labels)
        ],
        "direction": "down",
        "x": 0.8,
        "xanchor": "center",
        "y": 1.15,
        "yanchor": "top",
        "showactive": True
    }]
)

fig.write_html("queensland_solar_radiation_heatmap.html")
