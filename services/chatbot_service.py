import os
import joblib
import numpy as np
from config import Config
from utils.translation import get_ui_text

class ChatbotService:
    def __init__(self):
        self.bundle = None
        self.pipeline = None
        self.intents_map = {}
        self.sessions = {}  # session_id -> list of {'role': ..., 'text': ...}
        self._load_model()
        
    def _load_model(self):
        try:
            if os.path.exists(Config.CHATBOT_MODEL_PATH):
                self.bundle = joblib.load(Config.CHATBOT_MODEL_PATH)
                self.pipeline = self.bundle['pipeline']
                self.intents_map = self.bundle.get('intents_map', {})
            else:
                self.pipeline = None
                self.intents_map = {}
        except Exception as e:
            print(f"Error loading chatbot model: {e}")
            self.pipeline = None
            self.intents_map = {}

    def is_model_ready(self):
        return self.pipeline is not None and len(self.intents_map) > 0

    def get_supported_intents(self):
        return list(self.intents_map.keys())

    def get_session_history(self, session_id):
        if not session_id:
            return []
        return self.sessions.get(session_id, [])

    def process_message(self, message, language='en', session_id=None):
        if not message or not message.strip():
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'response': "Please enter a farming question or tap the microphone to speak.",
                'language': language,
                'session_id': session_id
            }

        cleaned_msg = message.strip()
        lang_ui = get_ui_text(language)
        
        # Ensure model is ready
        if not self.is_model_ready():
            self._load_model()
            
        intent = 'general_farming'
        confidence = 0.50
        
        if self.is_model_ready():
            try:
                # Predict probabilities
                probs = self.pipeline.predict_proba([cleaned_msg])[0]
                classes = list(self.pipeline.classes_)
                best_idx = int(np.argmax(probs))
                confidence = float(probs[best_idx]) * 100.0
                intent = classes[best_idx]
                
                # If confidence is too low or message is completely unrelated
                if confidence < 20.0 and len(cleaned_msg.split()) < 2:
                    intent = 'unknown'
            except Exception as e:
                print(f"Chatbot inference exception: {e}")
                intent = 'general_farming'
                confidence = 50.0

        # Retrieve response for intent
        if intent in self.intents_map:
            intent_responses = self.intents_map[intent]
            # Get response in requested language, fallback to English
            response_text = intent_responses.get(language, intent_responses.get('en', ''))
        else:
            response_text = lang_ui.get('unknown_response')

        # Store in session memory
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            self.sessions[session_id].append({'role': 'farmer', 'text': cleaned_msg})
            self.sessions[session_id].append({'role': 'assistant', 'text': response_text})
            # Keep last 20 messages
            self.sessions[session_id] = self.sessions[session_id][-20:]

        return {
            'intent': intent,
            'confidence': round(confidence, 1),
            'response': response_text,
            'language': language,
            'session_id': session_id
        }

chatbot_service = ChatbotService()

