from datetime import datetime, timezone
from database import db
import json

def get_utc_now():
    return datetime.now(timezone.utc)

class CropRecommendationHistory(db.Model):
    __tablename__ = 'crop_recommendation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    soil_type = db.Column(db.String(50), nullable=True)
    season = db.Column(db.String(50), nullable=True)
    growth_stage = db.Column(db.String(50), nullable=True)
    recommended_crop = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'temperature': round(self.temperature, 2),
            'humidity': round(self.humidity, 2),
            'ph': round(self.ph, 2),
            'rainfall': round(self.rainfall, 2),
            'location': self.location or 'Not specified',
            'soil_type': self.soil_type or 'General',
            'season': self.season or 'Any',
            'growth_stage': self.growth_stage or 'Sowing/Vegetative',
            'recommended_crop': self.recommended_crop,
            'confidence': round(self.confidence, 2) if self.confidence else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class DiseaseDetectionHistory(db.Model):
    __tablename__ = 'disease_detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    detected_crop = db.Column(db.String(100), nullable=False)
    predicted_disease = db.Column(db.String(150), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    symptoms = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    prevention = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'detected_crop': self.detected_crop,
            'predicted_disease': self.predicted_disease,
            'confidence': round(self.confidence, 2),
            'symptoms': self.symptoms,
            'treatment': self.treatment,
            'prevention': self.prevention,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class FarmerQuery(db.Model):
    __tablename__ = 'farmer_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_query = db.Column(db.Text, nullable=False)
    detected_intent = db.Column(db.String(100), nullable=False)
    response = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='en')
    session_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_query': self.user_query,
            'detected_intent': self.detected_intent,
            'response': self.response,
            'language': self.language,
            'session_id': self.session_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class AdvisoryHistory(db.Model):
    __tablename__ = 'advisory_history'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    growth_stage = db.Column(db.String(50), nullable=True)
    soil_data = db.Column(db.Text, nullable=True)  # JSON-encoded string
    weather_data = db.Column(db.Text, nullable=True)  # JSON-encoded string
    disease_info = db.Column(db.Text, nullable=True)  # JSON-encoded string
    irrigation_advice = db.Column(db.Text, nullable=False)
    fertilizer_advice = db.Column(db.Text, nullable=False)
    disease_advice = db.Column(db.Text, nullable=False)
    weather_advice = db.Column(db.Text, nullable=False)
    general_advice = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_name': self.crop_name,
            'growth_stage': self.growth_stage,
            'soil_data': json.loads(self.soil_data) if self.soil_data else {},
            'weather_data': json.loads(self.weather_data) if self.weather_data else {},
            'disease_info': json.loads(self.disease_info) if self.disease_info else {},
            'irrigation_advice': self.irrigation_advice,
            'fertilizer_advice': self.fertilizer_advice,
            'disease_advice': self.disease_advice,
            'weather_advice': self.weather_advice,
            'general_advice': self.general_advice,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
