import os
from flask import Flask, jsonify, render_template
from config import Config
from database import db, init_db

# Import services for health status inspection
from services.crop_service import crop_service
from services.disease_service import disease_service
from services.chatbot_service import chatbot_service
from services.weather_service import weather_service

# Import Blueprints
from routes.dashboard_routes import dashboard_bp
from routes.crop_routes import crop_bp
from routes.disease_routes import disease_bp
from routes.weather_routes import weather_bp
from routes.chatbot_routes import chatbot_bp
from routes.advisory_routes import advisory_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure necessary folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ML_DIR'], exist_ok=True)
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(advisory_bp)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_healthy = True
        try:
            db.session.execute(db.text('SELECT 1'))
        except Exception:
            db_healthy = False
            
        return jsonify({
            'status': 'healthy' if db_healthy else 'degraded',
            'database': 'connected' if db_healthy else 'error',
            'modules': {
                'crop_recommendation': {
                    'ready': crop_service.is_model_ready(),
                    'model_type': 'Random Forest Classifier (22 crops)'
                },
                'disease_detection': {
                    'ready': disease_service.is_model_ready(),
                    'model_type': 'MobileNetV2 Transfer Learning'
                },
                'chatbot_assistant': {
                    'ready': chatbot_service.is_model_ready(),
                    'model_type': 'TF-IDF + Logistic Regression'
                },
                'weather_intelligence': {
                    'configured': weather_service.is_configured(),
                    'service': 'OpenWeather API'
                },
                'adaptive_decision_engine': {
                    'ready': True,
                    'type': 'Multimodal Rule-Based Agronomic Engine'
                }
            }
        })
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('dashboard.html', error_msg="Page not found (404)"), 404
        
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'status': 'error', 'message': 'Internal Server Error (500)'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Adaptive Crop Advisory server on http://127.0.0.1:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=False)

