import pytest
from services.chatbot_service import chatbot_service

def test_chatbot_model_ready():
    assert chatbot_service.is_model_ready() is True

def test_chatbot_intent_fertilizer_en():
    res = chatbot_service.process_message("How much urea and NPK should I apply for wheat?", language='en')
    assert res['intent'] == 'fertilizer_query'
    assert len(res['response']) > 20
    assert res['language'] == 'en'

def test_chatbot_intent_disease_en():
    res = chatbot_service.process_message("My crop leaves have black spots and blight", language='en')
    assert res['intent'] == 'disease_query'
    assert 'leaf' in res['response'].lower() or 'fungal' in res['response'].lower()

def test_chatbot_multilingual_te():
    res = chatbot_service.process_message("వరికి ఏ ఎరువు వాడాలి", language='te')
    assert res['intent'] == 'fertilizer_query'
    assert res['language'] == 'te'
    assert len(res['response']) > 10

def test_chatbot_multilingual_hi():
    res = chatbot_service.process_message("फसल में पानी कब देना चाहिए", language='hi')
    assert res['intent'] == 'irrigation_query'
    assert res['language'] == 'hi'
    assert len(res['response']) > 10

def test_chatbot_session_memory():
    sess_id = "test_pytest_session_001"
    chatbot_service.process_message("Hello there", language='en', session_id=sess_id)
    history = chatbot_service.get_session_history(sess_id)
    assert len(history) >= 2
    assert history[0]['role'] == 'farmer'
    assert history[1]['role'] == 'assistant'

