/**
 * Multilingual Agricultural Chatbot with Voice Input & TTS Output
 */

let currentSessionId = localStorage.getItem('agro_chat_session') || generateUUID();
localStorage.setItem('agro_chat_session', currentSessionId);

let isVoiceOutputEnabled = true;
let recognition = null;
let isListening = false;

const SUGGESTIONS = {
  en: [
    "How much fertilizer should I apply for rice?",
    "My tomato leaves have yellow spots and rings",
    "How often should I irrigate my crops?",
    "Is it safe to spray pesticides in windy weather?",
    "What crop is best for low rainfall areas?"
  ],
  te: [
    "వరికి ఏ ఎరువు వాడాలి?",
    "టమాటో ఆకులపై పసుపు మచ్చలు ఉన్నాయి",
    "పంటకు ఎప్పుడు నీరు పెట్టాలి?",
    "ఈ రోజు మందులు పిచికారీ చేయవచ్చా?",
    "నా నేలలో ఏ పంట వేయాలి?"
  ],
  hi: [
    "धान के लिए कौन सा खाद डालें?",
    "टमाटर की पत्तियों पर काले और पीले धब्बे हैं",
    "फसल में सिंचाई कब और कैसे करें?",
    "क्या आज कीटनाशक छिड़काव कर सकते हैं?",
    "कम पानी में कौन सी फसल उगाएं?"
  ]
};

const WELCOME_MESSAGES = {
  en: "Hello! I am your Adaptive Crop Advisory assistant. You can ask me questions about crop selection, fertilizer application, irrigation scheduling, plant diseases, or weather precautions. How may I help you today?",
  te: "నమస్కారం! నేను మీ అడాప్టివ్ క్రాప్ అడ్వైజరీ సహాయకుడిని. పంట ఎంపిక, ఎరువుల వాడకం, నీటి పారుదల, తెగుళ్ల నివారణ లేదా వాతావరణ జాగ్రత్తల గురించి నన్ను అడగవచ్చు. మీకు ఎలా సహాయపడగలను?",
  hi: "नमस्ते! मैं आपका एडेप्टिव क्रॉप एडवाइजरी सहायक हूँ। आप मुझसे फसल चुनाव, खाद का उपयोग, सिंचाई का समय, पादप रोग या मौसम संबंधी सावधानियों के बारे में पूछ सकते हैं। मैं आपकी क्या मदद करूँ?"
};

document.addEventListener('DOMContentLoaded', () => {
  const langSelect = document.getElementById('chatLanguageSelect');
  const chatInput = document.getElementById('chatInput');
  const btnSend = document.getElementById('btnSend');
  const btnMic = document.getElementById('btnMic');
  const btnToggleSpeech = document.getElementById('btnToggleSpeechOutput');

  // Match language with global language
  const savedLang = localStorage.getItem('agro_language') || 'en';
  if (langSelect) {
    langSelect.value = savedLang;
    updateLanguageView(savedLang);

    langSelect.addEventListener('change', (e) => {
      const lang = e.target.value;
      localStorage.setItem('agro_language', lang);
      updateLanguageView(lang);
      window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    });
  }

  // Listen to global language change
  window.addEventListener('languageChanged', (e) => {
    if (langSelect && langSelect.value !== e.detail.language) {
      langSelect.value = e.detail.language;
      updateLanguageView(e.detail.language);
    }
  });

  // Speech Output Toggle
  if (btnToggleSpeech) {
    btnToggleSpeech.addEventListener('click', () => {
      isVoiceOutputEnabled = !isVoiceOutputEnabled;
      const icon = document.getElementById('speechOutputIcon');
      if (isVoiceOutputEnabled) {
        icon.className = 'fa-solid fa-volume-high text-success';
        showNotification('Voice output enabled.', 'info');
      } else {
        icon.className = 'fa-solid fa-volume-xmark text-muted';
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        showNotification('Voice output muted.', 'info');
      }
    });
  }

  // Send message on click or enter
  if (btnSend) {
    btnSend.addEventListener('click', () => submitMessage());
  }

  if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        submitMessage();
      }
    });
  }

  // Initialize Speech Recognition
  initSpeechRecognition();
});

function updateLanguageView(lang) {
  // Update welcome message
  const welcomeText = document.getElementById('welcomeMessageText');
  if (welcomeText && WELCOME_MESSAGES[lang]) {
    welcomeText.innerText = WELCOME_MESSAGES[lang];
  }

  // Update suggestions
  const container = document.getElementById('suggestedQuestionsList');
  if (container) {
    const questions = SUGGESTIONS[lang] || SUGGESTIONS.en;
    container.innerHTML = questions.map(q => `
      <button type="button" class="btn btn-outline-light text-dark border text-start btn-sm small py-2" onclick="sendSuggestedQuestion('${q.replace(/'/g, "\\'")}')">
        <i class="fa-regular fa-comment-dots text-success me-1"></i> ${q}
      </button>
    `).join('');
  }
}

function sendSuggestedQuestion(q) {
  const input = document.getElementById('chatInput');
  if (input) {
    input.value = q;
    submitMessage();
  }
}

async function submitMessage() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  const langSelect = document.getElementById('chatLanguageSelect');
  const language = langSelect ? langSelect.value : 'en';

  // Append user bubble
  appendMessage(message, 'farmer');
  input.value = '';

  // Append typing indicator bubble
  const typingId = appendTypingIndicator();

  try {
    const response = await fetch('/api/chatbot/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        language: language,
        session_id: currentSessionId
      })
    });

    const res = await response.json();
    removeTypingIndicator(typingId);

    if (response.ok && res.status === 'success') {
      appendMessage(res.data.response, 'assistant', res.data.intent, res.data.confidence);
      if (isVoiceOutputEnabled) {
        speakText(res.data.response, language);
      }
    } else {
      appendMessage("Sorry, I encountered an issue processing your query. Please try again.", 'assistant');
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    console.error('Chat error:', err);
    appendMessage("Unable to connect to the assistant service. Please check your network.", 'assistant');
  }
}

function appendMessage(text, role, intent = null, confidence = null) {
  const messagesBox = document.getElementById('chatMessages');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role}`;

  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (role === 'assistant') {
    let tagHtml = '';
    if (intent && intent !== 'unknown') {
      tagHtml = `<span class="badge bg-light text-muted border small ms-1" style="font-size: 0.68rem;">${intent}</span>`;
    }
    bubble.innerHTML = `
      <div class="d-flex align-items-center gap-2 mb-1">
        <span class="badge bg-success p-1"><i class="fa-solid fa-robot"></i></span>
        <strong class="small text-dark">Farmer Assistant</strong>
        ${tagHtml}
      </div>
      <div>${escapeHtml(text)}</div>
      <span class="msg-time text-muted">${timeStr}</span>
    `;
  } else {
    bubble.innerHTML = `
      <div>${escapeHtml(text)}</div>
      <span class="msg-time text-white-50">${timeStr}</span>
    `;
  }

  messagesBox.appendChild(bubble);
  messagesBox.scrollTop = messagesBox.scrollHeight;
}

function appendTypingIndicator() {
  const messagesBox = document.getElementById('chatMessages');
  const id = 'typing_' + Date.now();
  const bubble = document.createElement('div');
  bubble.id = id;
  bubble.className = 'chat-bubble assistant text-muted small';
  bubble.innerHTML = `
    <span class="agro-spinner me-2" style="border-color: #2d6a4f; border-top-color: transparent;"></span>
    Assistant is thinking...
  `;
  messagesBox.appendChild(bubble);
  messagesBox.scrollTop = messagesBox.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// Web Speech Recognition
function initSpeechRecognition() {
  const btnMic = document.getElementById('btnMic');
  const statusBanner = document.getElementById('voiceStatusBanner');

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    if (btnMic) {
      btnMic.title = 'Speech recognition not supported in this browser.';
      btnMic.classList.add('opacity-50');
      btnMic.addEventListener('click', () => {
        showNotification('Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.', 'warning');
      });
    }
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  btnMic.addEventListener('click', () => {
    if (isListening) {
      recognition.stop();
      return;
    }

    const langSelect = document.getElementById('chatLanguageSelect');
    const lang = langSelect ? langSelect.value : 'en';

    // Set recognition language
    if (lang === 'te') {
      recognition.lang = 'te-IN';
    } else if (lang === 'hi') {
      recognition.lang = 'hi-IN';
    } else {
      recognition.lang = 'en-US';
    }

    try {
      recognition.start();
      isListening = true;
      btnMic.className = 'btn btn-danger';
      statusBanner.classList.remove('d-none');
    } catch (e) {
      console.warn('Speech recognition start error:', e);
    }
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const input = document.getElementById('chatInput');
    if (input && transcript) {
      input.value = transcript;
      submitMessage();
    }
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    stopListeningUI();
  };

  recognition.onend = () => {
    stopListeningUI();
  };

  function stopListeningUI() {
    isListening = false;
    if (btnMic) btnMic.className = 'btn btn-outline-success';
    if (statusBanner) statusBanner.classList.add('d-none');
  }
}

// Web Speech Synthesis (Text to Speech)
function speakText(text, language = 'en') {
  if (!('speechSynthesis' in window)) return;

  window.speechSynthesis.cancel(); // Stop any previous speech
  const utterance = new SpeechSynthesisUtterance(text);

  if (language === 'te') {
    utterance.lang = 'te-IN';
  } else if (language === 'hi') {
    utterance.lang = 'hi-IN';
  } else {
    utterance.lang = 'en-US';
  }

  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  window.speechSynthesis.speak(utterance);
}

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function escapeHtml(string) {
  const pre = document.createElement('pre');
  const text = document.createTextNode(string);
  pre.appendChild(text);
  return pre.innerHTML;
}

