import pytest
from services.crop_service import crop_service
from utils.validators import validate_crop_inputs

def test_crop_model_ready():
    assert crop_service.is_model_ready() is True

def test_crop_prediction_rice():
    res = crop_service.predict(
        n=90, p=42, k=43,
        temperature=20.88, humidity=82.0, ph=6.5, rainfall=202.9,
        context={'location': 'Test Field', 'growth_stage': 'Vegetative'}
    )
    assert res['recommended_crop'].lower() == 'rice'
    assert res['confidence'] > 50.0
    assert len(res['top_candidates']) >= 1
    assert 'crop_info' in res
    assert 'scientific_name' in res['crop_info']
    assert res['crop_info']['scientific_name'] == 'Oryza sativa'

def test_crop_input_validation():
    valid, errors, cleaned = validate_crop_inputs({
        'nitrogen': '80',
        'phosphorus': '40',
        'potassium': '40',
        'temperature': '25.0',
        'humidity': '75.0',
        'ph': '6.8',
        'rainfall': '150.0'
    })
    assert valid is True
    assert len(errors) == 0
    assert cleaned['nitrogen'] == 80.0

def test_crop_input_invalid_ph():
    valid, errors, cleaned = validate_crop_inputs({
        'nitrogen': '80',
        'phosphorus': '40',
        'potassium': '40',
        'temperature': '25.0',
        'humidity': '75.0',
        'ph': '18.5', # Invalid pH > 14
        'rainfall': '150.0'
    })
    assert valid is False
    assert 'ph' in errors

