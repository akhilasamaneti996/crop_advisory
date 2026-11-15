import json
from flask import Blueprint, render_template, request, jsonify
from services.advisory_engine import advisory_engine
from models import AdvisoryHistory
from database import db

advisory_bp = Blueprint('advisory', __name__)

@advisory_bp.route('/advisory')
def advisory_page():
    return render_template('advisory.html')

@advisory_bp.route('/api/advisory/generate', methods=['POST'])
def generate_advisory():
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({'status': 'error', 'message': 'No advisory parameters supplied.'}), 400
            
        result = advisory_engine.generate_advisory(data)
        
        # Save advisory to database
        record = AdvisoryHistory(
            crop_name=result['crop_name'],
            growth_stage=result['growth_stage'],
            soil_data=json.dumps(data.get('soil', {})),
            weather_data=json.dumps(data.get('weather', {})),
            disease_info=json.dumps(data.get('disease', {})),
            irrigation_advice=result['irrigation_advice'],
            fertilizer_advice=result['fertilizer_advice'],
            disease_advice=result['disease_advice'],
            weather_advice=result['weather_advice'],
            general_advice=result['general_advice']
        )
        db.session.add(record)
        db.session.commit()
        
        result['record_id'] = record.id
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f"Advisory generation error: {str(e)}"
        }), 500

@advisory_bp.route('/api/history/advisories', methods=['GET'])
def get_advisory_history():
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        records = AdvisoryHistory.query.order_by(
            AdvisoryHistory.created_at.desc()
        ).limit(limit).all()
        return jsonify({
            'status': 'success',
            'count': len(records),
            'records': [r.to_dict() for r in records]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

