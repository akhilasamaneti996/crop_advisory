from flask import Blueprint, render_template, request, jsonify
from services.weather_service import weather_service

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather')
def weather_page():
    is_configured = weather_service.is_configured()
    return render_template('weather.html', is_configured=is_configured)

@weather_bp.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', 'Hyderabad').strip()
    if not city:
        city = 'Hyderabad'
    result = weather_service.get_weather(city=city)
    return jsonify(result)

