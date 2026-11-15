import pytest
from services.advisory_engine import advisory_engine

def test_advisory_fungal_and_high_humidity():
    data = {
        'crop_name': 'Tomato',
        'growth_stage': 'Flowering / Reproductive',
        'soil': {'nitrogen': 60, 'phosphorus': 40, 'potassium': 40, 'ph': 6.5, 'soil_type': 'Loamy'},
        'weather': {'temperature': 26.0, 'humidity': 84.0, 'wind_speed_kmh': 10.0, 'rainfall_mm': 0.0},
        'disease': {'predicted_disease': 'Early Blight', 'is_healthy': False}
    }
    res = advisory_engine.generate_advisory(data)
    assert res['risk_level'] == 'Critical'
    assert 'Fungal' in " ".join(res['decision_factors']) or 'humidity' in " ".join(res['decision_factors'])
    assert 'overhead' in res['disease_advice'].lower() or 'fungicide' in res['disease_advice'].lower()

def test_advisory_expected_rain():
    data = {
        'crop_name': 'Maize',
        'growth_stage': 'Vegetative Stage',
        'soil': {'nitrogen': 50, 'phosphorus': 40, 'potassium': 40, 'ph': 6.8, 'soil_type': 'Loamy'},
        'weather': {'temperature': 25.0, 'humidity': 70.0, 'wind_speed_kmh': 8.0, 'rainfall_mm': 5.0, 'upcoming_rain': True},
        'disease': {'predicted_disease': 'Healthy Leaf', 'is_healthy': True}
    }
    res = advisory_engine.generate_advisory(data)
    assert 'Rainfall is detected or expected' in res['irrigation_advice']
    assert 'Delay top-dressing' in res['fertilizer_advice'] or 'runoff' in res['fertilizer_advice'].lower()

def test_advisory_yellow_leaf_symptom():
    data = {
        'crop_name': 'Rice',
        'growth_stage': 'Vegetative Stage',
        'farmer_query': 'farmer noticed yellow leaves'
    }
    res = advisory_engine.generate_advisory(data)
    assert 'Yellow Leaf Symptom Advisory' in res['disease_advice']

