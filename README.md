# A Multimodal Approach to Adaptive Crop Advisory

An integrated, full-stack agricultural assistance web application that combines soil chemistry, computer vision leaf pathology, live weather intelligence, and natural language processing into an explainable, rule-based agronomic decision engine.

---

## 1. Project Overview

Traditional crop advisory systems often provide static, generic agricultural recommendations that fail to reflect the dynamic reality of an active farm. **Adaptive Crop Advisory** bridges this gap through a **multimodal approach**:

1. **Soil & Environmental Telemetry:** Nitrogen (N), Phosphorus (P), Potassium (K), Soil pH, temperature, relative humidity, and rainfall.
2. **Plant Pathology Computer Vision:** Close-up leaf imagery analyzed via deep convolutional neural networks (MobileNetV2) to identify early and late foliar blights.
3. **Meteorological Intelligence:** Microclimate data integrated via the OpenWeather REST API, producing actionable alerts for fungal spore growth and chemical spraying feasibility.
4. **Farmer Voice & Chatbot Assistant:** Multilingual intent-classified natural language assistant (English, Telugu, Hindi) supporting browser voice recognition and text-to-speech.
5. **Adaptive Decision Engine:** A rule-based synthesis layer that fuses these modalities into an explainable, personalized action plan for irrigation timing, fertilizer application, and disease mitigation.

---

## 2. Problem Statement

Farmers in diverse agro-ecological zones face major vulnerabilities:
- **Misaligned Crop Selection:** Planting crops ill-suited to specific soil mineral concentrations or microclimates, leading to yield loss.
- **Indiscriminate Chemical Usage:** Applying pesticides when wind speeds cause drift or rainfall causes runoff, wasting capital and contaminating local watersheds.
- **Delayed Disease Intervention:** Inability to identify fungal leaf symptoms (such as concentric target rings of early blight) before widespread defoliation occurs.
- **Language and Technical Barriers:** Complex agricultural advisories often lack intuitive local language (Telugu, Hindi) interfaces or voice interaction for non-technical users.

---

## 3. Objectives

- Develop a machine learning crop recommendation model trained on genuine soil and climate data across 22 crop classes with >99% accuracy.
- Implement an image-based plant disease detection pipeline using transfer learning (MobileNetV2) to diagnose foliar pathogens and provide cultural and chemical remedies.
- Integrate real-time weather analytics to warn farmers against high-humidity fungal risk and high-wind spray drift.
- Construct a multilingual farmer assistant supporting English, Telugu, and Hindi with Web Speech API integration.
- Implement an explainable, rule-based decision engine (`advisory_engine.py`) providing personalized irrigation, fertilizer, and disease guidance without fabricating arbitrary numbers.

---

## 4. System Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    CLIENT BROWSER                                       |
|  [Responsive UI (Bootstrap 5, CSS3)]  [Voice Web Speech API]  [Chart.js Visualizations]  |
+--------------------------------------------+--------------------------------------------+
                                             | HTTP / REST (JSON & Multipart)
                                             v
+-----------------------------------------------------------------------------------------+
|                                    FLASK BACKEND                                        |
|  routes/                                                                                |
|  - dashboard_routes.py  - crop_routes.py     - disease_routes.py                        |
|  - weather_routes.py    - chatbot_routes.py  - advisory_routes.py                       |
+--------------------------------------------+--------------------------------------------+
                                             |
            +--------------------------------+-------------------------------+
            |                                |                               |
            v                                v                               v
+-----------------------+  +----------------------------------+  +------------------------+
|   MACHINE LEARNING    |  |     ADAPTIVE DECISION ENGINE     |  |       DATABASE         |
|   & DEEP LEARNING     |  |       (services/advisory_engine) |  |   (SQLite / SQLAlchemy)|
|                       |  |                                  |  |                        |
| - Random Forest Model |  | Evaluates Multimodal Rules:      |  | - Crop History         |
|   (22 Crops, 99.5%)   |  | - Fungal Disease + Humidity Alert|  | - Disease History      |
| - MobileNetV2 CNN     |  | - Expected Rainfall Irrigation   |  | - Farmer Queries       |
|   (Foliar Pathology)  |  | - Wind Speed Chemical Drift      |  | - Advisory Plans       |
| - TF-IDF NLP Pipeline |  | - Phenological Growth Stages     |  |                        |
|   (Multilingual)      |  | - Soil NPK & pH Adjustments      |  +------------------------+
+-----------------------+  +----------------------------------+
            |                                |
            v                                v
+-----------------------+  +----------------------------------+
|   DATASETS & MODELS   |  |        EXTERNAL SERVICES         |
| - Crop_recommendation |  | - OpenWeather REST API           |
| - PlantVillage Sample |  | - Browser SpeechRecognition      |
| - Chatbot Intents     |  | - Browser SpeechSynthesis (TTS)  |
+-----------------------+  +----------------------------------+
```

---

## 5. Technology Stack

- **Backend:** Python 3.12, Flask 3.1, Werkzeug
- **Database:** SQLite with SQLAlchemy ORM (Flask-SQLAlchemy)
- **Machine Learning:** Scikit-learn, Random Forest Classifier, Pandas, NumPy, Joblib
- **Deep Learning & Vision:** TensorFlow 2.19 / Keras, MobileNetV2 Transfer Learning, Pillow (PIL)
- **Natural Language Processing:** Scikit-learn TF-IDF Vectorizer with Sublinear Term Frequency and Multi-Language Character N-Grams + Logistic Regression
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4, Font Awesome 6.5
- **Testing:** Pytest 9.1

---

## 6. Project Directory Structure

```
crop_advisory/
├── app.py                         # Application factory, blueprint registration & health check
├── config.py                      # Environment configuration & model paths
├── database.py                    # SQLAlchemy initialization
├── models.py                      # Database models (Crop, Disease, Query, Advisory History)
├── requirements.txt               # Production Python dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusion rules
├── README.md                      # Comprehensive project documentation
├── routes/                        # Modular Flask API & View Blueprints
│   ├── dashboard_routes.py        # Dashboard stats, activities, and landing page
│   ├── crop_routes.py             # Crop recommendation form and REST endpoints
│   ├── disease_routes.py          # Plant pathology upload and inference endpoints
│   ├── weather_routes.py          # Meteorological data and agricultural alerts
│   ├── chatbot_routes.py          # Multilingual chat handling and session history
│   └── advisory_routes.py         # Multimodal decision engine integration endpoint
├── services/                      # Core business logic and ML engines
│   ├── crop_service.py            # Crop prediction, candidate ranking, agronomic advice
│   ├── disease_service.py         # MobileNetV2 image processing & pathology knowledge
│   ├── weather_service.py         # OpenWeather API caller & rule-based alerts
│   ├── chatbot_service.py         # NLP classification and multilingual response selection
│   └── advisory_engine.py         # Explainable multimodal decision engine
├── ml_models/                     # Persisted trained models & evaluation metrics
│   ├── crop_model.pkl             # Trained Random Forest classifier
│   ├── crop_label_encoder.pkl     # Scikit-learn label encoder for 22 crops
│   ├── crop_model_metrics.json    # Genuine accuracy (99.55%), precision, recall
│   ├── disease_model.keras        # Trained MobileNetV2 Keras model
│   ├── disease_classes.json       # PlantVillage class names and metadata
│   ├── disease_model_metrics.json # Loss and validation accuracy metrics
│   ├── chatbot_model.pkl          # Trained TF-IDF + Logistic Regression pipeline
│   └── chatbot_metrics.json       # Chatbot intent metadata and CV scores
├── training/                      # Independent model training pipelines
│   ├── train_crop_model.py        # 80/20 train-test split, training & evaluation
│   ├── train_disease_model.py     # MobileNetV2 transfer learning training script
│   └── train_chatbot_model.py     # Intent classifier training on multilingual patterns
├── utils/                         # Validation, localization, and image helpers
│   ├── image_processing.py        # Upload sanitization, RGB conversion, resizing to 224x224
│   ├── translation.py             # English, Telugu, and Hindi UI string dictionaries
│   └── validators.py              # Strict input range validation for NPK, pH, and climate
├── templates/                     # Semantic HTML5 Jinja2 Templates
│   ├── base.html                  # Global layout, agricultural navbar, footer, language select
│   ├── index.html                 # Landing page with hero section and system overview
│   ├── dashboard.html             # Farmer dashboard with real-time stats & Chart.js widgets
│   ├── crop_recommendation.html   # Crop input form with presets and recommendation cards
│   ├── disease_detection.html     # Leaf drag-and-drop upload and pathology result viewer
│   ├── weather.html               # Live weather cards, forecast chart, and spraying alerts
│   ├── chatbot.html               # Multilingual conversational interface with microphone
│   └── advisory.html              # Comprehensive multimodal decision engine workspace
├── static/                        # Static assets
│   ├── css/style.css              # Custom agricultural green theme stylesheet
│   └── js/                        # Modular frontend scripts
│       ├── main.js                # Global language switcher and toast notifications
│       ├── dashboard.js           # Live statistics and Chart.js chart rendering
│       ├── crop.js                # Form validation, prediction request, context export
│       ├── disease.js             # Drag-drop upload, image preview, pathology rendering
│       ├── weather.js             # Weather API consumption, forecast charts, alerts
│       ├── chatbot.js             # Web Speech recognition and synthesis, message bubbles
│       └── advisory.js            # Multimodal data synthesis and action plan view
├── data/
│   ├── datasets/                  # Datasets used by training scripts
│   │   ├── Crop_recommendation.csv# 2,200 rows covering 22 agricultural crops
│   │   ├── plant_village_sample/  # Curated PlantVillage leaf image folders
│   │   └── chatbot_intents.json   # Multilingual intent patterns and responses
│   └── uploads/                   # Secured directory for farmer uploaded leaf images
└── tests/                         # Pytest test suite (25 automated unit & integration tests)
    ├── test_crop.py               # Crop model prediction, validation, and metadata tests
    ├── test_disease.py            # Image file validation, supported classes, inference tests
    ├── test_weather.py            # Missing key handling and rule advisory tests
    ├── test_chatbot.py            # Multilingual intent classification & session tests
    ├── test_advisory.py           # Multimodal decision rules and risk scoring tests
    └── test_routes.py             # Flask HTTP endpoint integration tests
```

---

## 7. Dataset Information

1. **Crop Recommendation Dataset:**
   - **Records:** 2,200 rows, 8 features (`N, P, K, temperature, humidity, ph, rainfall, label`).
   - **Target Classes (22 crops):** Apple, Banana, Blackgram, Chickpea, Coconut, Coffee, Cotton, Grapes, Jute, Kidneybeans, Lentil, Maize, Mango, Mothbeans, Mungbean, Muskmelon, Orange, Papaya, Pigeonpeas, Pomegranate, Rice, Watermelon.
   - **Quality:** Zero missing values. Split into 80% training (1,760 samples) and 20% testing (440 samples).
   - **Evaluated Performance:** **99.55% test accuracy**, **99.55% F1-score**.

2. **Plant Leaf Pathology Dataset:**
   - **Source:** PlantVillage benchmark dataset.
   - **Supported Classes:**
     - Tomato Early Blight (*Alternaria linariae*)
     - Tomato Late Blight (*Phytophthora infestans*)
     - Tomato Healthy Leaf
     - Potato Early Blight (*Alternaria solani*)
     - Potato Late Blight (*Phytophthora infestans*)
     - Potato Healthy Leaf
   - **Image Format:** 224 × 224 × 3 RGB images normalized to `[-1, 1]` for MobileNetV2.

3. **Chatbot Intent Dataset:**
   - **Intents:** 7 categories (`disease_query`, `fertilizer_query`, `irrigation_query`, `crop_recommendation_query`, `weather_query`, `general_farming`, `greeting`).
   - **Patterns:** Over 100 documented query variants in English, Telugu, and Hindi.

---

## 8. Installation & Setup (Windows)

### Step 1: Open Terminal in Project Directory
Open PowerShell or Command Prompt:
```powershell
cd c:\Users\ashwi\Documents\crop_advisory
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` in Notepad and add your OpenWeather API key (optional for live weather):
```
OPENWEATHER_API_KEY=your_actual_key_here
```

### Step 4: Verify or Re-Train Machine Learning Models
Pre-trained models are already saved in `ml_models/`. You can re-train any model at any time:
```powershell
# 1. Train Crop Recommendation Random Forest Model (Evaluates and outputs 99.55% accuracy)
python training/train_crop_model.py

# 2. Train Chatbot Intent Classifier (Multilingual TF-IDF + Logistic Regression)
python training/train_chatbot_model.py

# 3. Train Disease Detection Model (MobileNetV2 Transfer Learning)
python training/train_disease_model.py --epochs 5 --batch_size 8
```

### Step 5: Run Automated Pytest Suite
Run the 25 backend unit and integration tests:
```powershell
pytest tests/ -v
```

### Step 6: Start the Web Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 9. API Endpoint Reference

| Method | Endpoint | Description | Expected Payload / Params |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Application Landing Page | None |
| `GET` | `/dashboard` | Farmer Dashboard Interface | None |
| `GET` | `/crop-recommendation` | Crop Recommendation Module | None |
| `GET` | `/disease-detection` | Plant Pathology Module | None |
| `GET` | `/weather` | Weather Intelligence Dashboard | None |
| `GET` | `/chatbot` | Farmer Assistant Chat Interface | None |
| `GET` | `/advisory` | Multimodal Decision Engine Workspace | None |
| `GET` | `/api/health` | System health check (DB, ML models, APIs) | None |
| `GET` | `/api/dashboard/stats` | Live counters, activity feed, and chart data | None |
| `POST`| `/api/crop/recommend` | Runs Random Forest crop recommendation | JSON: `{nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, location, soil_type, season, growth_stage}` |
| `POST`| `/api/disease/predict` | Analyzes uploaded leaf image via MobileNetV2 | `multipart/form-data`: `image` (JPG/JPEG/PNG) |
| `GET` | `/api/weather` | Retrieves weather & rule-based farming alerts | Query param: `?city=Hyderabad` |
| `POST`| `/api/chatbot/message` | Classifies question intent & returns answer | JSON: `{message, language, session_id}` |
| `POST`| `/api/advisory/generate` | Synthesizes multimodal farm recommendations | JSON: `{crop_name, growth_stage, soil, weather, disease, farmer_query}` |
| `GET` | `/api/history/crops` | Retrieves past crop recommendations | Query param: `?limit=10` |
| `GET` | `/api/history/diseases`| Retrieves past leaf diagnoses | Query param: `?limit=10` |
| `GET` | `/api/history/advisories`| Retrieves past synthesized advisories | Query param: `?limit=10` |

---

## 10. Adaptive Decision Logic Examples

The decision engine in `services/advisory_engine.py` implements explainable rules combining all modalities:

- **Fungal Pathogen + High Humidity:**
  - *Trigger:* If disease diagnosis is Early/Late Blight AND atmospheric humidity exceeds 75%.
  - *Guidance:* Elevates farm risk to **Critical**. Instructs the farmer to cease overhead irrigation immediately, prune infected lower canopy leaves to reduce spore dispersal, and apply protective contact fungicides early in the morning.
- **Expected Precipitation:**
  - *Trigger:* If forecast precipitation is detected or observed rainfall > 0.5 mm.
  - *Guidance:* Pauses irrigation pump schedules. Warns against top-dressing granular fertilizers to prevent nitrogen runoff and leaching.
- **High Wind Velocity Spray Drift Alert:**
  - *Trigger:* Wind velocity exceeds 15 km/h.
  - *Guidance:* Marks spraying feasibility as **Unfavorable**. Postpones foliar chemical sprays to prevent non-target spray drift.
- **Soil pH Correction:**
  - *Trigger:* Soil pH < 5.8 (acidic) or > 7.8 (alkaline).
  - *Guidance:* Warns of phosphorus lockup in acidic soil and suggests agricultural lime; warns of iron/zinc micronutrient deficiency in alkaline soils.
- **Phenological Growth Stage Synchronization:**
  - *Seedling:* Prioritizes phosphorus for root establishment; warns against waterlogging to prevent damping-off.
  - *Flowering:* Highlights moisture-sensitivity to prevent floral abortion; shifts nutrition towards potassium.
  - *Maturity:* Advises tapering water 10-14 days before harvest to promote uniform ripening.

---

## 11. Known Limitations

- **Live Weather Requires API Key:** The system does not fabricate synthetic live weather. Without `OPENWEATHER_API_KEY` set in `.env`, the weather module displays a clear configuration banner while remaining functional for all other modules.
- **Leaf Pathology Scope:** The included MobileNetV2 model is trained on standard representative PlantVillage classes for Potato and Tomato (Early Blight, Late Blight, Healthy Leaf). Additional crop classes can be added by running `train_disease_model.py` against the full multi-gigabyte PlantVillage dataset.
- **Voice APIs:** Browser SpeechRecognition and SpeechSynthesis depend on native browser support (Google Chrome and Microsoft Edge recommended). Fallback text input is always available.

---

## 12. Future Enhancements

- **IoT Telemetry Ingestion:** Integration with ESP32 or LoRaWAN soil moisture and NPK sensor probes for automated real-time field data streaming.
- **Satellite Vegetation Indices:** Incorporating Sentinel-2 or Landsat NDVI (Normalized Difference Vegetation Index) maps to track field-level biomass health over time.
- **Direct Marketplace Integration:** Linking recommended bio-pesticides and organic fertilizers to verified regional agricultural input cooperatives.
- **Offline Progressive Web App (PWA):** Caching agronomic advisory rules and models locally for rural fields with intermittent mobile connectivity.

---

*Adaptive Crop Advisory — Developed as a genuine software engineering project for sustainable, data-driven agricultural assistance.*

#   c r o p _ a d v i s o r y  
 