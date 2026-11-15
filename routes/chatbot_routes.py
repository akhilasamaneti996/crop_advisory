from flask import Blueprint, render_template, request, jsonify
from services.chatbot_service import chatbot_service
from models import FarmerQuery
from database import db
import uuid

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
def send_message():
    try:
        data = request.get_json() or {}
        message = str(data.get('message', '')).strip()
        language = str(data.get('language', 'en')).strip().lower()
        if language not in ['en', 'te', 'hi']:
            language = 'en'
            
        session_id = data.get('session_id') or str(uuid.uuid4())
        
        if not message:
            return jsonify({
                'status': 'error',
                'message': 'Message cannot be empty.'
            }), 400
            
        res = chatbot_service.process_message(
            message=message,
            language=language,
            session_id=session_id
        )
        
        # Save query to database
        record = FarmerQuery(
            user_query=message,
            detected_intent=res['intent'],
            response=res['response'],
            language=language,
            session_id=session_id
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': res
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f"Chatbot processing error: {str(e)}"
        }), 500

@chatbot_bp.route('/api/chatbot/history', methods=['GET'])
def get_chat_history():
    session_id = request.args.get('session_id')
    history = chatbot_service.get_session_history(session_id)
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'history': history
    })

