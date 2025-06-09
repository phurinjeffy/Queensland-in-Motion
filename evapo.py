import pandas as pd
import plotly.graph_objects as go
import calendar

df = pd.read_csv('data/brisbane_evapotranspiration.csv')

df.columns = df.columns.str.strip()
df['et_morton_actual'] = df['et_morton_actual'].astype(float)
df['et_morton_potential'] = df['et_morton_potential'].astype(float)

df['date'] = pd.to_datetime(df['YYYY-MM-DD'])
df['month'] = df['date'].dt.month
df['month_name'] = df['month'].apply(lambda x: calendar.month_abbr[x])

month_order = list(calendar.month_abbr)[1:]

fig = go.Figure()

fig.add_trace(go.Box(
    y=df['et_morton_actual'],
    x=df['month_name'],
    name='Actual ET',
    marker_color='#0072B2',  # CUD blue
    boxmean='sd',
    boxpoints='all',
    jitter=1,
    whiskerwidth=0.5,
    marker=dict(size=4, opacity=0.5)
))

fig.add_trace(go.Box(
    y=df['et_morton_potential'],
    x=df['month_name'],
    name='Potential ET',
    marker_color='#D55E00',  # CUD orange
    boxmean='sd',
    boxpoints='all',
    jitter=1,
    whiskerwidth=0.5,
    marker=dict(size=4, opacity=0.5)
))

fig.update_layout(
    title='Monthly Distribution of Actual and Potential Evapotranspiration at Brisbane Station',
    xaxis_title='Month',
    yaxis_title='Evapotranspiration (mm)',
    boxmode='group',
    width=1300,
    height=600,
    bargap=0.5,
    margin=dict(t=80, l=60, r=30, b=60),
    font=dict(size=14)
)

fig.write_html('et_boxplots_by_month.html')
