import json

class AdaptiveAdvisoryEngine:
    """
    Rule-based, explainable agricultural decision engine that synthesizes
    multimodal inputs: crop characteristics, soil chemistry, growth stage,
    weather conditions, and disease diagnoses to produce actionable advisories.
    """
    
    def generate_advisory(self, data):
        """
        data dictionary can contain:
        - crop_name (str)
        - growth_stage (str: 'Seedling / Early', 'Vegetative', 'Flowering / Reproductive', 'Maturity / Harvesting')
        - soil: {nitrogen, phosphorus, potassium, ph, soil_type, moisture}
        - weather: {temperature, humidity, wind_speed_kmh, rainfall_mm, weather_main, upcoming_rain}
        - disease: {detected_crop, predicted_disease, is_healthy, confidence, pathogen_type}
        - farmer_query: str (optional)
        """
        crop_name = (data.get('crop_name') or 'General Crop').strip().title()
        growth_stage = (data.get('growth_stage') or 'Vegetative').strip()
        soil = data.get('soil') or {}
        weather = data.get('weather') or {}
        disease = data.get('disease') or {}
        farmer_query = (data.get('farmer_query') or '').lower()
        
        decision_factors = []
        
        # 1. Evaluate Irrigation Advice
        irrigation_advice = self._evaluate_irrigation(
            crop_name, growth_stage, soil, weather, decision_factors
        )
        
        # 2. Evaluate Fertilizer Advice
        fertilizer_advice = self._evaluate_fertilizer(
            crop_name, growth_stage, soil, weather, decision_factors
        )
        
        # 3. Evaluate Disease & Plant Health Advice
        disease_advice = self._evaluate_disease(
            crop_name, disease, weather, farmer_query, decision_factors
        )
        
        # 4. Evaluate Weather-Related Farming Operations
        weather_advice = self._evaluate_weather_operations(
            weather, decision_factors
        )
        
        # 5. General & Seasonal Crop Care
        general_advice = self._evaluate_general_care(
            crop_name, growth_stage, soil, decision_factors
        )
        
        # Calculate overall farm risk level
        risk_level = self._compute_risk_level(weather, disease)

        return {
            'crop_name': crop_name,
            'growth_stage': growth_stage,
            'risk_level': risk_level,
            'decision_factors': decision_factors,
            'irrigation_advice': irrigation_advice,
            'fertilizer_advice': fertilizer_advice,
            'disease_advice': disease_advice,
            'weather_advice': weather_advice,
            'general_advice': general_advice
        }

    def _evaluate_irrigation(self, crop, stage, soil, weather, factors):
        temp = float(weather.get('temperature', 25.0) or 25.0)
        humidity = float(weather.get('humidity', 60.0) or 60.0)
        rain_mm = float(weather.get('rainfall_mm', 0.0) or 0.0)
        upcoming_rain = weather.get('upcoming_rain', False) or rain_mm > 0.5
        soil_type = (soil.get('soil_type') or 'Loamy').lower()
        
        advice_points = []
        
        # Factor: Expected Rain
        if upcoming_rain:
            factors.append("Expected rainfall in the forecast warrants withholding irrigation.")
            advice_points.append(
                f"Rainfall is detected or expected ({rain_mm:.1f} mm). Do not run irrigation pumps today. "
                "Check soil moisture 24 hours after rainfall before resuming irrigation to avoid root asphyxiation."
            )
        else:
            # Factor: Temperature and Evaporation
            if temp > 35:
                factors.append(f"High ambient temperature ({temp:.1f}°C) elevates crop evapotranspiration.")
                advice_points.append(
                    f"Due to elevated temperatures ({temp:.1f}°C), evaporative loss is high. "
                    "Irrigate during early morning (6:00 - 8:30 AM) or late evening to minimize evaporation."
                )
            elif temp < 15:
                advice_points.append(
                    f"Cool ambient temperature ({temp:.1f}°C) reduces evapotranspiration. Water moderately."
                )
                
        # Factor: Growth Stage Moisture Needs
        stage_lower = stage.lower()
        if 'seedling' in stage_lower or 'early' in stage_lower:
            factors.append("Early seedling stage requires delicate moisture balance.")
            advice_points.append(
                "Seedling Stage: Roots are shallow and sensitive. Maintain light, frequent watering; avoid heavy water pooling which causes damping-off."
            )
        elif 'flower' in stage_lower or 'reproductive' in stage_lower or 'pod' in stage_lower:
            factors.append("Flowering/reproductive stage is critical moisture-sensitive period.")
            advice_points.append(
                "Flowering / Fruit-set Stage: This is the most moisture-sensitive period. Even mild water stress now causes flower abortion and poor fruit set. Keep soil uniformly moist."
            )
        elif 'harvest' in stage_lower or 'maturity' in stage_lower:
            factors.append("Maturity stage requires reduced moisture.")
            advice_points.append(
                "Maturity / Harvesting Stage: Withhold or drastically reduce irrigation 10-14 days before harvest to promote uniform ripening and prevent fruit splitting."
            )
        else:
            advice_points.append(
                "Vegetative Stage: Provide regular irrigations according to soil drying cycles to support active leaf and canopy growth."
            )

        # Factor: Soil drainage characteristic
        if 'sand' in soil_type:
            factors.append("Sandy soil has rapid percolation and low water holding capacity.")
            advice_points.append(
                "Sandy Soil: Water drains rapidly. Use frequent, smaller irrigations or drip emitters to maintain moisture in root zone."
            )
        elif 'clay' in soil_type or 'black' in soil_type:
            factors.append("Heavy clay soil has high water retention and slow drainage.")
            advice_points.append(
                "Clayey Soil: Soil retains water for long periods. Allow the top 2-3 inches to dry out slightly before the next watering to prevent root rot."
            )

        return " ".join(advice_points)

    def _evaluate_fertilizer(self, crop, stage, soil, weather, factors):
        n = float(soil.get('nitrogen', 50.0) or 50.0)
        p = float(soil.get('phosphorus', 40.0) or 40.0)
        k = float(soil.get('potassium', 40.0) or 40.0)
        ph = float(soil.get('ph', 6.5) or 6.5)
        rain_mm = float(weather.get('rainfall_mm', 0.0) or 0.0)
        upcoming_rain = weather.get('upcoming_rain', False) or rain_mm > 0.5
        
        advice_points = []
        
        # Weather constraint on application
        if upcoming_rain:
            factors.append("Forecast rainfall prohibits surface fertilizer application.")
            advice_points.append(
                "Weather Warning: Delay top-dressing granular fertilizers. Heavy rain causes surface runoff and nitrogen leaching into local waterways."
            )
            
        # Soil pH analysis
        if ph < 5.8:
            factors.append(f"Acidic soil pH ({ph:.1f}) reduces phosphorus and calcium availability.")
            advice_points.append(
                f"Soil is acidic (pH {ph:.1f}). Phosphorus gets locked in acidic soils. Consider applying agricultural lime (calcium carbonate) or dolomite as per soil testing recommendations to normalize pH."
            )
        elif ph > 7.8:
            factors.append(f"Alkaline soil pH ({ph:.1f}) reduces iron and zinc micronutrient uptake.")
            advice_points.append(
                f"Soil is alkaline (pH {ph:.1f}). Iron and zinc availability may be restricted. Apply well-decomposed organic farmyard manure or gypsum, and use foliar micronutrient sprays if interveinal chlorosis appears."
            )
        else:
            advice_points.append(
                f"Soil pH ({ph:.1f}) is within the optimum neutral range (6.0 - 7.5), facilitating efficient macro- and micronutrient uptake."
            )

        # Nutrient level & Growth Stage matching
        stage_lower = stage.lower()
        if 'seedling' in stage_lower or 'early' in stage_lower:
            factors.append("Early growth requires phosphorus for vigorous root architecture.")
            advice_points.append(
                "Basal / Early Stage: Prioritize phosphorus and organic compost at land preparation to stimulate rapid root branching and mycorrhizal colonization. Apply starter nitrogen in moderation."
            )
        elif 'flower' in stage_lower or 'reproductive' in stage_lower:
            factors.append("Reproductive stage demands potassium and balanced phosphorus.")
            advice_points.append(
                "Reproductive Stage: Increase potassium supply to support flower retention, carbohydrate transport, and grain/fruit filling. Avoid heavy nitrogen top-dressing now, which induces vegetative leafy growth over fruiting."
            )
        elif 'harvest' in stage_lower or 'maturity' in stage_lower:
            advice_points.append(
                "Ripening Stage: Stop chemical fertilizer applications. Allow crop to utilize existing internal nutrients for natural ripening."
            )
        else:
            # Vegetative
            if n < 40:
                factors.append(f"Low soil nitrogen ({n:.0f}) observed.")
                advice_points.append(
                    f"Soil nitrogen is low ({n:.0f}). Provide split top-dressing of organic compost or recommended nitrogenous fertilizer in 2-3 installments to support active tillering and branching."
                )
            elif n > 120:
                factors.append(f"High soil nitrogen ({n:.0f}) observed.")
                advice_points.append(
                    f"Soil nitrogen is abundant ({n:.0f}). Refrain from adding synthetic nitrogen, as excessive nitrogen causes succulent growth vulnerable to insect pests and stem lodging."
                )
            else:
                advice_points.append(
                    f"Soil NPK values ({int(n)}:{int(p)}:{int(k)}) are balanced. Maintain maintenance doses of organic compost."
                )

        advice_points.append(
            "General Notice: Always base chemical fertilizer quantities on accredited laboratory soil test reports rather than generalized blanket estimates."
        )
        return " ".join(advice_points)

    def _evaluate_disease(self, crop, disease, weather, farmer_query, factors):
        humidity = float(weather.get('humidity', 60.0) or 60.0)
        temp = float(weather.get('temperature', 25.0) or 25.0)
        
        disease_name = disease.get('predicted_disease', '') or ''
        is_healthy = disease.get('is_healthy', False)
        
        advice_points = []
        
        # Check text query for symptoms (e.g. yellow leaves)
        if 'yellow' in farmer_query:
            factors.append("Farmer inquiry mentions yellowing of foliage.")
            advice_points.append(
                "Yellow Leaf Symptom Advisory: Leaf chlorosis (yellowing) can stem from multiple distinct causes: "
                "(1) Nitrogen deficiency (yellowing starts on oldest lower leaves), "
                "(2) Iron/micronutrient deficiency (young upper leaves turn yellow with green veins), "
                "(3) Overwatering or waterlogged roots, or "
                "(4) Viral infection like mosaic virus. "
                "Carefully inspect the root zone moisture and vein patterns before applying any chemical treatment."
            )
            
        # Check visual disease classification
        if disease_name and not is_healthy:
            factors.append(f"Active disease detected: {disease_name} in {crop}.")
            advice_points.append(
                f"Pathogen Alert ({disease_name}): Immediate inspection of the crop canopy is recommended. "
                "Isolate or prune visibly infected lower foliage to reduce secondary spore dispersal. "
            )
            
            # Cross-reference with weather (fungal trigger)
            if 'blight' in disease_name.lower() or 'rust' in disease_name.lower() or 'mildew' in disease_name.lower():
                if humidity > 75:
                    factors.append(f"Fungal disease combined with high humidity ({humidity}%) creates severe infection risk.")
                    advice_points.append(
                        f"CRITICAL: Relative humidity is {humidity}%. Fungal spores proliferate rapidly in high atmospheric moisture. "
                        "Strictly avoid overhead irrigation; ensure maximum row ventilation; apply copper-based or approved protective fungicide early in the morning as guided by your local extension officer."
                    )
                else:
                    advice_points.append(
                        "Maintain dry foliage and ensure good plant spacing to prevent disease spread."
                    )
        elif is_healthy or disease.get('predicted_disease') == 'Healthy Leaf':
            advice_points.append(
                "Plant Health Status: Leaf analysis indicates healthy, vigorous foliage. Continue preventive sanitation, field scouting every 5-7 days, and keep weed competition minimal."
            )
        else:
            # No image analyzed yet
            if humidity > 75:
                factors.append(f"Ambient humidity of {humidity}% poses elevated fungal risk.")
                advice_points.append(
                    f"Fungal Risk Warning: Atmospheric humidity is currently {humidity}%. Warm, moist environments favor foliar spot fungi. "
                    "Monitor lower leaves for dark spots or mildew fuzz, and avoid handling foliage while wet."
                )
            else:
                advice_points.append(
                    "Crop health appears stable. Upload a leaf photograph in the Plant Disease Detection section for real-time pathology assessment."
                )

        return " ".join(advice_points)

    def _evaluate_weather_operations(self, weather, factors):
        wind_kmh = float(weather.get('wind_speed_kmh', 5.0) or 5.0)
        temp = float(weather.get('temperature', 25.0) or 25.0)
        rain_mm = float(weather.get('rainfall_mm', 0.0) or 0.0)
        upcoming_rain = weather.get('upcoming_rain', False) or rain_mm > 0.5
        
        ops = []
        # Chemical spraying window
        if wind_kmh > 15:
            factors.append(f"Wind speed {wind_kmh} km/h exceeds 15 km/h spraying threshold.")
            ops.append(
                f"Spraying Feasibility: Unfavorable. Wind speed is {wind_kmh} km/h. Postpone foliar sprays to eliminate dangerous pesticide drift."
            )
        elif upcoming_rain:
            factors.append("Precipitation risk reduces chemical retention on foliage.")
            ops.append(
                "Spraying Feasibility: Unfavorable. Rain within 6 hours will wash off agrochemicals, wasting inputs."
            )
        else:
            ops.append(
                f"Spraying Feasibility: Favorable. Calm winds ({wind_kmh} km/h) allow uniform spray coverage."
            )
            
        # Field operations / Tillage
        if upcoming_rain:
            ops.append(
                "Field Machinery: Avoid heavy tractor plowing or harvesting in saturated soil to prevent severe soil compaction and rutting."
            )
        else:
            ops.append(
                "Field Machinery: Field traffic conditions are suitable for intercultural operations, weeding, and mulching."
            )

        return " ".join(ops)

    def _evaluate_general_care(self, crop, stage, soil, factors):
        stage_lower = stage.lower()
        if 'seedling' in stage_lower or 'early' in stage_lower:
            return (
                f"Early Season Care for {crop}: Protect young seedlings from bird and rodent damage. "
                "Thin out overly dense clusters to recommended plant-to-plant spacing. Hoe lightly around rows to break soil crusting."
            )
        elif 'flower' in stage_lower or 'reproductive' in stage_lower:
            return (
                f"Mid-Season Care for {crop}: Avoid mechanical root disturbance during flowering. "
                "Install yellow sticky traps to capture whiteflies, thrips, and aphids without heavy chemical dependency."
            )
        elif 'harvest' in stage_lower or 'maturity' in stage_lower:
            return (
                f"Harvest Preparation for {crop}: Clean and calibrate harvesting tools and grain storage bags. "
                "Ensure threshing and drying floors are disinfected to preserve post-harvest grain/fruit quality."
            )
        else:
            return (
                f"General Agronomic Care for {crop}: Maintain clean field borders, monitor for beneficial predator insects (like ladybird beetles), and follow integrated crop management practices."
            )

    def _compute_risk_level(self, weather, disease):
        humidity = float(weather.get('humidity', 60.0) or 60.0)
        disease_name = (disease.get('predicted_disease') or '').lower()
        is_healthy = disease.get('is_healthy', False)
        
        if disease_name and not is_healthy and 'blight' in disease_name and humidity > 75:
            return 'Critical'
        if disease_name and not is_healthy:
            return 'High'
        if humidity > 80 or float(weather.get('temperature', 25.0) or 25.0) > 38:
            return 'Moderate'
        return 'Low'

advisory_engine = AdaptiveAdvisoryEngine()

