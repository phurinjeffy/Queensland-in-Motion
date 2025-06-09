import os
import xarray as xr
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Define coordinates for Queensland cities
CITY_COORDS = {
    "Brisbane": {"lat": -27.4550, "lon": 153.0351}
}

# Years to include
YEARS = [2020, 2021, 2022, 2023, 2024]
DATA_DIR = "data"

def find_nearest_grid_point(ds: xr.DataArray, target_lat: float, target_lon: float):
    lat_diff = np.abs(ds["lat"].values - target_lat)
    lon_diff = np.abs(ds["lon"].values - target_lon)
    return float(ds["lat"].values[lat_diff.argmin()]), float(ds["lon"].values[lon_diff.argmin()])

def load_and_aggregate_monthly_climatology(city_name: str):
    lat = CITY_COORDS[city_name]["lat"]
    lon = CITY_COORDS[city_name]["lon"]

    monthly_records = []

    for year in YEARS:
        max_path = os.path.join(DATA_DIR, f"temp/{year}.max_temp.nc")
        min_path = os.path.join(DATA_DIR, f"temp/{year}.min_temp.nc")
        rain_path = os.path.join(DATA_DIR, f"rain/{year}.daily_rain.nc")

        ds_max = xr.open_dataset(max_path)
        ds_min = xr.open_dataset(min_path)
        ds_rain = xr.open_dataset(rain_path)

        var_max = list(ds_max.data_vars)[0]
        var_min = list(ds_min.data_vars)[0]
        var_rain = list(ds_rain.data_vars)[0]

        grid_lat, grid_lon = find_nearest_grid_point(ds_max[var_max], lat, lon)

        max_vals = ds_max[var_max].sel(lat=grid_lat, lon=grid_lon, method="nearest").to_series()
        min_vals = ds_min[var_min].sel(lat=grid_lat, lon=grid_lon, method="nearest").to_series()
        rain_vals = ds_rain[var_rain].sel(lat=grid_lat, lon=grid_lon, method="nearest").to_series()

        df = pd.DataFrame({
            "max": max_vals,
            "min": min_vals,
            "rain": rain_vals
        })
        df.index.name = "date"
        df["mean"] = (df["max"] + df["min"]) / 2
        df["month"] = df.index.month

        monthly_summary = df.groupby("month").agg({
            "min": "mean",
            "mean": "mean",
            "max": "mean",
            "rain": "sum"
        }).reset_index()

        monthly_records.append(monthly_summary)

    # Average over years
    climatology_df = pd.concat(monthly_records).groupby("month").mean().reset_index()
    return climatology_df

def plot_climatology(climatology_df, city_name: str):
    fig = go.Figure()

    # Colorblind-friendly color palette
    line_colors = {
        "max": "#E64B35",     # Vivid red-orange
        "mean": "#7F63DD",    # Sky blue-teal
        "min": "#00A087"      # Teal green
    }

    # Max Temp – solid line
    fig.add_trace(go.Scatter(
        x=climatology_df["month"],
        y=climatology_df["max"],
        mode="lines+markers",
        name="Max Temperature",
        line=dict(color=line_colors["max"], width=2, dash="solid"),
        marker=dict(symbol="square", size=6),
        hovertemplate="%{y:.1f}°C<br>"
    ))

    # Mean Temp – dashed line
    fig.add_trace(go.Scatter(
        x=climatology_df["month"],
        y=climatology_df["mean"],
        mode="lines+markers",
        name="Mean Temperature",
        line=dict(color=line_colors["mean"], width=2, dash="dash"),
        marker=dict(symbol="circle", size=6),
        hovertemplate="%{y:.1f}°C<br>"
    ))

    # Min Temp – dotted line
    fig.add_trace(go.Scatter(
        x=climatology_df["month"],
        y=climatology_df["min"],
        mode="lines+markers",
        name="Min Temperature",
        line=dict(color=line_colors["min"], width=2, dash="dot"),
        marker=dict(symbol="triangle-up", size=6),
        hovertemplate="%{y:.1f}°C<br>"
    ))

    # Precipitation (bars, secondary axis)
    fig.add_trace(go.Bar(
        x=climatology_df["month"],
        y=climatology_df["rain"],
        name="Precipitation",
        marker_color="skyblue",
        yaxis="y2",
        opacity=0.6,
        hovertemplate="%{y:.1f} mm<br>"
    ))

    fig.update_layout(
        title=f"Monthly Temperature & Rainfall Patterns in {city_name} (2020–2024)",
        hovermode="x unified",
        xaxis=dict(
            title="Month",
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        ),
        yaxis=dict(
            title="Temperature (°C)",
            range=[0, 35]
        ),
        yaxis2=dict(
            title="Precipitation (mm)",
            overlaying="y",
            side="right",
            range=[0, 350]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        barmode="overlay",
        height=500,
        width=900,
        template="plotly_white"
    )

    fig.write_html(f"{city_name.lower()}_monthly_climatology.html")


city = "Brisbane"
climatology = load_and_aggregate_monthly_climatology(city)
plot_climatology(climatology, city)
