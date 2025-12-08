import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "model_metrics.txt")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "metadata.joblib")


# ---------------------------
# Data Loading & Cleaning
# ---------------------------
def get_dataset():
    csv_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError("dataset.csv not found")
    return pd.read_csv(csv_path)


def clean_data(df):
    df = df.copy()

    df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce')
    df['milage'] = pd.to_numeric(df['milage'].astype(str).str.replace(r'[ mi,]', '', regex=True), errors='coerce')

    df['accident'] = df['accident'].fillna('Unknown')
    df['model'] = df['model'].fillna('Unknown')
    df['engine'] = df['engine'].fillna('Unknown')

    df = df.dropna(subset=['brand', 'model_year', 'milage', 'price'])

    df = df[df['price'] <= 200000]  # remove exotic cars

    df['car_age'] = 2025 - df['model_year']

    return df


# ---------------------------
# Model Training
# ---------------------------
def train_model():
    df = clean_data(get_dataset())

    features = ['brand', 'model', 'car_age', 'milage', 'fuel_type', 'engine', 'transmission', 'accident']
    target = 'price'

    X, y = df[features], df[target]

    categorical = ['brand', 'model', 'fuel_type', 'engine', 'transmission', 'accident']

    preprocessor = ColumnTransformer(
        [('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical)],
        remainder='passthrough'
    )

    # Lighter tuning to avoid overfitting
    model = RandomForestRegressor(
        n_estimators=250,
        max_depth=22,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    # ---------------------------
    # Evaluation
    # ---------------------------
    y_pred = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
    r2 = r2_score(y_test, y_pred)
    errors = np.abs(y_test - y_pred)

    # error percentiles
    e25, e50, e75 = np.percentile(errors, [25, 50, 75])

    # compact report
    report = f"""
================ Car Price Model Report ================
Model: Random Forest
Samples: Train={len(X_train)}, Test={len(X_test)}

--- Accuracy ---
MAE:  ${mae:,.2f}
RMSE: ${rmse:,.2f}
R²:   {r2:.4f}

--- Error Distribution ---
25% Error: ${e25:,.2f}
50% Error: ${e50:,.2f}
75% Error: ${e75:,.2f}

--- Price Stats ---
Avg Price: ${y_test.mean():,.2f}
Min Price: ${y_test.min():,.2f}
Max Price: ${y_test.max():,.2f}
========================================================
"""

    print(report)

    with open(METRICS_PATH, "w") as f:
        f.write(report)

    joblib.dump(pipeline, MODEL_PATH)

    # metadata for frontend
    def clean_values(x):
        bad = ['nan', 'not supported', '', 'None']
        return sorted([v for v in x.astype(str).unique() if v not in bad])

    # Create brand-model mapping
    brand_models = {}
    model_engines = {}
    model_transmissions = {}
    model_fuel_types = {}
    
    for brand in df['brand'].astype(str).unique():
        if brand not in ['nan', 'not supported', '', 'None']:
            models = df[df['brand'] == brand]['model'].astype(str).unique()
            brand_models[brand] = sorted([m for m in models if m not in ['nan', 'not supported', '', 'None']])
    
    # Create model-specific engine, transmission, and fuel type mappings
    for model in df['model'].astype(str).unique():
        if model not in ['nan', 'not supported', '', 'None']:
            model_df = df[df['model'] == model]
            engines = model_df['engine'].astype(str).unique()
            transmissions = model_df['transmission'].astype(str).unique()
            fuel_types = model_df['fuel_type'].astype(str).unique()
            
            model_engines[model] = sorted([e for e in engines if e not in ['nan', 'not supported', '', 'None']])
            model_transmissions[model] = sorted([t for t in transmissions if t not in ['nan', 'not supported', '', 'None']])
            model_fuel_types[model] = sorted([f for f in fuel_types if f not in ['nan', 'not supported', '', 'None']])

    metadata = {
        "brands": clean_values(df['brand']),
        "models": clean_values(df['model']),
        "brand_models": brand_models,
        "model_engines": model_engines,
        "model_transmissions": model_transmissions,
        "model_fuel_types": model_fuel_types,
        "fuel_types": clean_values(df['fuel_type']),
        "engines": clean_values(df['engine']),
        "transmissions": clean_values(df['transmission']),
        "accidents": clean_values(df['accident']),
    }

    joblib.dump(metadata, METADATA_PATH)

    print("Model, metrics and metadata saved.")


# ---------------------------
# Prediction
# ---------------------------
def predict(input_data: dict):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained.")

    pipeline = joblib.load(MODEL_PATH)

    input_data['car_age'] = 2025 - input_data['model_year']

    df = pd.DataFrame([input_data])

    pred = pipeline.predict(df)[0]
    return max(0, pred)


def get_metadata():
    if os.path.exists(METADATA_PATH):
        return joblib.load(METADATA_PATH)
    return {}


if __name__ == "__main__":
    train_model()
