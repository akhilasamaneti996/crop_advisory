import os
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from utils.validators import validate_image_upload
from utils.image_processing import save_upload_file
from services.disease_service import disease_service
from models import DiseaseDetectionHistory
from database import db
from config import Config

disease_bp = Blueprint('disease', __name__)

@disease_bp.route('/disease-detection')
def disease_detection_page():
    classes = disease_service.get_supported_classes()
    metrics = disease_service.get_metrics()
    is_ready = disease_service.is_model_ready()
    return render_template(
        'disease_detection.html',
        classes=classes,
        metrics=metrics,
        is_ready=is_ready
    )

@disease_bp.route('/api/disease/predict', methods=['POST'])
def predict_disease():
    try:
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No image file uploaded in the request.'}), 400
            
        file = request.files['image']
        is_valid, err_msg = validate_image_upload(file)
        if not is_valid:
            return jsonify({'status': 'error', 'message': err_msg}), 400
            
        upload_folder = current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER)
        saved_filename, saved_filepath = save_upload_file(file, upload_folder)
        
        # Perform deep learning prediction
        result = disease_service.predict(saved_filepath, file.filename)
        
        # Save analysis to database
        history_record = DiseaseDetectionHistory(
            filename=saved_filename,
            detected_crop=result['detected_crop'],
            predicted_disease=result['predicted_disease'],
            confidence=result['confidence'],
            symptoms="\n".join(result['symptoms']),
            treatment="\n".join(result['treatments']),
            prevention="\n".join(result['preventions'])
        )
        db.session.add(history_record)
        db.session.commit()
        
        result['record_id'] = history_record.id
        result['image_url'] = f"/uploads/{saved_filename}"
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except RuntimeError as re:
        return jsonify({
            'status': 'error',
            'message': str(re),
            'model_unavailable': True
        }), 503
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f"Unexpected error during disease analysis: {str(e)}"}), 500

@disease_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER)
    return send_from_directory(upload_folder, filename)

@disease_bp.route('/api/history/diseases', methods=['GET'])
def get_disease_history():
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        records = DiseaseDetectionHistory.query.order_by(
            DiseaseDetectionHistory.created_at.desc()
        ).limit(limit).all()
        return jsonify({
            'status': 'success',
            'count': len(records),
            'records': [r.to_dict() for r in records]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

