from flask import Blueprint, render_template, request, jsonify
from utils.validators import validate_crop_inputs
from services.crop_service import crop_service
from models import CropRecommendationHistory
from database import db

crop_bp = Blueprint('crop', __name__)

@crop_bp.route('/crop-recommendation')
def crop_recommendation_page():
    metrics = crop_service.get_model_metrics()
    return render_template('crop_recommendation.html', metrics=metrics)

@crop_bp.route('/api/crop/recommend', methods=['POST'])
def recommend_crop():
    try:
        data = request.get_json() or request.form.to_dict()
        if not data:
            return jsonify({'status': 'error', 'message': 'No input data provided.'}), 400
            
        is_valid, errors, cleaned = validate_crop_inputs(data)
        if not is_valid:
            return jsonify({'status': 'error', 'errors': errors}), 422
            
        prediction_result = crop_service.predict(
            n=cleaned['nitrogen'],
            p=cleaned['phosphorus'],
            k=cleaned['potassium'],
            temperature=cleaned['temperature'],
            humidity=cleaned['humidity'],
            ph=cleaned['ph'],
            rainfall=cleaned['rainfall'],
            context={
                'location': cleaned.get('location'),
                'soil_type': cleaned.get('soil_type'),
                'season': cleaned.get('season'),
                'growth_stage': cleaned.get('growth_stage')
            }
        )
        
        # Save to database
        history_record = CropRecommendationHistory(
            nitrogen=cleaned['nitrogen'],
            phosphorus=cleaned['phosphorus'],
            potassium=cleaned['potassium'],
            temperature=cleaned['temperature'],
            humidity=cleaned['humidity'],
            ph=cleaned['ph'],
            rainfall=cleaned['rainfall'],
            location=cleaned.get('location'),
            soil_type=cleaned.get('soil_type'),
            season=cleaned.get('season'),
            growth_stage=cleaned.get('growth_stage'),
            recommended_crop=prediction_result['recommended_crop'],
            confidence=prediction_result['confidence']
        )
        db.session.add(history_record)
        db.session.commit()
        
        prediction_result['record_id'] = history_record.id
        return jsonify({
            'status': 'success',
            'data': prediction_result
        })
        
    except RuntimeError as re:
        return jsonify({'status': 'error', 'message': str(re)}), 503
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f"Unexpected error during crop prediction: {str(e)}"}), 500

@crop_bp.route('/api/history/crops', methods=['GET'])
def get_crop_history():
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        records = CropRecommendationHistory.query.order_by(
            CropRecommendationHistory.created_at.desc()
        ).limit(limit).all()
        return jsonify({
            'status': 'success',
            'count': len(records),
            'records': [r.to_dict() for r in records]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

