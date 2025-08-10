"""
Global Healthcare Data ETL & Analysis CLI

Features:
- Reads covid_stats & vaccination_data from MySQL (config.ini)
- Sidebar switch between COVID stats & Vaccination data
- KPIs, trends, top-N countries, and world map
- CLI-style analytics for COVID stats
- Vaccination analytics tab
- CSV export for filtered data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import configparser
import mysql.connector
from mysql.connector import Error
from datetime import datetime

st.set_page_config(page_title="🌍 Global Healthcare Data ETL & Analysis CLI", layout="wide", initial_sidebar_state="expanded")

def read_db_config(path="config.ini"):
    cfg = configparser.ConfigParser()
    cfg.read(path)
    return {
        "host": cfg["mysql"].get("host", "localhost"),
        "user": cfg["mysql"].get("user", "root"),
        "password": cfg["mysql"].get("password", ""),
        "database": cfg["mysql"].get("database", "healthcare_db"),
        "port": cfg["mysql"].getint("port", 3306),
    }

@st.cache_data(ttl=300)
def load_table(cfg_path, table_name):
    cfg = read_db_config(cfg_path)
    try:
        conn = mysql.connector.connect(**cfg)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
    except Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.columns = [c.strip() for c in df.columns]
    return df

@st.cache_data
def load_latlon(csv_path="data/world_latitude_longitude.csv"):
    try:
        latdf = pd.read_csv(csv_path)
        rename_map = {}
        for c in latdf.columns:
            if c.lower() in ("country", "country_name"):
                rename_map[c] = "country"
            if c.lower() in ("latitude", "lat"):
                rename_map[c] = "Latitude"
            if c.lower() in ("longitude", "lon", "long"):
                rename_map[c] = "Longitude"
        latdf = latdf.rename(columns=rename_map)
        if not set(["country", "Latitude", "Longitude"]).issubset(latdf.columns):
            return pd.DataFrame()
        return latdf[["country", "Latitude", "Longitude"]]
    except FileNotFoundError:
        return pd.DataFrame()

def summarize_kpis(df, metric_cols):
    return {col: int(df[col].sum()) for col in metric_cols if col in df.columns}

st.markdown("""
<style>
    /* KPI Cards */
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 15px 25px;
        box-shadow: 0 2px 8px rgb(0 0 0 / 0.1);
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 20px rgb(0 0 0 / 0.15);
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #0072B5;
    }
    .metric-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333333;
    }
    /* Sidebar header */
    .sidebar .sidebar-content > div:first-child {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 20px;
        color: #0072B5;
    }
    /* Footer */
    .footer {
        text-align: center;
        color: #666666;
        font-size: 0.9rem;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌍 Global Healthcare Data ETL & Analysis CLI")
st.markdown("Analyze COVID-19 and Vaccination trends worldwide with interactive filters and rich visualizations.")

st.sidebar.header("🔧 Settings & Filters")
cfg_path = st.sidebar.text_input("Config File Path", value="config.ini", help="Path to your MySQL config.ini file")
data_choice = st.sidebar.radio("Select Data to Explore", ["COVID Stats", "Vaccination Data"], help="Toggle between COVID cases data and vaccination data")
refresh = st.sidebar.button("🔄 Reload Data")

with st.spinner(f"Loading {data_choice} data..."):
    df = load_table(cfg_path, "covid_stats" if data_choice == "COVID Stats" else "vaccination_data")
    metric_options = ["cases", "deaths", "recovered"] if data_choice == "COVID Stats" else ["vaccinations"]

if df.empty:
    st.warning(f"No data found in '{data_choice}' table.")
    st.stop()

latlon_df = load_latlon()

country_list = sorted(df["country"].dropna().unique())
selected_country = st.sidebar.selectbox("Select Country", ["All"] + country_list, index=0, help="Filter data by a specific country or view all")
min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Select Date Range", value=[min_date, max_date], min_value=min_date, max_value=max_date, help="Filter data by date range")
metric = st.sidebar.selectbox("Choose Metric", options=metric_options, help="Select metric to analyze")
top_n = st.sidebar.slider("Top N Countries to Display", 3, 30, 7, help="Number of top countries to show in bar chart and map")

filtered = df.copy()
if selected_country != "All":
    filtered = filtered[filtered["country"] == selected_country]
if len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["date"] >= start_dt) & (filtered["date"] <= end_dt)]

tabs = st.tabs(["📊 Overview", "📈 Top N & Map", "🧮 Analytics", "📋 Raw Data"])

with tabs[0]:
    st.header("Overview")
    kpis = summarize_kpis(filtered, metric_options)
    cols = st.columns(len(kpis))
    for i, (label, value) in enumerate(kpis.items()):
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{value:,}</div>
                    <div class="metric-label">{label.title()}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown(f"**Records shown:** {len(filtered):,}")

    if metric in filtered.columns:
        fig = px.line(filtered.sort_values("date"), x="date", y=metric,
                      title=f"{metric.title()} over Time",
                      markers=True,
                      template="plotly_white",
                      color_discrete_sequence=["#0072B5"])
        fig.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.header("Top N Countries & Map")
    grouped = df.copy()
    if len(date_range) == 2:
        gstart, gend = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        grouped = grouped[(grouped["date"] >= gstart) & (grouped["date"] <= gend)]

    top = grouped.groupby("country", as_index=False)[metric].sum().sort_values(by=metric, ascending=False).head(top_n)
    fig_bar = px.bar(top, x="country", y=metric, text=metric,
                     labels={"country": "Country", metric: metric.title()},
                     title=f"Top {top_n} Countries by {metric.title()}",
                     template="plotly_white",
                     color_discrete_sequence=["#0072B5"])
    fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_bar.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', margin=dict(t=40))
    st.plotly_chart(fig_bar, use_container_width=True)

    if not latlon_df.empty:
        latest_date = df["date"].max()
        snapshot = df[df["date"] == latest_date].groupby("country", as_index=False)[metric].sum()
        map_df = snapshot.merge(latlon_df, on="country", how="left").dropna(subset=["Latitude", "Longitude"])
        if not map_df.empty:
            fig_map = px.scatter_geo(
                map_df, lat="Latitude", lon="Longitude", color=metric, size=metric,
                hover_name="country", projection="natural earth",
                color_continuous_scale=px.colors.sequential.Blues,
                title=f"Top {top_n} Countries by {metric.title()} on {latest_date.date()}"
            )
            fig_map.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Latitude/Longitude data not available for the selected countries.")

with tabs[2]:
    if data_choice == "COVID Stats":
        st.subheader("Global Summary")
        st.table(df.agg({"cases": "sum", "deaths": "sum", "recovered": "sum"}).to_frame().T.style.format("{:,}"))

        st.subheader("Countries with Zero Deaths")
        zero_deaths = df.groupby("country")["deaths"].sum().reset_index()
        zero_death_countries = zero_deaths[zero_deaths["deaths"] == 0]["country"].tolist()
        st.write(", ".join(zero_death_countries) if zero_death_countries else "None")

        st.subheader("Most Critical Cases (Top 5 by Deaths)")
        top_deaths = df.groupby("country")["deaths"].sum().reset_index().sort_values("deaths", ascending=False).head(5)
        st.table(top_deaths.style.format({"deaths": "{:,}"}))

        st.subheader("Recovered Rate > 50%")
        recovery = df.groupby("country").agg({"recovered": "sum", "cases": "sum"}).reset_index()
        recovery["rate"] = (recovery["recovered"] / recovery["cases"]) * 100
        st.table(recovery[recovery["rate"] > 50].style.format({"recovered": "{:,}", "cases": "{:,}", "rate": "{:.2f}%"}))

    else:
        st.subheader("Vaccination Summary")
        total_vax = int(df["vaccinations"].sum())
        st.metric("Total Vaccinations", f"{total_vax:,}")

        st.subheader("Top 5 Countries by Vaccinations")
        top_vax = df.groupby("country")["vaccinations"].sum().reset_index().sort_values("vaccinations", ascending=False).head(5)
        st.table(top_vax.style.format({"vaccinations": "{:,}"}))

with tabs[3]:
    st.header("Raw Data")
    st.dataframe(filtered.reset_index(drop=True))
    st.download_button("Download CSV", filtered.to_csv(index=False).encode(), f"{data_choice.replace(' ', '_')}.csv", "text/csv")

st.markdown("""
<footer class="footer">
    <hr>
    <p>Data sourced from MySQL tables: <code>covid_stats</code> & <code>vaccination_data</code>. Powered by Streamlit and Plotly.</p>
    <p style="font-size:1.3rem; font-weight:bold; color:black;">
        Developed by <span style="color:#0072B5;">Vaka Sravanthi</span>
    </p>
</footer>
""", unsafe_allow_html=True)

