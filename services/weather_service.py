import os
import requests
from config import Config

class WeatherService:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        
    def is_configured(self):
        self.api_key = os.environ.get('OPENWEATHER_API_KEY', Config.OPENWEATHER_API_KEY)
        return bool(self.api_key and self.api_key.strip() and self.api_key != 'your_openweather_api_key_here')

    def get_weather(self, city='Hyderabad'):
        if not self.is_configured():
            return {
                'status': 'api_key_missing',
                'is_configured': False,
                'message': (
                    "OpenWeather API key is not configured. "
                    "To enable live weather intelligence, obtain a free API key from "
                    "https://openweathermap.org/api and add OPENWEATHER_API_KEY=<your_key> to your .env file."
                ),
                'city': city
            }
            
        try:
            # 1. Current Weather
            current_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            resp = requests.get(current_url, params=params, timeout=7)
            
            if resp.status_code == 401:
                return {
                    'status': 'error',
                    'is_configured': True,
                    'message': "Invalid OpenWeather API key. Please check the OPENWEATHER_API_KEY in your .env file."
                }
            elif resp.status_code == 404:
                return {
                    'status': 'error',
                    'is_configured': True,
                    'message': f"City '{city}' was not found. Please check spelling or try a nearby city."
                }
            elif resp.status_code != 200:
                return {
                    'status': 'error',
                    'is_configured': True,
                    'message': f"Weather service responded with status {resp.status_code}."
                }
                
            data = resp.json()
            
            # Extract current weather parameters
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed_ms = data['wind']['speed']
            wind_speed_kmh = round(wind_speed_ms * 3.6, 1)
            weather_desc = data['weather'][0]['description'].title()
            weather_main = data['weather'][0]['main']
            icon_code = data['weather'][0]['icon']
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            rain_val = 0.0
            if 'rain' in data:
                rain_val = data['rain'].get('1h', data['rain'].get('3h', 0.0))
                
            # 2. 5-Day Forecast
            forecast_items = []
            try:
                forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
                f_resp = requests.get(forecast_url, params=params, timeout=7)
                if f_resp.status_code == 200:
                    f_data = f_resp.json()
                    # Sample every 8 intervals (approx every 24 hours at 12:00)
                    for item in f_data.get('list', [])[:16]:
                        forecast_items.append({
                            'dt_txt': item['dt_txt'],
                            'temp': round(item['main']['temp'], 1),
                            'humidity': item['main']['humidity'],
                            'description': item['weather'][0]['description'].title(),
                            'icon': item['weather'][0]['icon'],
                            'rain_prob': round(item.get('pop', 0) * 100),
                            'wind_kmh': round(item['wind']['speed'] * 3.6, 1)
                        })
            except Exception as e:
                print(f"Forecast fetch exception (non-fatal): {e}")

            # 3. Generate rule-based agricultural suggestions
            agri_advisory = self.generate_weather_advisory(
                temperature=temp,
                humidity=humidity,
                wind_speed_kmh=wind_speed_kmh,
                rain_val=rain_val,
                weather_main=weather_main,
                forecast_items=forecast_items
            )

            return {
                'status': 'success',
                'is_configured': True,
                'city': data.get('name', city),
                'country': data.get('sys', {}).get('country', ''),
                'coordinates': data.get('coord', {}),
                'temperature': round(temp, 1),
                'feels_like': round(feels_like, 1),
                'humidity': humidity,
                'pressure': pressure,
                'wind_speed_kmh': wind_speed_kmh,
                'weather_main': weather_main,
                'weather_description': weather_desc,
                'icon_url': icon_url,
                'rainfall_mm': round(rain_val, 1),
                'forecast': forecast_items,
                'agricultural_advisory': agri_advisory
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'is_configured': True,
                'message': f"Network error connecting to OpenWeather API: {str(e)}"
            }

    def generate_weather_advisory(self, temperature, humidity, wind_speed_kmh, rain_val, weather_main, forecast_items):
        """
        Rule-based agricultural guidelines based on weather.
        Note: These rules represent general agronomic best-practices,
        not scientifically validated disease diagnoses.
        """
        suggestions = []
        
        # Check expected rain in forecast
        upcoming_rain = rain_val > 0 or any(item.get('rain_prob', 0) > 60 for item in forecast_items[:4])
        
        # 1. Fungal disease risk
        if humidity > 75:
            suggestions.append({
                'type': 'warning',
                'category': 'Disease Risk',
                'title': 'High Fungal Disease Risk',
                'description': f"Relative humidity is high ({humidity}%). Humid conditions promote spore germination of foliar blights and powdery mildew. Inspect lower canopy leaves and maintain plant aeration."
            })
        elif humidity < 40:
            suggestions.append({
                'type': 'info',
                'category': 'Moisture Alert',
                'title': 'Low Atmospheric Humidity',
                'description': f"Relative humidity is {humidity}%. Evapotranspiration is heightened. Monitor younger seedlings for wilting."
            })
            
        # 2. Irrigation guidance
        if upcoming_rain:
            suggestions.append({
                'type': 'info',
                'category': 'Irrigation',
                'title': 'Rainfall Expected / Imminent',
                'description': "Rainfall is detected or likely in the near forecast. Delay scheduled irrigation and check root-zone moisture before running pumps to prevent root asphyxiation."
            })
        elif temperature > 35:
            suggestions.append({
                'type': 'warning',
                'category': 'Irrigation',
                'title': 'High Temperature Water Stress',
                'description': f"Ambient temperature is {temperature:.1f} °C. High evaporative demand increases crop water requirements. Water early in the morning or late evening."
            })
        else:
            suggestions.append({
                'type': 'success',
                'category': 'Irrigation',
                'title': 'Normal Irrigation Schedule',
                'description': "Atmospheric conditions are stable. Maintain regular moisture schedule based on crop growth stage."
            })
            
        # 3. Chemical spraying feasibility
        if wind_speed_kmh > 15:
            suggestions.append({
                'type': 'danger',
                'category': 'Spraying Alert',
                'title': 'Unsuitable Spraying Conditions (High Wind)',
                'description': f"Wind speed is {wind_speed_kmh} km/h (exceeds recommended 15 km/h limit). High wind causes chemical drift, reducing efficacy and risking non-target exposure. Postpone spraying."
            })
        elif upcoming_rain:
            suggestions.append({
                'type': 'warning',
                'category': 'Spraying Alert',
                'title': 'Rain Risk for Spraying',
                'description': "Foliar chemical sprays require 4 to 6 hours of rain-free drying time to avoid wash-off. Postpone application until weather clears."
            })
        else:
            suggestions.append({
                'type': 'success',
                'category': 'Spraying Alert',
                'title': 'Favorable Spraying Conditions',
                'description': f"Calm winds ({wind_speed_kmh} km/h) and dry skies are favorable for foliar nutrient and pest management sprays."
            })
            
        # 4. Temperature extreme warnings
        if temperature > 38:
            suggestions.append({
                'type': 'danger',
                'category': 'Heat Stress',
                'title': 'Severe Heat Wave Advisory',
                'description': "High heat can cause floral abortion and pollen sterility in vegetables and cereals. Ensure light frequent irrigation to cool the microclimate."
            })
        elif temperature < 6:
            suggestions.append({
                'type': 'warning',
                'category': 'Cold Alert',
                'title': 'Frost / Chilling Risk',
                'description': "Low night temperatures risk frost damage to sensitive seedlings. Consider light evening irrigations or field border smoke cover if frost is imminent."
            })
            
        return suggestions

weather_service = WeatherService()

