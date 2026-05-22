import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime as dt
from datetime import date as dt_date
from streamlit_folium import st_folium
import folium
from PIL import Image
import streamlit.components.v1 as components
import io
import random
import base64
from io import BytesIO


# --- UTILITY FUNCTIONS ---
def img_to_bytes(img: Image.Image) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- CONFIGURATION ---
#API_URL = "https://reefsight-api-2-98532754363.europe-west1.run.app/"
API_URL="http://127.0.0.1:8000"
img_url = "https://image2url.com/images/1765895634547-53b1795e-520b-477f-9fd4-7aa744291e4c.jpg"

# Define User options list early for validation
options_list = ("Image", "Data", "Image+Data")

# Header Image loader
def load_image(url: str):
    return Image.open(BytesIO(requests.get(url).content))

# --- CORAL FACTS complied using researched scientific websites material---
CORAL_FACTS = [
    " Coral bleaching occurs when corals expel the algae (zooxanthellae) that live in their tissues, causing the coral to turn white.",
    " The primary cause of coral bleaching is rising sea temperatures, often linked to climate change.",
    " Bleached corals are not dead; but they are under more stress and are at a higher risk of mortality.",
    " Increased sea surface temperatures are the most common cause of coral bleaching.",
    " Pollution from agricultural runoff and sewage can also lead to coral bleaching.",
    " Overexposure to sunlight, especially during low tides, can cause corals to bleach.",
    " Ocean acidification, resulting from increased CO2 levels, weakens corals and makes them more susceptible to bleaching.",
    " Coral bleaching reduces the biodiversity of coral reefs, as many marine species depend on healthy corals for habitat.",
    " Bleached corals have reduced reproductive capabilities, affecting the regeneration of coral populations.",
    " Coral reefs provide coastal protection by reducing wave energy, and their degradation can lead to increased coastal erosion.",
    " The loss of coral reefs can negatively impact local economies that rely on tourism and fishing.",
    " The first global coral bleaching event was recorded in 1998, during a strong El Niño event.",
    " Another significant global bleaching event occurred in 2010, affecting reefs in the Caribbean, Indian Ocean, and Southeast Asia.",
    " The most severe global bleaching event to date happened between 2014 and 2017, impacting over 70% of the world's coral reefs.",
    " Rising global temperatures due to climate change are the primary driver of increased coral bleaching events.",
    " Climate models predict that if current trends continue, annual severe bleaching will occur on 99% of the world's reefs by the end of the century.",
    " Efforts to reduce greenhouse gas emissions can help mitigate the impact of climate change on coral reefs.",
    " Marine protected areas (MPAs) can help reduce local stressors on coral reefs, giving them a better chance to recover from bleaching events.",
    " Coral restoration projects involve growing corals in nurseries and transplanting them to degraded reefs.",
    " Researchers are exploring the potential of breeding heat-resistant coral species to withstand higher temperatures.",
    " Reducing pollution and improving water quality can help alleviate some of the stressors that contribute to coral bleaching.",
    " Coral reefs support over 25% of all marine species, despite covering less than 1% of the ocean floor.",
    " They provide food and livelihood for millions of people worldwide.",
    " Coral reefs are a source of new medicines, including treatments for cancer and other medicines.",
    " Healthy coral reefs contribute to the overall health of the ocean, which is essential for the planet's climate regulation.",
    " Protecting coral reefs is crucial for maintaining biodiversity and the well-being of human communities that depend on them."
]

def get_random_fact():
    return random.choice(CORAL_FACTS)


# --- OCTOPUS LOADER ---
def show_octopus_loader():
    st.markdown("""
<div style="width:100%; height:60px; overflow:hidden; position:relative; background:transparent;">
    <div class="octopus" style="font-size:50px; position:absolute; left:-60px;">🐙</div>
    <p style="text-align:center; color:#004d40; font-weight:bold; margin-top:10px;">
        Fetching environmental data and running prediction...
    </p>
</div>

<style>
@keyframes swim {
    0% { left: -60px; }
    100% { left: 100%; }
}
.octopus {
    animation: swim 7s linear infinite;
    transform: scale(1.25);
    filter: hue-rotate(260deg) saturate(3) brightness(1);
}
</style>
""", unsafe_allow_html=True)

# --- CALLBACK FUNCTION FOR MODE SELECTION ---
def update_mode_selection():
    """Sets the chosen mode and enables rendering of the rest of the application."""
    # The radio widget's current value is accessible via its key in session_state
    st.session_state.prediction_type = st.session_state.mode_selector_radio_temp
    st.session_state.mode_chosen_flag = True

    # FIX #1: Clear ALL prediction-related state when mode changes
    st.session_state.show_results = False
    st.session_state.api_result = None
    st.session_state.uploaded_file = None  # Clear the uploaded image
    st.session_state.raw_api_response = {}

# --- PAGE SETUP ---
st.set_page_config(
    page_title="🌊 ReefSight Bleaching Predictor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS ---
st.markdown("""
<style>
.stApp { background-color: #ffffff; color:#004d40; }
h1,h2,h3,h4,h5,h6{color:#004d40 !important;}

div.stButton > button {
    background-color: darkorange !important;
    color: white !important;
    font-weight:bold !important;
    font-size:16px !important;
    padding:10px 22px !important;
    border-radius:8px !important;
    border:none !important;
    margin-left:auto !important;
    margin-right:auto !important;
    display:block !important;
}

div.stButton > button:hover {
    background-color:#ff9800 !important;
}

.fish-loader-container { width:100%; height:50px; overflow:hidden; position:relative; margin:20px 0; background:transparent; }
.fish-loader { width:50px; height:30px; background-color:#ff8f00; border-radius:50% 50% 50% 50% / 60% 60% 40% 40%; position:absolute; left:-100px; animation:swim 3s linear infinite; transform:rotate(-5deg);}
.fish-loader::after { content:''; position:absolute; top:5px; left:45px; width:20px; height:15px; background-color:#ff8f00; border-radius:50% / 0 100% 0 100%; transform:rotate(45deg);}
@keyframes swim {0%{left:-10%;}100%{left:110%;}}
</style>
""", unsafe_allow_html=True)


# --- SESSION STATE INITIALIZATION ---
if "selected_location" not in st.session_state:
    st.session_state.selected_location = {"lat": 16.5526, "lon": -151.7326} # Default Great Barrier Reef
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "api_result" not in st.session_state:
    st.session_state.api_result = None
if "raw_api_response" not in st.session_state:
    st.session_state.raw_api_response = {}
if "input_lat" not in st.session_state:
    st.session_state.input_lat = st.session_state.selected_location["lat"]
if "input_lon" not in st.session_state:
    st.session_state.input_lon = st.session_state.selected_location["lon"]
if "input_date" not in st.session_state:
    st.session_state.input_date = dt_date.today()
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
# State for loading indicator
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "fallback_info" not in st.session_state:
    st.session_state.fallback_info = {}

# --- Validate and reset prediction_type if invalid ---
if "prediction_type" not in st.session_state or st.session_state.prediction_type not in options_list:
    st.session_state.prediction_type = "Image+Data"

if "has_manual_data" not in st.session_state:
    st.session_state.has_manual_data = "No (fetch data)"

if "mode_chosen_flag" not in st.session_state:
    st.session_state.mode_chosen_flag = False

# FIX #2: Initialize manual override features in session state
if "manual_features" not in st.session_state:
    st.session_state.manual_features = {
        "Distance_to_Shore": 357.92,
        "Turbidity": 0.028,
        "Cyclone_Frequency": 52.33,
        "Depth_m": 2.0,
        "ClimSST": 300.47,
        "Temperature_Kelvin": 301.97,
        "Windspeed": 5.0,
        "Exposure": "Sheltered",
        "SSTA": 0.52,
        "SSTA_DHW": 2.58,
        "TSA": -0.11,
        "TSA_DHW": 1.36
    }

#--- Logo ---
col1, col2, col3 = st.columns(3)

with col2:
    st.image("reefsight_logo_2.png")
# --- HEADER ---
st.markdown(
    "<h4 style='text-align:center; color:#004d40;'> Automatic Coral Health Insights Powered by AI</h1>",
    unsafe_allow_html=True
)

st.markdown("<div style='padding-top:10px'></div>", unsafe_allow_html=True)

st.markdown("<h5 style='text-align:center;'>Use our model to analyze coral health using images, environmental data, or both.", unsafe_allow_html=True)

# Centered image
img = load_image(img_url)
st.markdown(
    f"""
    <div style='text-align:center;'>
        <img src='data:image/png;base64,{img_to_bytes(img)}'
             style='max-width:90%; height:auto;' />
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='padding-top:10px'></div>", unsafe_allow_html=True)

# Centered descriptive sentence
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Above you can see a clear difference between a healthy and bleached coral reef in South Florida, USA. </p>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- SECTION 1: PREDICTION MODE SELECTION (Centered) ---
st.markdown("<h3 style='text-align:center;'> What can you tell us about your coral? </h3>", unsafe_allow_html=True)

# Use columns to center the radio button group
col_l, col_c, col_r = st.columns([0.430, 0.450, 0.1])

with col_c:
    st.markdown(
        "<div style='display:flex; justify-content:center;'>",
        unsafe_allow_html=True
    )
    st.radio(
        "Choose prediction mode:",
        options_list,
        index=options_list.index(st.session_state.prediction_type),
        horizontal=True,
        key="mode_selector_radio_temp",
        label_visibility="collapsed",
        on_change=update_mode_selection
    )

st.markdown("</div>", unsafe_allow_html=True)

if "run_prediction_flag" not in st.session_state:
    st.session_state.run_prediction_flag = False

# --- PREDICTION LOGIC FUNCTION ---
def run_prediction(input_lat, input_lon, input_date, prediction_type, override_features, uploaded_file):

    # --- Internal Mode Handling for Tabular-Only Flow ---
    internal_mode = prediction_type
    if prediction_type == "Data":
        if st.session_state.has_manual_data == "Yes (manual data entry)":
            internal_mode = "Tabular-Only (Manual)"
        else:
            internal_mode = "Tabular-Only (NOAA)"

    # 1. Validation
    requires_loc_date = internal_mode not in ("Image")
    if requires_loc_date:
        # Note: Lat/Lon/Date are required for Fusion and all Tabular modes
        if input_lat is None or input_lon is None or (abs(input_lat) < 0.001 and abs(input_lon) < 0.001):
            st.error("Please provide a valid location (Latitude and Longitude, ensure they are not zero).")
            return False
        if input_date is None:
            st.error("Please provide an Observation Date.")
            return False

    if internal_mode in ("Image+Data", "Image") and not uploaded_file:
        st.error("Please upload an image for image-based prediction.")
        return False

    if internal_mode == "Tabular-Only (Manual)":
        required_keys = ["Distance_to_Shore", "Turbidity", "Cyclone_Frequency", "Depth_m", "ClimSST", "Temperature_Kelvin", "Windspeed", "SSTA", "SSTA_DHW", "TSA", "TSA_DHW", "Exposure"]
        # Ensure all required keys exist in override_features and none of their values are None
        if not all(key in override_features and override_features[key] and override_features[key] != '' for key in required_keys):
            st.error("Please ensure ALL 12 required manual data fields have been entered for this prediction mode.")
            return False

    # Reset results view and diagnostics before running
    st.session_state.show_results = False
    st.session_state.api_result = None
    st.session_state.raw_api_response = {}


    # --- START LOADING ---
    st.session_state.is_loading = True

    # Date extraction for new API schema
    input_year = input_date.year
    input_month = input_date.month

    # 2. Dynamic Endpoint and Request Construction
    api_call_kwargs = {}

    # Tabular Modes (NOAA or Manual)
    if internal_mode in ("Tabular-Only (NOAA)", "Tabular-Only (Manual)"):
        endpoint = "/predict/tabular"

        # Prepare the request body for the /predict/tabular endpoint
        if internal_mode == "Tabular-Only (NOAA)":
            tabular_payload = {
                "latitude": input_lat,
                "longitude": input_lon,
                "observation_date": input_date.isoformat()
            }

        elif internal_mode == "Tabular-Only (Manual)":
            tabular_payload = {
                "Latitude_Degrees": input_lat,
                "Longitude_Degrees": input_lon,
                "Date_Year": input_year,
                "Date_Month": input_month,
            }
        tabular_payload.update(override_features)

        api_call_kwargs = {"json": tabular_payload}

    # Image Modes (Fusion or Image-Only)
    elif internal_mode in ("Image+Data", "Image"):
        endpoint = "/predict/image"

        if uploaded_file:
            uploaded_file.seek(0)
            files = {"image_file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

        data = {}
        if internal_mode == "Image+Data":
            # Data should contain location/date and overrides if provided
            data = {
                "Latitude_Degrees": input_lat,
                "Longitude_Degrees": input_lon,
                "Date_Year": input_year,
                "Date_Month": input_month
            }
            if override_features:
                data.update(override_features)

            api_call_kwargs = {"files": files, "data": data}
        else:
            api_call_kwargs = {"files": files}

    else:
        st.session_state.is_loading = False
        st.error(f"Internal routing error for prediction mode: {internal_mode}")
        return False

    # 3. Make API Request
    try:
        full_url = f"{API_URL}{endpoint}"

        request_kwargs = {
            "timeout": 600,
        }

        if "json" in api_call_kwargs:
            request_kwargs["json"] = api_call_kwargs["json"]
        else:
            request_kwargs["files"] = api_call_kwargs.get("files")
            request_kwargs["data"] = api_call_kwargs.get("data")

        response = requests.post(full_url, **request_kwargs)


        # Raise HTTP errors first
        response.raise_for_status()

        # Parse JSON
        try:
            api_result = response.json()
            st.session_state.raw_api_response = api_result


        except json.JSONDecodeError:
            st.session_state.is_loading = False
            st.error("API response was not valid JSON.")
            st.exception(response.text)
            return False

    except requests.exceptions.HTTPError as e:

        st.session_state.is_loading = False

        try:
            error_json = e.response.json()
            detail = error_json.get("detail", {})

            # ---------------------------------------------------
            # ERROR TYPE & SUGGESTION
            # ---------------------------------------------------

            main_error = detail.get(
                "error",
                "Prediction failed."
            )

            st.error(f"❌ Error: {main_error}")


            suggestion = detail.get("suggestion")
            if suggestion:
                st.info(f"ℹ️ Suggestion: {suggestion}")

            # ---------------------------------------------------
            # FETCH ERRORS
            # ---------------------------------------------------

            fetch_errors = detail.get("fetch_errors", {})

            if fetch_errors:


                with st.expander(
                    "Show unavailable environmental variables"
                ):

                    for variable, msg in fetch_errors.items():

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#ffebee;
                                padding:10px;
                                border-radius:8px;
                                margin-bottom:8px;
                                border-left:6px solid #E24B4A;
                            ">
                                <b>{variable}</b><br>
                                {msg}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )



            # ---------------------------------------------------
            # MISSING COLUMNS
            # ---------------------------------------------------

            missing_cols = detail.get("missing_columns", [])

            if missing_cols:

                st.warning(
                    "The following required features were missing:"
                )

                st.write(", ".join(missing_cols))

            # ---------------------------------------------------
            # TECHNICAL MESSAGE
            # ---------------------------------------------------
            technical_message = detail.get("message")

            if technical_message:

                with st.expander("Technical details"):
                    st.code(technical_message)

        except Exception:

            st.error(
                f"Prediction API Error ({e.response.status_code})"
            )

            st.code(e.response.text)

        return False

    # --- STOP LOADING ---
    st.session_state.is_loading = False
    st.success("Prediction Complete!")

    # Store results and enable display
    st.session_state.api_result = api_result
    st.session_state.fallback_info = api_result.get("fallback_sources", {})
    st.session_state.show_results = True
    return True

# --- SECTION 2: DYNAMIC LAYOUT START (Conditional on mode selection) ---
if st.session_state.mode_chosen_flag:

    current_mode = st.session_state.prediction_type
    is_tabular_only = current_mode == "Data"
    is_fusion = current_mode == "Image+Data"
    is_image_only = current_mode == "Image"

    show_tabular_source_radio = is_tabular_only or is_fusion
    show_image_uploader = is_fusion or is_image_only

    #st.markdown("<h2 style='text-align:center;'>Input your data</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # ---------------------------------------------------------------
    # STEP 1: Data source selection (only for Data / Image+Data modes)
    # ---------------------------------------------------------------
    if show_tabular_source_radio:

        st.markdown("### Data Source Selection")
        col_source_choice, col_disclaimers = st.columns(2)
        with col_source_choice:
            st.markdown(
                "To determine the health state of a given coral reef, our model requires the following environmental variables:  \n"
                "<span style='color:#388e3c; '>Observation Date, Longitude, Latitude</span>, "
                "<span style='color:#1976d2; '>Distance to Shore, Turbidity, Cyclone Frequency, Depth, SSTA, SSTA DHW, "
                "ClimSST, Temperature, Windspeed, Reef Exposure, TSA, TSA DHW</span>",
                unsafe_allow_html=True,
    )

            st.markdown(
                "<span style='color:#388e3c; font-weight:bold;'>⬤</span> Essential inputs — must be provided by you &nbsp;&nbsp;&nbsp;  \n"
                "<span style='color:#1976d2; font-weight:bold;'>⬤</span> Optional inputs — the program can fetch these automatically.",
                unsafe_allow_html=True,
            )

            st.session_state.has_manual_data = st.radio(
                "Do you have access to the optional inputs?",
                ("No (fetch data)", "Yes (manual data entry)"),
                index=0 if st.session_state.has_manual_data == "No (fetch data)" else 1,
                key="manual_data_radio",
                horizontal=True,
            )
        with col_disclaimers:
            if show_tabular_source_radio and st.session_state.has_manual_data == "No (fetch data)":
                st.info(
                    "**Implications of data fetching**\n\n"
                    "⚠️ **Disclaimer 1**: fetching and processing environmental variables "
                    "from external databases (NOAA ERDDAP servers) may take up to 5 minutes.\n\n"
                    "⚠️ **Disclaimer 2**: a fallback strategy has been put in place in case "
                    "the environmental variables cannot be fetched based on your exact input "
                    "data (refer to the legend on the right-hand side)."
                )
        st.markdown("---")


    # Re-derive after the radio widget has rendered
    is_manual_tabular_only = is_tabular_only and st.session_state.has_manual_data == "Yes (manual data entry)"
    show_manual_override   = is_manual_tabular_only or is_fusion
    show_map               = is_fusion or is_tabular_only
    show_required_inputs   = not is_image_only



    # ---------------------------------------------------------------
    # STEP 2 (gating): Nothing more until the user has made a choice
    #   For Image-only mode there is no radio, so we proceed directly.
    # ---------------------------------------------------------------
    data_source_chosen = (
        not show_tabular_source_radio               # Image-only — no choice needed
        or st.session_state.has_manual_data in ("No (fetch data)", "Yes (manual data entry)")
    )

    if data_source_chosen:

        # We track everything that will be submitted outside the form
        current_override_features = {}

        # ---------------------------------------------------------------
        # IMAGE-ONLY MODE: simple uploader + submit, no map/date needed
        # ---------------------------------------------------------------
        if is_image_only:
            with st.form("prediction_input_form", clear_on_submit=False):
                st.subheader("Image Input")
                current_uploaded_file = st.file_uploader(
                    "Upload coral image", type=["jpg", "png", "jpeg"], key="image_uploader"
                )
                st.session_state.uploaded_file = current_uploaded_file
                submitted = st.form_submit_button(
                    "RUN PREDICTION", type="primary", help="Run bleaching prediction now!"
                )

        # ---------------------------------------------------------------
        # ALL OTHER MODES: unified "Date and Location" section with map
        # ---------------------------------------------------------------
        else:
            # ── Section header ──────────────────────────────────────────
            st.markdown("### 📍 Date and Location")
            st.write(
                "Please indicate a date and location for your coral reef observation. "
                "You can manually input the reef's geocoordinates or use the map to localise it"
            )

            # ── Two-column layout: inputs left, map right ────────────────
            input_col, map_col = st.columns([1, 1])

            # LEFT — date / lat / lon inputs (and image uploader for Fusion)
            with input_col:

                # When manual fields follow below, we skip st.form entirely so we
                # can place the single "RUN PREDICTION" button after those fields.
                # When there are no manual fields, we use st.form for the UX benefit
                # of Enter-to-submit.
                if show_manual_override:
                    # --- Formless inputs (state written on every rerun) ---
                    input_date = st.date_input(
                        "Observation Date",
                        value=st.session_state.input_date,
                        key="date_input",
                    )
                    input_lat = st.number_input(
                        "Latitude (Degrees)",
                        value=st.session_state.input_lat,
                        format="%.6f",
                        key="lat_input",
                    )
                    input_lon = st.number_input(
                        "Longitude (Degrees)",
                        value=st.session_state.input_lon,
                        format="%.6f",
                        key="lon_input",
                    )
                    st.session_state.input_lat = input_lat
                    st.session_state.input_lon = input_lon
                    st.session_state.input_date = input_date
                    st.session_state.selected_location = {"lat": input_lat, "lon": input_lon}

                    if show_image_uploader:
                        st.markdown("---")
                        st.subheader("Image Input")
                        current_uploaded_file = st.file_uploader(
                            "Upload coral image",
                            type=["jpg", "png", "jpeg"],
                            key="image_uploader",
                        )
                        st.session_state.uploaded_file = current_uploaded_file
                    else:
                        current_uploaded_file = st.session_state.uploaded_file

                    submitted = False  # set by the bottom button further below

                else:
                    # --- Form-based inputs (no manual fields follow) ---
                    with st.form("prediction_input_form", clear_on_submit=False):
                        input_date = st.date_input(
                            "Observation Date",
                            value=st.session_state.input_date,
                            key="date_input",
                        )
                        input_lat = st.number_input(
                            "Latitude (Degrees)",
                            value=st.session_state.input_lat,
                            format="%.6f",
                        )
                        input_lon = st.number_input(
                            "Longitude (Degrees)",
                            value=st.session_state.input_lon,
                            format="%.6f",
                        )
                        st.session_state.input_lat = input_lat
                        st.session_state.input_lon = input_lon
                        st.session_state.input_date = input_date
                        st.session_state.selected_location = {"lat": input_lat, "lon": input_lon}

                        if show_image_uploader:
                            st.markdown("---")
                            st.subheader("Image Input")
                            current_uploaded_file = st.file_uploader(
                                "Upload coral image",
                                type=["jpg", "png", "jpeg"],
                                key="image_uploader",
                            )
                            st.session_state.uploaded_file = current_uploaded_file
                        else:
                            current_uploaded_file = st.session_state.uploaded_file

                        submitted = st.form_submit_button(
                            "RUN PREDICTION",
                            type="primary",
                            help="Run bleaching prediction now!",
                        )

            # RIGHT — map widget
            with map_col:
                map_center = [
                    st.session_state.selected_location["lat"],
                    st.session_state.selected_location["lon"],
                ]
                m = folium.Map(
                    location=map_center,
                    zoom_start=6,
                    width="100%",
                    min_zoom=2,
                    max_bounds=True,
                    height=460,
                    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                    attr="Reef Overlay",
                )
                m.fit_bounds([[-85, -180], [85, 180]])
                if st.session_state.selected_location:
                    folium.Marker(
                        location=[
                            st.session_state.selected_location["lat"],
                            st.session_state.selected_location["lon"],
                        ],
                        tooltip="Selected Location",
                        icon=folium.Icon(color="darkblue", icon="fish", prefix="fa"),
                    ).add_to(m)

                map_data = st_folium(m, width="100%", height=460)
                if map_data and map_data.get("last_clicked"):
                    st.session_state.input_lat = map_data["last_clicked"]["lat"]
                    st.session_state.input_lon = map_data["last_clicked"]["lng"]
                    st.session_state.selected_location = {
                        "lat": st.session_state.input_lat,
                        "lon": st.session_state.input_lon,
                    }

            # ---------------------------------------------------------------
            # MANUAL ENVIRONMENTAL VARIABLES
            # Shown below the date/location block, left-aligned, when needed
            # ---------------------------------------------------------------
            if show_manual_override:
                st.markdown("---")
                header_text = (
                    "Manual Feature Overrides *(will override pulled data)*"
                    if is_fusion
                    else "🌡️ Other Environmental Variables"
                )
                st.markdown(f"### {header_text}")

                # For Fusion mode, wrap in an expander so it stays optional
                _show_fields = True
                if is_fusion:
                    with st.expander("Click to manually input environmental data (optional)"):
                        _show_fields = True   # expander is always "open" once clicked
                        # We render the fields INSIDE the expander context below
                        _inside_expander = True
                else:
                    _inside_expander = False

                def _render_manual_fields():
                    c1, c2 = st.columns(2)
                    with c1:
                        st.session_state.manual_features["Distance_to_Shore"] = st.number_input(
                            "Distance to Shore (m)",
                            value=st.session_state.manual_features["Distance_to_Shore"],
                            key="dist_shore_outer", format="%.2f",
                        )
                        st.session_state.manual_features["Turbidity"] = st.number_input(
                            "Turbidity (NTU)",
                            value=st.session_state.manual_features["Turbidity"],
                            key="turbidity_outer", format="%.3f",
                        )
                        st.session_state.manual_features["Cyclone_Frequency"] = st.number_input(
                            "Cyclone Frequency",
                            value=st.session_state.manual_features["Cyclone_Frequency"],
                            key="cyclone_freq_outer", format="%.2f",
                        )
                        st.session_state.manual_features["Depth_m"] = st.number_input(
                            "Depth (m)",
                            value=st.session_state.manual_features["Depth_m"],
                            key="depth_m_outer", format="%.1f",
                        )
                    with c2:
                        st.session_state.manual_features["ClimSST"] = st.number_input(
                            "ClimSST (K)",
                            value=st.session_state.manual_features["ClimSST"],
                            help="Climatological Sea Surface Temperature",
                            key="clim_sst_outer", format="%.2f",
                        )
                        st.session_state.manual_features["Temperature_Kelvin"] = st.number_input(
                            "Temperature (K)",
                            value=st.session_state.manual_features["Temperature_Kelvin"],
                            key="temp_k_outer", format="%.2f",
                        )
                        st.session_state.manual_features["Windspeed"] = st.number_input(
                            "Windspeed (m/s)",
                            value=st.session_state.manual_features["Windspeed"],
                            key="windspeed_outer", format="%.1f",
                        )
                        exposure_options = ["Sheltered", "Exposed", "Sometimes"]
                        cur_idx = (
                            exposure_options.index(st.session_state.manual_features["Exposure"])
                            if st.session_state.manual_features["Exposure"] in exposure_options
                            else 0
                        )
                        st.session_state.manual_features["Exposure"] = st.selectbox(
                            "Reef Exposure",
                            options=exposure_options,
                            index=cur_idx,
                            key="exposure_outer",
                        )

                    c3, c4 = st.columns(2)
                    with c3:
                        st.session_state.manual_features["SSTA"] = st.number_input(
                            "SSTA", value=st.session_state.manual_features["SSTA"],
                            help="Sea Surface Temperature Anomaly",
                            key="ssta_outer", format="%.3f",
                        )
                        st.session_state.manual_features["SSTA_DHW"] = st.number_input(
                            "SSTA DHW", value=st.session_state.manual_features["SSTA_DHW"],
                            help="SSTA Degree Heating Weeks",
                            key="ssta_dhw_outer", format="%.3f",
                        )
                    with c4:
                        st.session_state.manual_features["TSA"] = st.number_input(
                            "TSA", value=st.session_state.manual_features["TSA"],
                            help="Thermal Stress Anomaly",
                            key="tsa_outer", format="%.3f",
                        )
                        st.session_state.manual_features["TSA_DHW"] = st.number_input(
                            "TSA DHW", value=st.session_state.manual_features["TSA_DHW"],
                            help="Thermal Stress Anomaly Degree Heating Weeks",
                            key="tsa_dhw_outer", format="%.3f",
                        )

                if _inside_expander:
                    with st.expander("Click to manually input environmental data (optional)"):
                        _render_manual_fields()
                else:
                    _render_manual_fields()

                current_override_features = st.session_state.manual_features.copy()

                # ── RUN PREDICTION button at the very bottom for manual mode ──
                st.markdown("---")
                if st.button("RUN PREDICTION", type="primary", key="run_btn_manual"):
                    submitted = True
                else:
                    submitted = submitted   # keeps value from the form widget above
                    # If form button was already pressed submitted_inside carries it

        # ---------------------------------------------------------------
        # Trigger prediction
        # ---------------------------------------------------------------
        if submitted:
            st.session_state.is_loading = True
            st.session_state.run_prediction_flag = True

        if st.session_state.run_prediction_flag:
            st.session_state.run_prediction_flag = False

            run_prediction(
                input_lat=st.session_state.input_lat,
                input_lon=st.session_state.input_lon,
                input_date=st.session_state.input_date,
                prediction_type=st.session_state.prediction_type,
                override_features=current_override_features,
                uploaded_file=st.session_state.uploaded_file,
            )

    # --- RESULTS DISPLAY ---
    st.markdown("---")
    st.markdown("<h2 style='text-align:center;'>Results:</h2>", unsafe_allow_html=True)

    # Display Loader while thinking
    if st.session_state.is_loading:
        show_octopus_loader()

    if st.session_state.show_results and st.session_state.api_result:
        api_result = st.session_state.api_result



        # Display Prediction Result Card
        if "prediction" in api_result:
            prediction_data = api_result["prediction"]

            # --- Robust Classification Logic using Probability ---
            probability_bleached = prediction_data.get("probability_bleached", 0.0)
            probability_unbleached = prediction_data.get("probability_healthy", 0.0)

            risk = probability_bleached * 100

            if probability_bleached > 0.5:
                final_classification = "Bleached"
                color = "#f44336" # Red
                icon = "🔥"
            else:
                final_classification = "Healthy"
                color = "#4CAF50" # Green
                icon = "✅"

            level = "High Risk" if risk > 70 else ("Moderate Risk" if risk > 40 else "Low Risk")

            # Classification card
            border_color = "#E24B4A" if final_classification == "Bleached" else "#639922"
            icon = "🔥" if final_classification == "Bleached" else "🌿"
            badge_bg = "#FCEBEB" if final_classification == "Bleached" else "#EAF3DE"
            badge_text_color = "#A32D2D" if final_classification == "Bleached" else "#3B6D11"
            prob_healthy = probability_unbleached * 100

            result_col, fact_col = st.columns([1, 1])

            with result_col:
                st.markdown(f"""
                <div style="border: 0.5px solid #e0e0e0; border-left: 3px solid {border_color};
                    border-radius: 10px; padding: 1rem 1.25rem; display: flex;
                    align-items: center; justify-content: space-between; margin-bottom: 1.25rem;">
                <div>
                    <p style="font-size: 12px; color: #888; text-transform: uppercase;
                    letter-spacing: 0.05em; margin: 0 0 4px;">Classification</p>
                    <p style="font-size: 20px; font-weight: 500; margin: 0;">
                    {final_classification}
                    <span style="font-size: 12px; font-weight: 500; padding: 3px 10px;
                        border-radius: 99px; background: {badge_bg}; color: {badge_text_color};
                        margin-left: 8px;">{level}</span>
                    </p>
                </div>
                <span style="font-size: 28px;">{icon}</span>
                </div>

                <p style="font-size: 12px; color: #aaa; text-transform: uppercase;
                letter-spacing: 0.06em; margin-bottom: 10px;">Confidence</p>

                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 13px; color: #888; width: 90px;">Healthy</span>
                <div style="flex: 1; height: 6px; background: #f0f0f0; border-radius: 99px; overflow: hidden;">
                    <div style="width: {prob_healthy:.1f}%; height: 100%; background: #639922; border-radius: 99px;"></div>
                </div>
                <span style="font-size: 13px; font-weight: 500; width: 40px; text-align: right;">{prob_healthy:.1f}%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 13px; color: #888; width: 90px;">Bleached</span>
                <div style="flex: 1; height: 6px; background: #f0f0f0; border-radius: 99px; overflow: hidden;">
                    <div style="width: {risk:.1f}%; height: 100%; background: #E24B4A; border-radius: 99px;"></div>
                </div>
                <span style="font-size: 13px; font-weight: 500; width: 40px; text-align: right;">{risk:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

            with fact_col:
                fact = get_random_fact()
                st.markdown(f"""
                <div style="border: 0.5px solid #e0e0e0; border-left: 3px solid #888;
                    border-radius: 10px; padding: 1rem 1.25rem; margin-top: 0.5rem;">
                <p style="font-size: 12px; color: #888; text-transform: uppercase;
                    letter-spacing: 0.05em; margin: 0 0 8px;">Did you know?</p>
                <p style="font-size: 14px; color: var(--color-text-primary);
                    line-height: 1.6; margin: 0;">{fact}</p>
                </div>
                """, unsafe_allow_html=True)


            # Display Image and Metrics
            if is_image_only or is_fusion:
                img_col, metric_col = st.columns([1, 1])
                with img_col:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown("""
                                ##### Image Analyzed
                                """)
                    if st.session_state.uploaded_file:
                        st.image(st.session_state.uploaded_file, caption="User Upload")
            else:
                metric_col = st.container()

            with metric_col:
                prob_healthy = probability_unbleached * 100



            # --- FALLBACK INFORMATION (shown only on successful prediction) ---
            st.markdown("<br><br>", unsafe_allow_html=True)

            if st.session_state.show_results and st.session_state.fallback_info:
                with st.expander("🔍 Details on fallback strategy used"):
                    left_column, right_column = st.columns(2)
                    with left_column:
                        for variable, fb in st.session_state.fallback_info.items():
                            st.markdown(
                                f"""
                                <div style="
                                    background-color:#e3f2fd;
                                    padding:10px;
                                    border-radius:8px;
                                    margin-bottom:8px;
                                    border-left:6px solid #1976d2;
                                ">
                                    <b>{variable}</b><br>
                                    {fb}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    with right_column:
                        st.markdown(
                            "**Fallback strategy legend**  \n"
                            "**1**. Exact = the exact date and geocoordinates you provided were used  \n"
                            "**2**. Temporal = the date used differs from the one you provided by the indicated number of days  \n"
                            "**3**. Spatial nearest = the geocoordinates used differ from the ones you provided by the indicated number of kilometres  \n"
                            "**4**. Combined = a combination of strategy 2 and 3  \n"
                            "**5**. Nearest 4D = as in strategy 4 but with wider search parameters"
                        )


# --- FOOTER ---
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0 0.5rem;">
    <p style="font-size: 12px; color: #888; text-transform: uppercase;
       letter-spacing: 0.08em; margin-bottom: 1rem;">Data & Privacy Policy</p>
    <p style="font-size: 13px; color: var(--color-text-secondary); line-height: 1.8; max-width: 600px; margin: 0 auto;">
       All inputs (images, coordinates, environmental data) are used only for the immediate prediction request.
       Predictions are generated by machine learning models and may contain inaccuracies.
       No data is stored or logged — all processing occurs in-memory and is wiped after generating the prediction.
    </p>
    <p style="font-size: 12px; color: #aaa; margin-top: 1rem; letter-spacing: 0.04em;">
       NO DATA RETENTION · IN-MEMORY PROCESSING ONLY
    </p>
</div>
""", unsafe_allow_html=True)
