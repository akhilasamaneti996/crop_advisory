import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'crop-advisory-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{os.path.join(basedir, "crop_advisory.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'data', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max image upload
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    
    # External APIs
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
    
    # ML & DL Model Paths
    ML_DIR = os.path.join(basedir, 'ml_models')
    CROP_MODEL_PATH = os.path.join(ML_DIR, 'crop_model.pkl')
    CROP_ENCODER_PATH = os.path.join(ML_DIR, 'crop_label_encoder.pkl')
    DISEASE_MODEL_PATH = os.path.join(ML_DIR, 'disease_model.keras')
    DISEASE_CLASSES_PATH = os.path.join(ML_DIR, 'disease_classes.json')
    CHATBOT_MODEL_PATH = os.path.join(ML_DIR, 'chatbot_model.pkl')
    
    # Datasets
    DATA_DIR = os.path.join(basedir, 'data', 'datasets')
    CROP_DATASET_PATH = os.path.join(DATA_DIR, 'Crop_recommendation.csv')
    CHATBOT_DATASET_PATH = os.path.join(DATA_DIR, 'chatbot_intents.json')

