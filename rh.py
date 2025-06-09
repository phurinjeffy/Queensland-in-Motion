import os
import xarray as xr
import pandas as pd
import numpy as np
import plotly.graph_objects as go

CITY_COORDS = {
    "Brisbane": {"lat": -27.4550, "lon": 153.0351}
}

YEARS = [2020, 2021, 2022, 2023, 2024]
DATA_DIR = "data/rh"

def find_nearest_grid_point(ds, target_lat, target_lon):
    lat_diff = np.abs(ds["lat"].values - target_lat)
    lon_diff = np.abs(ds["lon"].values - target_lon)
    return float(ds["lat"].values[lat_diff.argmin()]), float(ds["lon"].values[lon_diff.argmin()])

def get_season(month):
    return {
        12: "Summer", 1: "Summer", 2: "Summer",
        3: "Autumn", 4: "Autumn", 5: "Autumn",
        6: "Winter", 7: "Winter", 8: "Winter",
        9: "Spring", 10: "Spring", 11: "Spring"
    }[month]

def load_rh_data(year, city_coords):
    tmax_path = os.path.join(DATA_DIR, f"{year}.rh_tmax.nc")
    tmin_path = os.path.join(DATA_DIR, f"{year}.rh_tmin.nc")

    ds_tmax = xr.open_dataset(tmax_path)
    ds_tmin = xr.open_dataset(tmin_path)

    var_tmax = list(ds_tmax.data_vars)[0]
    var_tmin = list(ds_tmin.data_vars)[0]

    lat, lon = city_coords["lat"], city_coords["lon"]
    grid_lat, grid_lon = find_nearest_grid_point(ds_tmax, lat, lon)

    tmax = ds_tmax[var_tmax].sel(lat=grid_lat, lon=grid_lon, method="nearest")
    tmin = ds_tmin[var_tmin].sel(lat=grid_lat, lon=grid_lon, method="nearest")

    df = pd.DataFrame({
        "date": pd.to_datetime(tmax["time"].values),
        "rh_tmax": tmax.values,
        "rh_tmin": tmin.values
    })
    df["delta_rh"] = df["rh_tmin"] - df["rh_tmax"]
    df["year"] = df["date"].dt.year.astype(str)
    df["season"] = df["date"].dt.month.map(get_season)
    return df

def aggregate_seasonal_deltas(city_name):
    all_years_df = []
    for year in YEARS:
        df = load_rh_data(year, CITY_COORDS[city_name])
        all_years_df.append(df)
    combined = pd.concat(all_years_df)
    grouped = combined.groupby(["year", "season"])["delta_rh"].mean().reset_index()
    return grouped

def plot_seasonal_delta_rh(grouped_df, city_name):
    seasons = ["Spring", "Summer", "Autumn", "Winter"]

    # Colorblind-friendly palette
    color_map = {
        "Spring": "#CC79A7",  # orange
        "Summer": "#E69F00",  # sky blue
        "Autumn": "#009E73",  # green
        "Winter": "#56B4E9",  # pink
    }

    # Different line dash styles
    dash_map = {
        "Spring": "solid",
        "Summer": "dot",
        "Autumn": "dash",
        "Winter": "dashdot",
    }

    fig = go.Figure()
    for season in seasons:
        season_df = grouped_df[grouped_df["season"] == season]

        fig.add_trace(go.Scatter(
            x=season_df["year"],
            y=season_df["delta_rh"],
            mode="lines+markers",
            name=season,
            line=dict(
                width=3,
                dash=dash_map[season],
                color=color_map[season]
            ),
            marker=dict(size=6, symbol="circle")
        ))

    fig.update_layout(
        title=f"Seasonal Relative Humidity Difference (ΔRH) in {city_name} (2020-2024)",
        xaxis_title="Year",
        yaxis_title="ΔRH (%)",
        legend_title="Season",
        height=500,
        width=850,
        template="plotly_white",
        margin=dict(l=60, r=30, t=80, b=60),
    )
    fig.write_html(f"seasonal_delta_rh_{city_name.lower()}.html")

if __name__ == "__main__":
    city = "Brisbane"
    seasonal_data = aggregate_seasonal_deltas(city)
    plot_seasonal_delta_rh(seasonal_data, city)
