#%%
import requests
import pandas as pd
from datetime import datetime

API_KEY = "886f723feb7c49f5b1d205912262404"

cities = [
    "Lahore",
    "Karachi",
    "Islamabad",
    "Sialkot",
    "Peshawar",
    "Swat",
    "Murree",
    "Gilgit"
]

data_list = []

for city in cities:
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response = requests.get(url)
        data = response.json()

        record = {
            "city": city,
            "date": datetime.now(),
            "temperature": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"],
            "pressure": data["current"]["pressure_mb"],
            "rainfall": data["current"].get("precip_mm", 0)
        }

        data_list.append(record)

    except Exception as e:
        print(f"Error fetching data for {city}: {e}")

df = pd.DataFrame(data_list)

print(df)

#%%
import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "886f723feb7c49f5b1d205912262404"

cities = [
    "Lahore",
    "Karachi",
    "Islamabad",
    "Sialkot",
    "Peshawar",
    "Swat",
    "Murree",
    "Gilgit"
]

data_list = []

# Get last 7 days
for city in cities:
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"
        response = requests.get(url)
        data = response.json()

        try:
            day_data = data["forecast"]["forecastday"][0]["day"]

            record = {
                "city": city,
                "date": date,
                "temperature": day_data["avgtemp_c"],
                "humidity": day_data["avghumidity"],
                "wind_speed": day_data["maxwind_kph"],
                "pressure": None,  # not available in history easily
                "rainfall": day_data["totalprecip_mm"]
            }

            data_list.append(record)

        except:
            print(f"Error for {city} on {date}")

df = pd.DataFrame(data_list)

df.to_csv("weather_history.csv", index=False)

print(df.head())

# %%
import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "886f723feb7c49f5b1d205912262404"

cities = [
    "Lahore", "Karachi", "Islamabad", "Sialkot",
    "Peshawar", "Swat", "Murree", "Gilgit",
    "Faisalabad", "Multan", "Hyderabad",
    "Quetta", "Gujranwala", "Bahawalpur",
    "Sargodha", "Abbottabad", "Skardu"
]

data_list = []

# Last 7 days data
for city in cities:
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

        try:
            url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"
            response = requests.get(url)
            data = response.json()

            day_data = data["forecast"]["forecastday"][0]["day"]

            record = {
                "city": city,
                "date": date,
                "temperature": day_data["avgtemp_c"],
                "humidity": day_data["avghumidity"],
                "wind_speed": day_data["maxwind_kph"],
                "rainfall": day_data["totalprecip_mm"]
            }

            data_list.append(record)

        except Exception as e:
            print(f"Error for {city} on {date}: {e}")

# Convert to DataFrame
df = pd.DataFrame(data_list)

# Save file
df.to_csv("weather_history_expanded.csv", index=False)

# Preview
print(df.head())
print("\nTotal rows:", len(df))
# %%

#%%
import requests

API_KEY = "886f723feb7c49f5b1d205912262404"
url = "http://api.weatherapi.com/v1/history.json?key={}&q=Lahore&dt=2026-04-20".format(API_KEY)
data = requests.get(url).json()

forecastday = data["forecast"]["forecastday"][0]

print("Keys available:", forecastday.keys())
print("Number of hours:", len(forecastday["hour"]))
print("\nFirst hour sample:")
print(forecastday["hour"][0])
# %%
import requests
import pandas as pd
from datetime import datetime, timedelta
 
API_KEY = "886f723feb7c49f5b1d205912262404"
 
cities = [
    "Lahore", "Karachi", "Islamabad", "Sialkot",
    "Peshawar", "Swat", "Murree", "Gilgit",
    "Faisalabad", "Multan", "Hyderabad",
    "Quetta", "Gujranwala", "Bahawalpur",
    "Sargodha", "Abbottabad", "Skardu"
]
 
data_list = []
 
# Last 7 days hourly data
for city in cities:
    for i in range(7, 0, -1):                          # oldest → newest
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        try:
            url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"
            response = requests.get(url)
            data = response.json()
 
            # ✅ FIXED: was ["day"], now ["hour"] to get 24 rows per day
            hours = data["forecast"]["forecastday"][0]["hour"]
 
            for hour in hours:
                record = {
                    "city":        city,
                    "date":        hour["time"],         # "2026-04-20 00:00"
                    "temperature": hour["temp_c"],
                    "humidity":    hour["humidity"],
                    "wind_speed":  hour["wind_kph"],
                    "pressure":    hour["pressure_mb"],  # ✅ FIXED: now included
                    "rainfall":    hour["precip_mm"],
                }
                data_list.append(record)
 
            print(f"✓ {city} | {date} | {len(hours)} rows")
 
        except Exception as e:
            print(f"✗ Error — {city} on {date}: {e}")
 
# Convert to DataFrame
df = pd.DataFrame(data_list)
 
# Fix date column to proper datetime
df["date"] = pd.to_datetime(df["date"])
 
# Save file
df.to_csv("weather_history_expanded.csv", index=False)
 
# Preview
print(df.head())
# %%
from sqlalchemy import create_engine
import pandas as pd

# Load your cleaned CSV
df = pd.read_csv("weather_ml_ready.csv")

# PostgreSQL credentials
user = "postgres"
password = "ahmer1"
host = "localhost"
port = "5432"
database = "weather_db"

# Create connection
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
# %%
df.to_sql(
    "weather_data",
    engine,
    if_exists="replace",
    index=False
)
# %%
import pandas as pd
from sqlalchemy import create_engine

# DB connection
engine = create_engine("postgresql://postgres:ahmer1@localhost:5432/weather_db")

# Load data
query = "SELECT * FROM weather_data"
df = pd.read_sql(query, engine)

print(df.head())
# %%
features = [
    'humidity', 'wind_speed', 'pressure',
    'temp_lag_1', 'rain_lag_1', 'humidity_lag_1',
    'hour', 'day', 'month', 'dayofweek',
    'is_monsoon', 'temp_lag_24',
    'temp_roll_24', 'rain_roll_72'
]

target = 'temperature'
# %%
# Encode city
df = pd.get_dummies(df, columns=['city'])

# Drop date only
df = df.drop(columns=['date'])
# %%
from sklearn.model_selection import train_test_split

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
# %%
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(n_estimators=100)

model.fit(X_train, y_train)
# %%
y_pred = model.predict(X_test)

# %%
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("MAE:", mae)
print("RMSE:", rmse)
# %%
import pandas as pd

results = pd.DataFrame({
    "Metric": ["MAE", "RMSE"],
    "Value": [mae, rmse]
})

results.to_csv("temperature_prediction_metrics.csv", index=False)

print("File saved as temperature_prediction_metrics.csv")
# %%
import pandas as pd

importance = pd.Series(model.feature_importances_, index=features)
print(importance.sort_values(ascending=False))

# %%
import matplotlib.pyplot as plt
import pandas as pd

# Create series
importance = pd.Series(model.feature_importances_, index=features)

# Sort values
importance = importance.sort_values(ascending=False)

# Plot
plt.figure()
importance.plot(kind='bar')

plt.title("Important Features - Temperature Prediction")
plt.xlabel("Features")
plt.ylabel("Importance")

plt.xticks(rotation=45)
plt.tight_layout()
# %%
feature_columns = X.columns
# %%
def predict_temperature(input_data, model, feature_columns):
    import pandas as pd

    # Convert input to DataFrame
    input_df = pd.DataFrame([input_data])

    # One-hot encode city (same as training)
    input_df = pd.get_dummies(input_df)

    # Match columns with training data
    input_df = input_df.reindex(columns=feature_columns, fill_value=0)

    # Prediction
    prediction = model.predict(input_df)

    return prediction[0]
# %%
sample_input = {
    'humidity': 70,
    'wind_speed': 15,
    'pressure': 1007,
    'temp_lag_1': 25.2,
    'rain_lag_1': 0,
    'humidity_lag_1': 69,
    'hour': 6,
    'day': 21,
    'month': 4,
    'dayofweek': 1,
    'is_monsoon': 0,
    'temp_lag_24': 24.9,
    'temp_roll_24': 27.9,
    'rain_roll_72': 0,
    
    # city encoding (IMPORTANT)
    'city_Lahore': 0,
    'city_Karachi': 0,
    'city_Islamabad': 0,
    'city_Abbottabad': 1
}
# %%
pred = predict_temperature(sample_input, model, feature_columns)
print("Predicted Temperature:", pred)
# %%
results_df = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_pred
})

results_df.to_csv("model_results.csv", index=False)
# %%
import joblib

joblib.dump(model, "temperature_model.pkl")

# %%
df['rain_label'] = df['rainfall'].apply(lambda x: 1 if x > 0 else 0)
# %%
features = [
    'humidity', 'wind_speed', 'pressure',
    'temp_lag_1', 'rain_lag_1', 'humidity_lag_1',
    'hour', 'day', 'month', 'dayofweek',
    'is_monsoon', 'temp_lag_24',
    'temp_roll_24', 'rain_roll_72'
]

target = 'rain_label'
# %%
from sklearn.model_selection import train_test_split

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
# %%
from sklearn.ensemble import RandomForestClassifier

model_rain = RandomForestClassifier(n_estimators=100)

model_rain.fit(X_train, y_train)
# %%
y_pred = model_rain.predict(X_test)
# %%
from sklearn.metrics import accuracy_score, classification_report

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
# %%
import pandas as pd

report_dict = classification_report(y_test, y_pred, output_dict=True)
df_report = pd.DataFrame(report_dict).transpose()

df_report.to_csv("random_forest_results.csv")
# %%
results_df = pd.DataFrame({
    "Actual": y_test,
    "Predicted": y_pred
})

results_df.to_csv("rain_predictions.csv", index=False)
# %%
# ✅ 1. SAVE RAIN MODEL
import joblib

joblib.dump(model_rain, "rain_model.pkl")
# %%
# ✅ 2. PREDICTION FUNCTION + SAVE RESULT

def predict_rain(input_data, model, feature_columns):
    import pandas as pd

    # Convert to DataFrame
    input_df = pd.DataFrame([input_data])

    # Encode city (same as training)
    input_df = pd.get_dummies(input_df)

    # Match columns
    input_df = input_df.reindex(columns=feature_columns, fill_value=0)

    # Prediction
    pred = model.predict(input_df)[0]

    return pred


# 🔹 Example Input
sample_input = {
    'humidity': 80,
    'wind_speed': 10,
    'pressure': 1005,
    'temp_lag_1': 26,
    'rain_lag_1': 0,
    'humidity_lag_1': 78,
    'hour': 10,
    'day': 21,
    'month': 4,
    'dayofweek': 1,
    'is_monsoon': 0,
    'temp_lag_24': 25,
    'temp_roll_24': 27,
    'rain_roll_72': 0,

    # city encoding
    'city_Lahore': 1
}

# 🔹 Predict
prediction = predict_rain(sample_input, model_rain, feature_columns)

print("Rain Prediction (0=No, 1=Yes):", prediction)


# 💾 Save result
import pandas as pd

result_df = pd.DataFrame([{
    "city": "Lahore",
    "prediction": prediction
}])

result_df.to_csv("rain_prediction_result.csv", index=False)
# %%
def flood_risk(row):
    if row['rainfall'] > 10 or row['rain_roll_72'] > 20:
        return 2  # High Risk
    elif row['rainfall'] > 3 or row['rain_roll_72'] > 5:
        return 1  # Medium Risk
    else:
        return 0  # Low Risk

df['flood_risk'] = df.apply(flood_risk, axis=1)
# %%
features = [
    'humidity', 'wind_speed', 'pressure',
    'temp_lag_1', 'rain_lag_1', 'humidity_lag_1',
    'hour', 'day', 'month', 'dayofweek',
    'is_monsoon', 'temp_lag_24',
    'temp_roll_24', 'rain_roll_72'
]

target = 'flood_risk'
# %%
from sklearn.model_selection import train_test_split

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
# %%
from sklearn.ensemble import RandomForestClassifier

flood_model = RandomForestClassifier(n_estimators=100, class_weight='balanced')

flood_model.fit(X_train, y_train)
# %%
y_pred = flood_model.predict(X_test)
# %%from sklearn.metrics import classification_report, accuracy_score

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# %%
import joblib

joblib.dump(flood_model, "flood_model.pkl")
# %%
def predict_flood(input_data, model, feature_columns):
    import pandas as pd

    df_input = pd.DataFrame([input_data])
    df_input = pd.get_dummies(df_input)
    df_input = df_input.reindex(columns=feature_columns, fill_value=0)

    pred = model.predict(df_input)[0]

    if pred == 0:
        return "Low Risk"
    elif pred == 1:
        return "Medium Risk"
    else:
        return "High Risk"
# %%
sample = {
    'humidity': 85,
    'wind_speed': 12,
    'pressure': 1002,
    'temp_lag_1': 27,
    'rain_lag_1': 5,
    'humidity_lag_1': 83,
    'hour': 18,
    'day': 21,
    'month': 7,
    'dayofweek': 5,
    'is_monsoon': 1,
    'temp_lag_24': 26,
    'temp_roll_24': 28,
    'rain_roll_72': 25
}

print(predict_flood(sample, flood_model, feature_columns))
# %%
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
# %%
FEATURES = [
    'humidity', 'wind_speed', 'pressure',
    'temp_lag_1', 'rain_lag_1', 'humidity_lag_1',
    'hour', 'day', 'month', 'dayofweek',
    'is_monsoon', 'temp_lag_24',
    'temp_roll_24', 'rain_roll_72'
]
# %%
try:
    engine = create_engine("postgresql://postgres:ahmer1@localhost:5432/weather_db")
    df = pd.read_sql("SELECT * FROM weather_data", engine)
    df["date"] = pd.to_datetime(df["date"])
    print(f"✅ Loaded {len(df)} rows from PostgreSQL")
except Exception as e:
    print(f"❌ DB error: {e} — falling back to CSV")
    df = pd.read_csv("weather_ml_ready.csv")
    df["date"] = pd.to_datetime(df["date"])
# %%
def get_latest_row(city: str):
    city_df = df[df["city"].str.lower() == city.lower()]
    if city_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found. Available: {sorted(df['city'].unique().tolist())}"
        )
    return city_df.sort_values("date").iloc[-1]
# %%
def build_X(row) -> pd.DataFrame:
    return pd.DataFrame([{feat: row[feat] for feat in FEATURES}])
# %%
def flood_label(pred: int) -> str:
    return {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}.get(int(pred), "Unknown")
# %%
def flood_emoji(pred: int) -> str:
    return {0: "🟢", 1: "🟡", 2: "🔴"}.get(int(pred), "⚪")
# %%
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
# %%
