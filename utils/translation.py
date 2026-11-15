import os

# Comprehensive UI and Advisory Localization Dictionary
UI_TRANSLATIONS = {
    'en': {
        'app_name': 'Adaptive Crop Advisory',
        'tagline': 'Smart Farming Starts with Better Decisions',
        'nav_home': 'Home',
        'nav_dashboard': 'Dashboard',
        'nav_crop': 'Crop Recommendation',
        'nav_disease': 'Disease Detection',
        'nav_weather': 'Weather Intelligence',
        'nav_chatbot': 'Farmer Assistant',
        'nav_advisory': 'Adaptive Advisory',
        'btn_get_started': 'Get Started',
        'btn_predict': 'Predict Best Crop',
        'btn_analyze': 'Analyze Leaf Image',
        'btn_refresh': 'Refresh Weather',
        'btn_send': 'Send',
        'btn_generate_advisory': 'Generate Comprehensive Advisory',
        'quick_actions': 'Quick Actions',
        'recent_activity': 'Recent Advisory Activities',
        'status_healthy': 'Healthy',
        'status_infected': 'Attention Required',
        'language_label': 'Language',
        'listening': 'Listening to your question...',
        'voice_error': 'Voice recognition not supported in this browser.',
        'unknown_response': "I am not completely sure about that specific question. Please consult our Crop Recommendation or Disease Detection modules, or reach out to your local Krishi Vigyan Kendra (KVK) for specialized advice."
    },
    'te': {
        'app_name': 'అడాప్టివ్ క్రాప్ అడ్వైజరీ',
        'tagline': 'సరైన నిర్ణయాలతోనే స్మార్ట్ వ్యవసాయం ప్రారంభం',
        'nav_home': 'హోమ్',
        'nav_dashboard': 'డ్యాష్‌బోర్డ్',
        'nav_crop': 'పంట సిఫార్సు',
        'nav_disease': 'తెగులు గుర్తింపు',
        'nav_weather': 'వాతావరణ సమాచారం',
        'nav_chatbot': 'రైతు సహాయకుడు',
        'nav_advisory': 'అడాప్టివ్ సలహా',
        'btn_get_started': 'ప్రారంభించండి',
        'btn_predict': 'ఉత్తమ పంటను కనుగొనండి',
        'btn_analyze': 'ఆకు చిత్రాన్ని విశ్లేషించండి',
        'btn_refresh': 'వాతావరణం రిఫ్రెష్ చేయండి',
        'btn_send': 'పంపండి',
        'btn_generate_advisory': 'సమగ్ర సలహాను రూపొందించండి',
        'quick_actions': 'త్వరిత చర్యలు',
        'recent_activity': 'ఇటీవలి సలహా కార్యకలాపాలు',
        'status_healthy': 'ఆరోగ్యంగా ఉంది',
        'status_infected': 'గమనించవలసిన అవసరం ఉంది',
        'language_label': 'భాష',
        'listening': 'మీ ప్రశ్న వింటున్నాము...',
        'voice_error': 'ఈ బ్రౌజర్‌లో వాయిస్ రికగ్నిషన్ సదుపాయం లేదు.',
        'unknown_response': "ఈ ప్రశ్నకు స్పష్టమైన సమాధానం లభించలేదు. దయచేసి పంట సిఫార్సు లేదా రోగ నిర్ధారణ విభాగాలను ఉపయోగించండి లేదా సమీపంలోని కృషి విజ్ఞాన కేంద్రం (KVK) ను సంప్రదించండి."
    },
    'hi': {
        'app_name': 'एडेप्टिव क्रॉप एडवाइजरी',
        'tagline': 'बेहतर निर्णयों से ही शुरू होती है स्मार्ट खेती',
        'nav_home': 'होम',
        'nav_dashboard': 'डैशबोर्ड',
        'nav_crop': 'फसल सिफारिश',
        'nav_disease': 'पादप रोग पहचान',
        'nav_weather': 'मौसम जानकारी',
        'nav_chatbot': 'किसान सहायक',
        'nav_advisory': 'अनुकूली सलाह',
        'btn_get_started': 'शुरू करें',
        'btn_predict': 'सर्वोत्तम फसल जानें',
        'btn_analyze': 'पत्ती का विश्लेषण करें',
        'btn_refresh': 'मौसम अपडेट करें',
        'btn_send': 'भेजें',
        'btn_generate_advisory': 'विस्तृत कृषि सलाह प्राप्त करें',
        'quick_actions': 'त्वरित कार्य',
        'recent_activity': 'हाल की कृषि सलाह गतिविधियां',
        'status_healthy': 'स्वस्थ',
        'status_infected': 'ध्यान देने की आवश्यकता है',
        'language_label': 'भाषा',
        'listening': 'आपकी आवाज सुनी जा रही है...',
        'voice_error': 'इस ब्राउज़र में वॉयस रिकग्निशन समर्थित नहीं है।',
        'unknown_response': "मुझे इस विशिष्ट प्रश्न के बारे में पूरी जानकारी नहीं है। कृपया हमारे 'क्रॉप रिकमेंडेशन' या 'डिजीज डिटेक्शन' मॉड्यूल का उपयोग करें या निकटतम कृषि विज्ञान केंद्र (KVK) से संपर्क करें।"
    }
}

def get_ui_text(lang='en'):
    """Returns the translation dictionary for the selected language (fallback to English)."""
    return UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS['en'])

def translate_phrase(text, target_lang='en'):
    """Translates known UI phrases or returns original text."""
    lang_dict = UI_TRANSLATIONS.get(target_lang, UI_TRANSLATIONS['en'])
    for k, v in UI_TRANSLATIONS['en'].items():
        if v.lower() == text.strip().lower():
            return lang_dict.get(k, text)
    return text

