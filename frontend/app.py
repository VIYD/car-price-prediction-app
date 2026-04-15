import os
from datetime import datetime

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
METADATA_URL = f"{BACKEND_URL}/metadata"
PREDICT_URL = f"{BACKEND_URL}/predict"


@st.cache_data(ttl=300)
def fetch_metadata() -> dict:
    response = requests.get(METADATA_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def estimate_price(payload: dict) -> float:
    response = requests.post(PREDICT_URL, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    if "price" not in data:
        raise ValueError("Backend response does not contain 'price'.")
    return float(data["price"])


def main() -> None:
    st.set_page_config(page_title="Car Price Predictor", page_icon="🚗", layout="centered")
    st.title("🚗 Car Price Predictor")
    st.caption(f"Backend API: `{BACKEND_URL}`")

    try:
        metadata = fetch_metadata()
    except requests.RequestException as exc:
        st.error(f"Could not load metadata from backend: {exc}")
        st.info("Ensure backend is running and reachable from this app.")
        return

    brands = metadata.get("brands", [])
    accidents = metadata.get("accidents", [])
    brand_models = metadata.get("brand_models", {})
    model_engines = metadata.get("model_engines", {})
    model_transmissions = metadata.get("model_transmissions", {})
    model_fuel_types = metadata.get("model_fuel_types", {})

    if not brands:
        st.warning("No brands available in metadata. Train model and verify metadata generation.")
        return

    current_year = datetime.now().year

    if "brand" not in st.session_state or st.session_state.brand not in brands:
        st.session_state.brand = brands[0]

    col1, col2 = st.columns(2)
    with col1:
        selected_brand = st.selectbox("Brand", options=brands, key="brand")

    models_for_brand = brand_models.get(selected_brand, [])
    if not models_for_brand:
        st.warning(f"No models available for brand: {selected_brand}")
        return

    if "model" not in st.session_state or st.session_state.model not in models_for_brand:
        st.session_state.model = models_for_brand[0]

    with col2:
        selected_model = st.selectbox("Model", options=models_for_brand, key="model")

    fuel_options = model_fuel_types.get(selected_model, []) or ["Unknown"]
    engine_options = model_engines.get(selected_model, []) or ["Unknown"]
    transmission_options = model_transmissions.get(selected_model, []) or ["Unknown"]

    if "fuel_type" not in st.session_state or st.session_state.fuel_type not in fuel_options:
        st.session_state.fuel_type = fuel_options[0]
    if "engine" not in st.session_state or st.session_state.engine not in engine_options:
        st.session_state.engine = engine_options[0]
    if "transmission" not in st.session_state or st.session_state.transmission not in transmission_options:
        st.session_state.transmission = transmission_options[0]

    col3, col4 = st.columns(2)
    with col3:
        model_year = st.number_input(
            "Model year",
            min_value=1990,
            max_value=current_year,
            value=st.session_state.get("model_year", min(max(2020, 1990), current_year)),
            step=1,
            key="model_year",
        )

    with col4:
        milage = st.number_input(
            "Mileage (miles)",
            min_value=0,
            value=st.session_state.get("milage", 50000),
            step=1000,
            key="milage",
        )

    col5, col6 = st.columns(2)
    with col5:
        selected_fuel = st.selectbox("Fuel type", options=fuel_options, key="fuel_type")

    with col6:
        selected_engine = st.selectbox("Engine", options=engine_options, key="engine")

    accident_options = accidents or ["Unknown"]
    if "accident" not in st.session_state or st.session_state.accident not in accident_options:
        st.session_state.accident = accident_options[0]

    col7, col8 = st.columns(2)
    with col7:
        selected_transmission = st.selectbox("Transmission", options=transmission_options, key="transmission")

    with col8:
        selected_accident = st.selectbox("Accident history", options=accident_options, key="accident")

    submitted = st.button("Estimate price", use_container_width=True)

    if submitted:
        payload = {
            "brand": selected_brand,
            "model": selected_model,
            "model_year": int(model_year),
            "milage": int(milage),
            "fuel_type": selected_fuel,
            "engine": selected_engine,
            "transmission": selected_transmission,
            "accident": selected_accident,
        }

        with st.spinner("Calculating estimate..."):
            try:
                price = estimate_price(payload)
            except requests.RequestException as exc:
                st.error(f"Prediction request failed: {exc}")
                return
            except ValueError as exc:
                st.error(str(exc))
                return

        st.success("Prediction generated")
        st.metric("Estimated price", f"${price:,.0f}")


if __name__ == "__main__":
    main()