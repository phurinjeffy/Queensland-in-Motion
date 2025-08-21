# Queensland in Motion

Visual, interactive climate and terrain maps for Queensland, Australia, built with Python, Plotly, Xarray, and SciPy.

## Requirements

- Python 3.9+
- Packages:
  - numpy, pandas, xarray, scipy, plotly
  - matplotlib (for `x_2d.py`, `x_3d.py`)
  - netCDF backends: one of `netcdf4` or `h5netcdf`

Install (example):

```sh
python -m pip install numpy pandas xarray scipy plotly matplotlib netcdf4
```

## Data sources

### Elevation data
- The terrain data is taken from the Australia‑Wide Airborne Geophysical Survey 2 (AWAGS2), 2007 (survey P1152) line‑elevation dataset (Geoscience Australia, 2019), which was used to generate 3D model of Queensland’s topography.

https://ecat.ga.gov.au/geonetwork/srv/api/records/9458b427-79f5-40c2-8c2f-7d5cd4c7a59a

### Climate data: Rainfall, Solar Radiation, Temperature, Humidity, Evapotranspiration
- All climate visualisations are based on gridded datasets from SILO (Scientific Information for Land Owners), a comprehensive archive of Australian climate data maintained and distributed by the Queensland Government (2025). The NetCDF datasets used include:
  - Daily Rainfall (mm/day)
  - Solar Radiation (MJ/m²)
  - Minimum and Maximum Temperature (°C)
  - Relative Humidity (%) measured at daily min/max temperature
  - Morton’s Actual and Potential Evapotranspiration (mm/day)

https://www.longpaddock.qld.gov.au/silo/gridded-data/

## How to run

From the project root on macOS/Linux (zsh):

```sh
python 3d.py
python rain.py
python heatmap.py
python climate.py
python evapo.py
python temp.py
python rh.py
```

where running each script generate a `.html` file which contain the various visualisations.
