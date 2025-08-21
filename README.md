# Queensland in Motion

Visual, interactive climate and terrain maps for Queensland, Australia, built with Python, Plotly, Xarray, and SciPy.

## Visual gallery

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/91739d67-664f-47be-8fa1-d8e26d10f6d9" width="300" alt="Rainfall over Terrain" />
      <br /><sub>3D Terrain Elevation (DEM)</sub>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/a7cc9324-596f-45d7-ae00-eda2a03c9c14" width="300" alt="Solar Radiation Heatmap" />
      <br /><sub>Daily Rainfall over Terrain (3D, animated)</sub>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/720682f4-0d58-4f45-be36-6669ee9b00f8" width="300" alt="Monthly Climatology" />
      <br /><sub>Monthly Solar Radiation (animated heatmaps)</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/e7ce985a-87a0-447a-8b65-4de36b49545c" width="300" alt="Evapotranspiration Boxplots" />
      <br /><sub>Brisbane Monthly Climatology (Temp + Rain)</sub>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/5004c71e-5ef7-40e8-baa9-38b09597c56d" width="300" alt="Daily Temperatures" />
      <br /><sub>Evapotranspiration Boxplots</sub>
    </td>
    <td align="center" colspan="3">
      <img src="https://github.com/user-attachments/assets/cf1dc66d-63cb-42f0-af20-2948d72249ea" width="450" alt="Seasonal ΔRH" />
      <br /><sub>Seasonal ΔRH (tmin − tmax)</sub>
    </td>
  </tr>
  <tr>
  </tr>
  
</table>


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
