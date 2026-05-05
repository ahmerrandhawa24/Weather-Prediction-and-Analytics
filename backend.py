#%%
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine

app = FastAPI(title="Pakistan Weather Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
#  EXACT features used during your training
# ─────────────────────────────────────────
FEATURES = [
    'humidity', 'wind_speed', 'pressure',
    'temp_lag_1', 'rain_lag_1', 'humidity_lag_1',
    'hour', 'day', 'month', 'dayofweek',
    'is_monsoon', 'temp_lag_24',
    'temp_roll_24', 'rain_roll_72'
]

# ─────────────────────────────────────────
#  Load your 3 saved models
# ─────────────────────────────────────────
try:
    temp_model  = joblib.load("temperature_model.pkl")
    rain_model  = joblib.load("rain_model.pkl")
    flood_model = joblib.load("flood_model.pkl")
    print("✅ All 3 models loaded")
except Exception as e:
    print(f"❌ Model loading error: {e}")
    temp_model = rain_model = flood_model = None

# ─────────────────────────────────────────
#  Load data from PostgreSQL
# ─────────────────────────────────────────
try:
    engine = create_engine("postgresql://postgres:ahmer1@localhost:5432/weather_db")
    df = pd.read_sql("SELECT * FROM weather_data", engine)
    df["date"] = pd.to_datetime(df["date"])
    print(f"✅ Loaded {len(df)} rows from PostgreSQL")
except Exception as e:
    print(f"❌ DB error: {e} — falling back to CSV")
    df = pd.read_csv("weather_ml_ready.csv")
    df["date"] = pd.to_datetime(df["date"])


# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────
def get_latest_row(city: str):
    city_df = df[df["city"].str.lower() == city.lower()]
    if city_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found. Available: {sorted(df['city'].unique().tolist())}"
        )
    return city_df.sort_values("date").iloc[-1]


def build_X(row) -> pd.DataFrame:
    return pd.DataFrame([{feat: row[feat] for feat in FEATURES}])


def flood_label(pred: int) -> str:
    return {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}.get(int(pred), "Unknown")

def flood_emoji(pred: int) -> str:
    return {0: "🟢", 1: "🟡", 2: "🔴"}.get(int(pred), "⚪")


# ─────────────────────────────────────────
#  GET /
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "models_loaded": {
            "temperature_model": temp_model  is not None,
            "rain_model":        rain_model  is not None,
            "flood_model":       flood_model is not None,
        },
        "total_rows":   len(df),
        "total_cities": df["city"].nunique(),
    }


# ─────────────────────────────────────────
#  GET /cities
# ─────────────────────────────────────────
@app.get("/cities")
def get_cities():
    return {
        "cities": sorted(df["city"].unique().tolist()),
        "total":  df["city"].nunique()
    }


# ─────────────────────────────────────────
#  GET /predict?city=Lahore
# ─────────────────────────────────────────
@app.get("/predict")
def predict(city: str):
    row = get_latest_row(city)
    X   = build_X(row)

    # Temperature prediction + confidence
    if temp_model:
        pred_temp  = round(float(temp_model.predict(X)[0]), 1)
        tree_preds = np.array([t.predict(X)[0] for t in temp_model.estimators_])
        temp_conf  = round(max(0, min(100, 100 - float(np.std(tree_preds)))), 1)
    else:
        pred_temp = temp_conf = None

    # Rain prediction + confidence
    if rain_model:
        pred_rain  = int(rain_model.predict(X)[0])
        rain_proba = rain_model.predict_proba(X)[0]
        rain_conf  = round(float(max(rain_proba)) * 100, 1)
        rain_label = "Rain Expected 🌧️" if pred_rain == 1 else "No Rain ☀️"
    else:
        pred_rain = rain_conf = None
        rain_label = "Model not loaded"

    # Flood prediction + confidence
    if flood_model:
        pred_flood  = int(flood_model.predict(X)[0])
        flood_proba = flood_model.predict_proba(X)[0]
        flood_conf  = round(float(max(flood_proba)) * 100, 1)
    else:
        pred_flood = flood_conf = None

    return {
        "city":         row["city"],
        "last_updated": str(row["date"]),

        "current": {
            "temperature":  round(float(row["temperature"]), 1),
            "humidity":     round(float(row["humidity"]), 1),
            "wind_speed":   round(float(row["wind_speed"]), 1),
            "pressure":     round(float(row["pressure"]), 1),
            "rainfall":     round(float(row["rainfall"]), 2),
            "rain_roll_72": round(float(row["rain_roll_72"]), 2),
        },

        "predictions": {
            "temperature":      pred_temp,
            "temp_confidence":  f"{temp_conf}%" if temp_conf is not None else None,

            "rain":             rain_label,
            "rain_confidence":  f"{rain_conf}%" if rain_conf is not None else None,

            "flood_risk":       flood_label(pred_flood) if pred_flood is not None else None,
            "flood_emoji":      flood_emoji(pred_flood) if pred_flood is not None else "⚪",
            "flood_confidence": f"{flood_conf}%" if flood_conf is not None else None,
        }
    }


# ─────────────────────────────────────────
#  GET /history/Lahore?hours=168
# ─────────────────────────────────────────
@app.get("/history/{city}")
def get_history(city: str, hours: int = 168):
    city_df = df[df["city"].str.lower() == city.lower()]
    if city_df.empty:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")

    recent = city_df.sort_values("date").tail(hours)[[
        "date", "temperature", "humidity",
        "wind_speed", "rainfall", "pressure", "rain_roll_72"
    ]]
    return {
        "city":    city,
        "hours":   hours,
        "records": recent.to_dict(orient="records")
    }


# ─────────────────────────────────────────
#  GET /compare
# ─────────────────────────────────────────
@app.get("/compare")
def compare_cities():
    latest = (
        df.sort_values("date")
          .groupby("city").last()
          .reset_index()
    )
    result = []
    for _, row in latest.iterrows():
        X          = build_X(row)
        pred_flood = int(flood_model.predict(X)[0]) if flood_model else None
        result.append({
            "city":         row["city"],
            "temperature":  round(float(row["temperature"]), 1),
            "humidity":     round(float(row["humidity"]), 1),
            "rainfall":     round(float(row["rainfall"]), 2),
            "rain_roll_72": round(float(row["rain_roll_72"]), 2),
            "flood_risk":   flood_label(pred_flood) if pred_flood is not None else "N/A",
            "flood_emoji":  flood_emoji(pred_flood) if pred_flood is not None else "⚪",
        })
    return {"cities": result}


# ─────────────────────────────────────────
#  Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
# %%
