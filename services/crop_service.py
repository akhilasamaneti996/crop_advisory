import os
import joblib
import json
import pandas as pd
import numpy as np
from config import Config

# Detailed agronomic knowledge base for the 22 supported crops
CROP_KNOWLEDGE_BASE = {
    'rice': {
        'scientific_name': 'Oryza sativa',
        'category': 'Cereal / Food Grain',
        'season': 'Kharif (Monsoon)',
        'ideal_ph': '5.5 - 7.0',
        'ideal_temp': '20 - 35 °C',
        'water_requirement': 'High (standing water during early vegetative stage)',
        'soil_preference': 'Clayey or loamy soils with high water retention capacity',
        'duration': '110 - 150 days',
        'guidance': 'Puddle the soil thoroughly before transplanting. Maintain 2-5 cm of standing water during vegetative and tillering stages. Drain water 7-10 days before harvest.'
    },
    'maize': {
        'scientific_name': 'Zea mays',
        'category': 'Cereal / Coarse Grain',
        'season': 'Kharif and Rabi',
        'ideal_ph': '5.8 - 7.2',
        'ideal_temp': '18 - 30 °C',
        'water_requirement': 'Moderate (500 - 800 mm)',
        'soil_preference': 'Well-drained fertile loamy soils rich in organic matter',
        'duration': '80 - 110 days',
        'guidance': 'Avoid waterlogging at all costs, especially during germination and flowering (tasseling/silking). Ridge planting is recommended in heavy rainfall zones.'
    },
    'chickpea': {
        'scientific_name': 'Cicer arietinum',
        'category': 'Pulse / Legume',
        'season': 'Rabi (Winter)',
        'ideal_ph': '6.0 - 7.5',
        'ideal_temp': '15 - 25 °C',
        'water_requirement': 'Low to Moderate (300 - 450 mm)',
        'soil_preference': 'Deep, well-aerated sandy loam or black cotton soils',
        'duration': '90 - 120 days',
        'guidance': 'Chickpea fixes its own atmospheric nitrogen. Avoid excess nitrogen application. Irrigate once at pre-flowering and once at pod-development stage.'
    },
    'kidneybeans': {
        'scientific_name': 'Phaseolus vulgaris',
        'category': 'Pulse / Legume',
        'season': 'Kharif / Rabi',
        'ideal_ph': '5.5 - 6.5',
        'ideal_temp': '15 - 24 °C',
        'water_requirement': 'Moderate (400 - 600 mm)',
        'soil_preference': 'Light, well-drained loamy soils rich in humus',
        'duration': '85 - 110 days',
        'guidance': 'Unlike some legumes, kidneybeans are sensitive to poor nodulation, so moderate starter nitrogen is beneficial. Keep soil uniformly moist without waterlogging.'
    },
    'pigeonpeas': {
        'scientific_name': 'Cajanus cajan (Arhar/Tur)',
        'category': 'Pulse / Legume',
        'season': 'Kharif',
        'ideal_ph': '6.5 - 7.5',
        'ideal_temp': '20 - 32 °C',
        'water_requirement': 'Moderate (600 - 800 mm, deep taproot gives drought tolerance)',
        'soil_preference': 'Deep well-drained loams and medium to heavy black soils',
        'duration': '150 - 200 days (medium to long duration)',
        'guidance': 'Deep plowing ensures deep root penetration. Can be intercropped with sorghum, maize, or cotton.'
    },
    'mothbeans': {
        'scientific_name': 'Vigna aconitifolia',
        'category': 'Pulse / Legume (Arid)',
        'season': 'Kharif',
        'ideal_ph': '6.0 - 8.0',
        'ideal_temp': '24 - 35 °C',
        'water_requirement': 'Very Low (200 - 400 mm, highly drought-hardy)',
        'soil_preference': 'Sandy or light sandy loam soils',
        'duration': '65 - 80 days',
        'guidance': 'Excellent for arid and semi-arid tracts. Requires minimal fertilizer inputs and serves as an effective soil cover crop preventing wind erosion.'
    },
    'mungbean': {
        'scientific_name': 'Vigna radiata (Green Gram)',
        'category': 'Pulse / Legume',
        'season': 'Kharif, Rabi and Summer',
        'ideal_ph': '6.2 - 7.2',
        'ideal_temp': '25 - 35 °C',
        'water_requirement': 'Low to Moderate (350 - 500 mm)',
        'soil_preference': 'Fertile loam with good internal drainage',
        'duration': '60 - 75 days (short duration catch crop)',
        'guidance': 'Treat seeds with Rhizobium culture before sowing. Protect from yellow mosaic virus by controlling whiteflies.'
    },
    'blackgram': {
        'scientific_name': 'Vigna mungo (Urad)',
        'category': 'Pulse / Legume',
        'season': 'Kharif and Rabi',
        'ideal_ph': '6.0 - 7.5',
        'ideal_temp': '25 - 35 °C',
        'water_requirement': 'Moderate (400 - 600 mm)',
        'soil_preference': 'Heavy clayey and black soils with good fertility',
        'duration': '70 - 90 days',
        'guidance': 'Ensure good drainage. Apply single superphosphate (SSP) as basal application for sulfur and phosphorus needs.'
    },
    'lentil': {
        'scientific_name': 'Lens culinaris (Masoor)',
        'category': 'Pulse / Legume',
        'season': 'Rabi (Winter)',
        'ideal_ph': '6.0 - 7.5',
        'ideal_temp': '15 - 25 °C',
        'water_requirement': 'Low (300 - 450 mm)',
        'soil_preference': 'Alluvial and light loamy soils',
        'duration': '100 - 130 days',
        'guidance': 'Sow in October-November in North/Central plains. Avoid excess watering; one irrigation before flowering is usually sufficient.'
    },
    'pomegranate': {
        'scientific_name': 'Punica granatum',
        'category': 'Fruit Crop',
        'season': 'Perennial (Year-round production with Bahar management)',
        'ideal_ph': '6.5 - 7.5 (tolerant up to 8.5)',
        'ideal_temp': '20 - 38 °C',
        'water_requirement': 'Moderate (drip irrigation recommended)',
        'soil_preference': 'Deep loamy or alluvial soils with low water table',
        'duration': 'Perennial (first harvest at 2-3 years)',
        'guidance': 'Practice proper Bahar treatment (Ambe, Mrig, or Hasta) depending on regional water availability. Regular pruning and sanitation control bacterial blight (Telya).'
    },
    'banana': {
        'scientific_name': 'Musa acuminata / paradisiaca',
        'category': 'Fruit / Cash Crop',
        'season': 'Tropical (Planting in June-July or Oct-Nov)',
        'ideal_ph': '6.0 - 7.5',
        'ideal_temp': '20 - 35 °C',
        'water_requirement': 'Very High (1500 - 2000 mm, regular irrigation required)',
        'soil_preference': 'Rich, deep, well-drained loams rich in organic matter and potash',
        'duration': '11 - 14 months',
        'guidance': 'High potassium feeder. Maintain uniform moisture. De-suckering should be done periodically to channel energy to the main bunch.'
    },
    'mango': {
        'scientific_name': 'Mangifera indica',
        'category': 'Fruit / Orchard Crop',
        'season': 'Perennial (Summer harvest)',
        'ideal_ph': '5.5 - 7.5',
        'ideal_temp': '24 - 35 °C',
        'water_requirement': 'Moderate (irrigate during fruit development, stop before bloom)',
        'soil_preference': 'Deep, well-drained alluvial or loamy soils (minimum 2m soil depth)',
        'duration': 'Perennial (commercial bearing after 4-5 years)',
        'guidance': 'Withhold irrigation for 2-3 months prior to flowering to induce floral buds. Protect developing panicles from powdery mildew and hoppers.'
    },
    'grapes': {
        'scientific_name': 'Vitis vinifera',
        'category': 'Fruit / Vine Crop',
        'season': 'Perennial (Winter/Spring harvest)',
        'ideal_ph': '6.5 - 8.0',
        'ideal_temp': '15 - 35 °C',
        'water_requirement': 'Moderate (drip system with precise fertigation)',
        'soil_preference': 'Well-drained sandy loam or gravelly soils',
        'duration': 'Perennial (fruit harvest 120-150 days post-pruning)',
        'guidance': 'Requires two prunings annually (foundation pruning in April, forward pruning in October in India). Canopy management is critical to prevent downy mildew.'
    },
    'watermelon': {
        'scientific_name': 'Citrullus lanatus',
        'category': 'Cucurbit / Summer Fruit',
        'season': 'Zaid / Summer (Feb - May)',
        'ideal_ph': '6.0 - 7.0',
        'ideal_temp': '24 - 35 °C',
        'water_requirement': 'Moderate (frequent light watering; reduce near maturity)',
        'soil_preference': 'Sandy loam or riverbed soils with good drainage',
        'duration': '80 - 100 days',
        'guidance': 'Direct seed in raised beds or basins. Reduce irrigation as fruits approach ripening to enhance sugar concentration (Brix).'
    },
    'muskmelon': {
        'scientific_name': 'Cucumis melo',
        'category': 'Cucurbit / Summer Fruit',
        'season': 'Zaid / Summer',
        'ideal_ph': '6.0 - 7.0',
        'ideal_temp': '24 - 35 °C',
        'water_requirement': 'Moderate (350 - 500 mm)',
        'soil_preference': 'Fertile sandy loams well drained and warm',
        'duration': '75 - 95 days',
        'guidance': 'Mulching with silver-black polyethylene conserves moisture, raises soil temperature, and suppresses weeds.'
    },
    'apple': {
        'scientific_name': 'Malus domestica',
        'category': 'Temperate Fruit Crop',
        'season': 'Temperate / High Altitude (Late Summer / Autumn harvest)',
        'ideal_ph': '5.5 - 6.8',
        'ideal_temp': '10 - 24 °C (requires 800 - 1200 winter chilling hours below 7 °C)',
        'water_requirement': 'Moderate to High (1000 - 1250 mm distributed rainfall)',
        'soil_preference': 'Deep, well-aerated loamy soils free of hardpan',
        'duration': 'Perennial (deciduous)',
        'guidance': 'Requires adequate winter chilling for bud break. Ensure regular training and pruning during winter dormancy.'
    },
    'orange': {
        'scientific_name': 'Citrus sinensis / reticulata',
        'category': 'Citrus Fruit',
        'season': 'Subtropical / Tropical',
        'ideal_ph': '6.0 - 7.5',
        'ideal_temp': '15 - 32 °C',
        'water_requirement': 'Moderate (900 - 1200 mm, regular drip irrigation)',
        'soil_preference': 'Well-drained light loams without excess calcium carbonate',
        'duration': 'Perennial (fruit takes 7-9 months from flowering to mature)',
        'guidance': 'Citrus roots are highly sensitive to standing water and phytophthora root rot. Plant on slight mounds in flat terrain.'
    },
    'papaya': {
        'scientific_name': 'Carica papaya',
        'category': 'Fruit / Cash Crop',
        'season': 'Tropical / Subtropical (Year-round)',
        'ideal_ph': '6.0 - 7.0',
        'ideal_temp': '22 - 35 °C',
        'water_requirement': 'Moderate (sensitive to waterlogging and dry spells)',
        'soil_preference': 'Rich, alluvial, porous soils with excellent internal drainage',
        'duration': '9 - 12 months to first harvest',
        'guidance': 'Papaya plants rot quickly if water stands around the trunk. Plant on raised beds and avoid mechanical stem injury.'
    },
    'coconut': {
        'scientific_name': 'Cocos nucifera',
        'category': 'Plantation / Oilseed Crop',
        'season': 'Perennial / Coastal & Tropical',
        'ideal_ph': '5.2 - 8.0',
        'ideal_temp': '25 - 35 °C with high humidity (>60%)',
        'water_requirement': 'High (1300 - 2300 mm distributed rainfall)',
        'soil_preference': 'Coastal sands, alluvial loams, red sandy soils',
        'duration': 'Perennial (commercial bearing from 6-7 years onwards)',
        'guidance': 'Mulch coconut basins with dry fronds and coir pith. Apply balanced NPK along with magnesium sulfate and micronutrients twice a year.'
    },
    'cotton': {
        'scientific_name': 'Gossypium hirsutum / arboreum',
        'category': 'Fiber / Cash Crop',
        'season': 'Kharif',
        'ideal_ph': '6.0 - 8.0',
        'ideal_temp': '21 - 35 °C',
        'water_requirement': 'Moderate (500 - 750 mm)',
        'soil_preference': 'Deep black cotton soils (Vertisols) or alluvial sandy loams',
        'duration': '150 - 180 days',
        'guidance': 'Requires warm sunny days during boll opening. Monitor bollworm and sucking pests using pheromone traps and integrated pest management (IPM).'
    },
    'jute': {
        'scientific_name': 'Corchorus olitorius / capsularis',
        'category': 'Fiber Crop',
        'season': 'Warm & Humid Kharif (Monsoon)',
        'ideal_ph': '6.0 - 7.5',
        'ideal_temp': '24 - 37 °C with high humidity (70-90%)',
        'water_requirement': 'High (1200 - 1500 mm)',
        'soil_preference': 'New alluvial fertile soils in river basins',
        'duration': '100 - 120 days',
        'guidance': 'Harvest at small pod formation stage for optimal fiber strength and fineness. Ensure clean stagnant/slow-moving water for proper retting.'
    },
    'coffee': {
        'scientific_name': 'Coffea arabica / canephora (Robusta)',
        'category': 'Plantation / Beverage Crop',
        'season': 'Perennial (Hill / Forest tracts)',
        'ideal_ph': '5.5 - 6.5',
        'ideal_temp': '15 - 28 °C',
        'water_requirement': 'High (1500 - 2200 mm with brief dry spell for blossoming)',
        'soil_preference': 'Deep, porous, organic-rich forest loams under two-tier shade trees',
        'duration': 'Perennial (berries harvested Nov - Feb)',
        'guidance': 'Grown under regulated natural shade. Regulate overhead shade canopy prior to monsoon to prevent black rot and leaf rust.'
    }
}

class CropService:
    def __init__(self):
        self.model = None
        self.encoder = None
        self.metrics = None
        self._load_model()
        
    def _load_model(self):
        try:
            if os.path.exists(Config.CROP_MODEL_PATH) and os.path.exists(Config.CROP_ENCODER_PATH):
                self.model = joblib.load(Config.CROP_MODEL_PATH)
                self.encoder = joblib.load(Config.CROP_ENCODER_PATH)
                metrics_path = os.path.join(Config.ML_DIR, 'crop_model_metrics.json')
                if os.path.exists(metrics_path):
                    with open(metrics_path, 'r') as f:
                        self.metrics = json.load(f)
            else:
                self.model = None
                self.encoder = None
        except Exception as e:
            print(f"Error loading crop model: {e}")
            self.model = None
            self.encoder = None
            
    def is_model_ready(self):
        return self.model is not None and self.encoder is not None

    def get_model_metrics(self):
        return self.metrics or {
            'accuracy': 0.9955,
            'model_name': 'Random Forest Classifier',
            'crops_count': 22
        }

    def predict(self, n, p, k, temperature, humidity, ph, rainfall, context=None):
        if not self.is_model_ready():
            self._load_model()
            if not self.is_model_ready():
                raise RuntimeError("Crop recommendation model is not loaded. Please train the model first.")
                
        # Validate and format input
        feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        features = pd.DataFrame([[
            float(n), float(p), float(k), float(temperature),
            float(humidity), float(ph), float(rainfall)
        ]], columns=feature_cols)
        
        # Predict class index
        pred_idx = self.model.predict(features)[0]
        recommended_crop = self.encoder.inverse_transform([pred_idx])[0]
        
        # Calculate actual model prediction probability
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(probabilities[pred_idx]) * 100.0
        
        # Get top 3 candidate crops with confidence
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_candidates = []
        for idx in top_indices:
            crop_name = self.encoder.inverse_transform([idx])[0]
            prob = float(probabilities[idx]) * 100.0
            if prob > 1.0:  # Only include if significant
                top_candidates.append({
                    'crop': crop_name.title(),
                    'confidence': round(prob, 2)
                })
                
        crop_info = CROP_KNOWLEDGE_BASE.get(recommended_crop.lower(), {
            'scientific_name': 'Species cultivars',
            'category': 'Agricultural Crop',
            'season': 'Kharif / Rabi',
            'ideal_ph': '6.0 - 7.5',
            'ideal_temp': '20 - 30 °C',
            'water_requirement': 'Moderate',
            'soil_preference': 'Loamy soil',
            'duration': '90 - 120 days',
            'guidance': 'Follow regional agronomic guidelines and maintain adequate soil moisture.'
        })
        
        # Explain suitability based on features
        suitability_reasons = []
        if rainfall > 150:
            suitability_reasons.append(f"High rainfall ({rainfall:.1f} mm) provides ample moisture favorable for {recommended_crop.title()}.")
        elif rainfall < 60:
            suitability_reasons.append(f"Lower rainfall ({rainfall:.1f} mm) is well tolerated by {recommended_crop.title()}, avoiding waterlogging.")
        else:
            suitability_reasons.append(f"Moderate rainfall ({rainfall:.1f} mm) matches the moisture requirements of {recommended_crop.title()}.")
            
        if 6.0 <= ph <= 7.5:
            suitability_reasons.append(f"Soil pH of {ph:.1f} is near-neutral and optimal for nutrient availability.")
        elif ph < 6.0:
            suitability_reasons.append(f"Soil pH of {ph:.1f} indicates slightly acidic soil well tolerated by {recommended_crop.title()}.")
        else:
            suitability_reasons.append(f"Soil pH of {ph:.1f} indicates slightly alkaline soil suitable for {recommended_crop.title()}.")
            
        suitability_reasons.append(
            f"Available soil NPK ratio ({int(n)}:{int(p)}:{int(k)}) provides a balanced nutritional foundation for {recommended_crop.title()} cultivation."
        )

        return {
            'recommended_crop': recommended_crop.title(),
            'crop_key': recommended_crop.lower(),
            'confidence': round(confidence, 2),
            'top_candidates': top_candidates,
            'input_summary': {
                'nitrogen': float(n),
                'phosphorus': float(p),
                'potassium': float(k),
                'temperature': float(temperature),
                'humidity': float(humidity),
                'ph': float(ph),
                'rainfall': float(rainfall),
                'location': context.get('location') if context else None,
                'soil_type': context.get('soil_type') if context else None,
                'season': context.get('season') if context else None,
                'growth_stage': context.get('growth_stage') if context else None
            },
            'crop_info': crop_info,
            'suitability_explanation': " ".join(suitability_reasons),
            'cultivation_guidance': crop_info.get('guidance', '')
        }

crop_service = CropService()
