#%%
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Pakistan Weather AI",
    page_icon="🌦️",
    layout="wide"
)

st.markdown("""
<style>
.flood-high   { background:#FF4444; color:white; padding:12px; border-radius:8px; text-align:center; font-size:18px; font-weight:bold; }
.flood-medium { background:#FFA500; color:white; padding:12px; border-radius:8px; text-align:center; font-size:18px; font-weight:bold; }
.flood-low    { background:#00C853; color:white; padding:12px; border-radius:8px; text-align:center; font-size:18px; font-weight:bold; }
</style>
""", unsafe_allow_html=True)


def fetch(endpoint):
    try:
        r = requests.get(f"{API_URL}{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FastAPI. Run: uvicorn main:app --reload --port 8000")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Sidebar ──
with st.sidebar:
    st.title("🌦️ Pakistan Weather AI")
    st.divider()

    cities_resp = fetch("/cities")
    cities_list = cities_resp["cities"] if cities_resp else ["Lahore"]

    selected_city = st.selectbox("🏙️ Select City", cities_list)
    history_hours = st.slider("📅 History (hours)", 24, 168, 72, step=24)

    st.divider()
    st.markdown("**Models**")
    st.markdown("🌡️ Temp → RandomForestRegressor")
    st.markdown("🌧️ Rain → RandomForestClassifier")
    st.markdown("🌊 Flood → RandomForestClassifier")


# ── Header ──
st.title(f"🌦️ Pakistan Weather AI — {selected_city}")
st.caption("3 Random Forest models | WeatherAPI.com | Pakistan cities")
st.divider()


# ── Section 1: Predictions ──
data = fetch(f"/predict?city={selected_city}")

if data:
    current     = data["current"]
    predictions = data["predictions"]

    # Current readings
    st.subheader("📊 Current Conditions")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌡️ Temperature",   f"{current['temperature']}°C")
    c2.metric("💧 Humidity",      f"{current['humidity']}%")
    c3.metric("💨 Wind Speed",    f"{current['wind_speed']} kph")
    c4.metric("📊 Pressure",      f"{current['pressure']} mb")
    c5.metric("🌊 72hr Rainfall", f"{current['rain_roll_72']} mm")

    st.divider()

    # ML Predictions
    st.subheader("🤖 ML Model Predictions")
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown("### 🌡️ Temperature")
        if predictions["temperature"]:
            delta = round(predictions["temperature"] - current["temperature"], 1)
            st.metric("Predicted", f"{predictions['temperature']}°C", delta=f"{delta}°C vs now")
        st.caption(f"Confidence: **{predictions['temp_confidence']}**")

    with p2:
        st.markdown("### 🌧️ Rainfall")
        st.metric("Prediction", predictions["rain"])
        st.caption(f"Confidence: **{predictions['rain_confidence']}**")

    with p3:
        st.markdown("### 🌊 Flood Risk")
        flood = predictions["flood_risk"]
        emoji = predictions["flood_emoji"]
        conf  = predictions["flood_confidence"]

        if "High" in flood:
            st.markdown(f'<div class="flood-high">{emoji} {flood}</div>', unsafe_allow_html=True)
        elif "Medium" in flood:
            st.markdown(f'<div class="flood-medium">{emoji} {flood}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="flood-low">{emoji} {flood}</div>', unsafe_allow_html=True)
        st.caption(f"Confidence: **{conf}**")

    st.divider()

    # Alert banner
    if "High" in flood:
        st.error(f"⚠️ FLOOD ALERT — {selected_city} is at HIGH flood risk! 72hr rainfall: {current['rain_roll_72']}mm")
    elif "Medium" in flood:
        st.warning(f"🟡 CAUTION — {selected_city} is at MEDIUM flood risk.")
    else:
        st.success(f"✅ {selected_city} — Low flood risk. Normal conditions.")

    st.caption(f"Last updated: {data['last_updated']}")
    st.divider()


# ── Section 2: History charts ──
st.subheader(f"📈 Last {history_hours} Hours — {selected_city}")

hist = fetch(f"/history/{selected_city}?hours={history_hours}")

if hist and hist["records"]:
    hdf = pd.DataFrame(hist["records"])
    hdf["date"] = pd.to_datetime(hdf["date"])

    THEME = dict(plot_bgcolor="#1B2A3B", paper_bgcolor="#1B2A3B", font_color="white")

    col_l, col_r = st.columns(2)

    with col_l:
        fig_t = px.line(hdf, x="date", y="temperature",
                        title="🌡️ Temperature (°C)",
                        color_discrete_sequence=["#FF6B35"])
        fig_t.update_layout(**THEME)
        st.plotly_chart(fig_t, use_container_width=True)

    with col_r:
        fig_r = px.bar(hdf, x="date", y="rainfall",
                       title="🌧️ Rainfall (mm)",
                       color_discrete_sequence=["#00B4D8"])
        fig_r.update_layout(**THEME)
        st.plotly_chart(fig_r, use_container_width=True)

    # Flood indicator chart
    fig_roll = px.area(hdf, x="date", y="rain_roll_72",
                       title="🌊 72hr Rolling Rainfall — Flood Risk Indicator",
                       color_discrete_sequence=["#FF4444"])
    fig_roll.add_hline(y=20, line_dash="dot", line_color="orange",
                       annotation_text="Medium Risk (20mm)")
    fig_roll.add_hline(y=50, line_dash="dot", line_color="red",
                       annotation_text="High Risk (50mm)")
    fig_roll.update_layout(**THEME)
    st.plotly_chart(fig_roll, use_container_width=True)

st.divider()


# ── Section 3: All cities ──
st.subheader("🏙️ All Cities — Flood Risk Comparison")

comp = fetch("/compare")
if comp:
    cdf = pd.DataFrame(comp["cities"])

    def color_flood(val):
        return {
            "High Risk":   "background-color:#FF4444;color:white",
            "Medium Risk": "background-color:#FFA500;color:white",
            "Low Risk":    "background-color:#00C853;color:white",
        }.get(val, "")

    st.dataframe(cdf.style.map(color_flood, subset=["flood_risk"]),
                 use_container_width=True)

    fig_c = px.bar(
        cdf.sort_values("temperature", ascending=True),
        x="temperature", y="city", orientation="h",
        color="flood_risk",
        color_discrete_map={"High Risk":"#FF4444","Medium Risk":"#FFA500","Low Risk":"#00C853"},
        title="🌡️ Temperature by City (colored by Flood Risk)"
    )
    fig_c.update_layout(plot_bgcolor="#1B2A3B", paper_bgcolor="#1B2A3B", font_color="white")
    st.plotly_chart(fig_c, use_container_width=True)

st.divider()
st.caption("Pakistan Weather ML Project | WeatherAPI.com | Random Forest Models")
# %%
