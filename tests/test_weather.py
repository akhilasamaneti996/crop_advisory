import pytest
from services.weather_service import weather_service

def test_weather_missing_api_key():
    # If no real key configured, should gracefully return 'api_key_missing'
    if not weather_service.is_configured():
        res = weather_service.get_weather('Hyderabad')
        assert res['status'] == 'api_key_missing'
        assert res['is_configured'] is False
        assert 'OPENWEATHER_API_KEY' in res['message']

def test_weather_rule_advisories():
    # Test rule generation logic independently
    suggestions = weather_service.generate_weather_advisory(
        temperature=32.0,
        humidity=85.0,  # High humidity trigger
        wind_speed_kmh=18.0,  # High wind trigger
        rain_val=0.0,
        weather_main='Clouds',
        forecast_items=[]
    )
    categories = [s['category'] for s in suggestions]
    assert 'Disease Risk' in categories
    assert 'Spraying Alert' in categories
    
    # Check that high wind produces spraying alert
    spray_alert = next(s for s in suggestions if s['category'] == 'Spraying Alert')
    assert 'Unsuitable' in spray_alert['title']

