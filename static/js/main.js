/**
 * Adaptive Crop Advisory - Main Application Script
 */

const UI_STRINGS = {
  en: {
    nav_home: '<i class="fa-solid fa-house me-1"></i> Home',
    nav_dashboard: '<i class="fa-solid fa-gauge-high me-1"></i> Dashboard',
    nav_crop: '<i class="fa-solid fa-wheat-awn me-1"></i> Crop Recommendation',
    nav_disease: '<i class="fa-solid fa-leaf me-1"></i> Disease Detection',
    nav_weather: '<i class="fa-solid fa-cloud-sun-rain me-1"></i> Weather',
    nav_chatbot: '<i class="fa-solid fa-comments me-1"></i> Farmer Assistant',
    nav_advisory: '<i class="fa-solid fa-brain me-1"></i> Adaptive Advisory'
  },
  te: {
    nav_home: '<i class="fa-solid fa-house me-1"></i> హోమ్',
    nav_dashboard: '<i class="fa-solid fa-gauge-high me-1"></i> డ్యాష్‌బోర్డ్',
    nav_crop: '<i class="fa-solid fa-wheat-awn me-1"></i> పంట సిఫార్సు',
    nav_disease: '<i class="fa-solid fa-leaf me-1"></i> తెగులు గుర్తింపు',
    nav_weather: '<i class="fa-solid fa-cloud-sun-rain me-1"></i> వాతావరణం',
    nav_chatbot: '<i class="fa-solid fa-comments me-1"></i> రైతు సహాయకుడు',
    nav_advisory: '<i class="fa-solid fa-brain me-1"></i> అడాప్టివ్ సలహా'
  },
  hi: {
    nav_home: '<i class="fa-solid fa-house me-1"></i> होम',
    nav_dashboard: '<i class="fa-solid fa-gauge-high me-1"></i> डैशबोर्ड',
    nav_crop: '<i class="fa-solid fa-wheat-awn me-1"></i> फसल सिफारिश',
    nav_disease: '<i class="fa-solid fa-leaf me-1"></i> पादप रोग पहचान',
    nav_weather: '<i class="fa-solid fa-cloud-sun-rain me-1"></i> मौसम',
    nav_chatbot: '<i class="fa-solid fa-comments me-1"></i> किसान सहायक',
    nav_advisory: '<i class="fa-solid fa-brain me-1"></i> अनुकूली सलाह'
  }
};

document.addEventListener('DOMContentLoaded', () => {
  initLanguageSelector();
});

function initLanguageSelector() {
  const select = document.getElementById('globalLanguageSelect');
  if (!select) return;

  const savedLang = localStorage.getItem('agro_language') || 'en';
  select.value = savedLang;
  applyLanguage(savedLang);

  select.addEventListener('change', (e) => {
    const lang = e.target.value;
    localStorage.setItem('agro_language', lang);
    applyLanguage(lang);
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
  });
}

function applyLanguage(lang) {
  const strings = UI_STRINGS[lang] || UI_STRINGS.en;
  document.querySelectorAll('[data-lang-key]').forEach(el => {
    const key = el.getAttribute('data-lang-key');
    if (strings[key]) {
      el.innerHTML = strings[key];
    }
  });
}

function showNotification(message, type = 'info') {
  const container = document.getElementById('notificationArea') || createNotificationArea();
  const alertDiv = document.createElement('div');
  const alertClass = type === 'error' ? 'alert-danger' : (type === 'success' ? 'alert-success' : 'alert-info');
  const icon = type === 'error' ? 'fa-circle-exclamation' : (type === 'success' ? 'fa-circle-check' : 'fa-circle-info');
  
  alertDiv.className = `alert ${alertClass} alert-dismissible fade show shadow-sm`;
  alertDiv.role = 'alert';
  alertDiv.innerHTML = `
    <i class="fa-solid ${icon} me-2"></i> ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  container.appendChild(alertDiv);
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => alertDiv.remove(), 250);
  }, 5000);
}

function createNotificationArea() {
  const div = document.createElement('div');
  div.id = 'notificationArea';
  div.style.position = 'fixed';
  div.style.top = '75px';
  div.style.right = '20px';
  div.style.zIndex = '9999';
  div.style.maxWidth = '380px';
  document.body.appendChild(div);
  return div;
}

