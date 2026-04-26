# Pakistan Weather Analytics & Flood Prediction System

An end-to-end Data Engineering + Machine Learning project that collects real-time weather data from 17 Pakistani cities, builds predictive ML models, stores data in PostgreSQL, and serves live predictions through a FastAPI + Streamlit dashboard.

---

## Table of Contents

- Phase 1 — Data Extraction  
- Phase 2 — Data Transformation  
- Phase 3 — Data Loading  
- Phase 4 — Machine Learning Models  
- Phase 5 — Dashboard: Power BI  
- Phase 6 --- Streamlit Dashboard  

---

## Project Overview

This project builds a complete weather analytics pipeline focused on Pakistan — a country highly vulnerable to extreme weather events including monsoon floods. The system:

- Collects hourly weather data from 17 Pakistani cities via WeatherAPI  
- Engineers 14 ML features including lag, rolling, and monsoon indicators  
- Trains 3 Random Forest models for temperature prediction, rainfall classification, and flood risk assessment  
- Stores all data in PostgreSQL for efficient querying  
- Serves live predictions via FastAPI REST API  
- Visualizes everything in Power BI and Streamlit dashboards  

---

## Phase 1 — Data Extraction

**Goal:** Collect historical and live hourly weather data for 17 Pakistani cities.

**Cities Covered:**  
Lahore, Karachi, Islamabad, Sialkot, Peshawar, Swat, Murree, Gilgit, Faisalabad, Multan, Hyderabad, Quetta, Gujranwala, Bahawalpur, Sargodha, Abbottabad, Skardu  

**Data Source:** WeatherAPI.com — `/history.json` endpoint  

### Fields Collected:

| Field        | Description                     |
|-------------|---------------------------------|
| temperature | Hourly temperature (°C)         |
| humidity    | Relative humidity (%)           |
| wind_speed  | Wind speed (kph)                |
| pressure    | Atmospheric pressure (mb)       |
| rainfall    | Precipitation (mm)              |
| date        | Hourly timestamp                |
| city        | City name                       |

### Collection Strategy:

- 7 days historical data × 24 hours × 17 cities = 2,856 rows  
- Hourly collection via `/history.json` endpoint  
- Live current data via `/current.json` endpoint  

---

## Phase 2 — Data Transformation

**Goal:** Clean raw data and engineer ML-ready features.

### Data Cleaning

- Removed null values and duplicate rows  
- Converted date strings to proper datetime format  
- Standardized units — Celsius, mm, kph  

### Feature Engineering

Lag Features — capture recent history  

Rolling Features — capture trends  

---

## Phase 3 — Data Loading

**Goal:** Store clean data in PostgreSQL for efficient querying and API access.

**Database:** weather_db on PostgreSQL  

---

## Phase 4 — Machine Learning Models

**Goal:** Train 3 models for temperature prediction, rainfall classification, and flood risk.

### Model 1 — Temperature Prediction (Regression)

- **Algorithm:** Random Forest Regressor  
- **Top Features by Importance:** temp_lag_1 > temp_lag_24 > temp_roll_24 > hour > humidity  

---

### Model 2 — Rainfall Prediction (Classification)

- **Algorithm:** Random Forest Classifier  
- **Target:** rain_label (0 = No Rain, 1 = Rain)  
- **Features:** 14 engineered features  

---

### Model 3 — Flood Risk Prediction (Multi-class Classification)

- **Algorithm:** Random Forest Classifier (class_weight='balanced')  
- **Target:** flood_risk (0=Low, 1=Medium, 2=High)  
- **Features:** 14 engineered features  

`flood_model.pkl → RandomForestClassifier`

---

## Phase 5 — Dashboard

### Part A — Power BI Dashboard

**Pages built:**

- Live Overview — KPI cards, Pakistan city map, flood alert table  
- Temperature Analysis — trends, city comparison, hour-of-day heatmap  
- Rainfall & Flood Risk — 72hr rolling rainfall, risk level table with conditional formatting  
- Monsoon Dashboard — monsoon vs non-monsoon comparison, toggle slicer  

---

### Part B — Streamlit + FastAPI Live App

- **FastAPI Backend:** backend.py running on port 8000  
- **Streamlit Frontend:** app.py running on port 8501  

**Features:**

- City selector dropdown  
- 5 KPI metric cards (temperature, humidity, wind, pressure, 72hr rainfall)  
- ML predictions — temperature, rain, flood risk with confidence scores  
- Flood alert banner (color coded red/yellow/green)  
- Temperature and rainfall history charts  
- 72hr rolling rainfall chart with risk threshold lines  
- All cities comparison table with conditional color formatting  

---

## Results

- 17 Pakistani cities monitored  
- 1,540 rows of clean hourly weather data  
- 3 ML models trained and deployed  
- Live REST API with 5 endpoints  
- Interactive dashboard with real-time predictions  
- Flood risk classification using 72hr cumulative rainfall  
