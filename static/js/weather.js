/**
 * Weather Intelligence JavaScript
 */

let forecastChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('weatherSearchForm');
  const cityInput = document.getElementById('cityInput');
  const btnRefresh = document.getElementById('btnRefreshWeather');

  // Load default weather on page load
  fetchWeatherData(cityInput.value.trim() || 'Hyderabad');

  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const city = cityInput.value.trim();
      if (city) {
        fetchWeatherData(city);
      }
    });
  }

  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      const city = cityInput.value.trim() || 'Hyderabad';
      fetchWeatherData(city);
    });
  }
});

async function fetchWeatherData(city) {
  const loading = document.getElementById('weatherLoading');
  const dashboard = document.getElementById('weatherDashboard');
  const configNotice = document.getElementById('weatherConfigNotice');

  loading.classList.remove('d-none');
  dashboard.classList.add('d-none');
  configNotice.classList.add('d-none');

  try {
    const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const data = await response.json();

    loading.classList.add('d-none');

    if (data.status === 'api_key_missing') {
      configNotice.classList.remove('d-none');
      return;
    }

    if (data.status === 'error') {
      showNotification(data.message || 'Error fetching weather.', 'error');
      configNotice.classList.remove('d-none');
      return;
    }

    if (data.status === 'success') {
      displayWeatherData(data);
      dashboard.classList.remove('d-none');
    }
  } catch (err) {
    loading.classList.add('d-none');
    console.error('Weather API error:', err);
    showNotification('Network error contacting weather service.', 'error');
  }
}

function displayWeatherData(data) {
  document.getElementById('weatherLocationBadge').innerText = `${data.city}, ${data.country}`;
  document.getElementById('weatherIcon').src = data.icon_url;
  document.getElementById('weatherTemp').innerText = `${data.temperature} °C`;
  document.getElementById('weatherCondition').innerText = data.weather_description;
  document.getElementById('weatherFeelsLike').innerText = `${data.feels_like} °C`;
  document.getElementById('weatherRain').innerText = `${data.rainfall_mm} mm`;

  document.getElementById('weatherHumidity').innerText = `${data.humidity} %`;
  document.getElementById('weatherWind').innerText = `${data.wind_speed_kmh} km/h`;
  document.getElementById('weatherPressure').innerText = `${data.pressure} hPa`;
  document.getElementById('weatherRainSummary').innerText = `${data.rainfall_mm} mm`;

  // Render Agricultural Suggestions
  const container = document.getElementById('agriSuggestionsContainer');
  if (container) {
    container.innerHTML = (data.agricultural_advisory || []).map(s => {
      let borderClass = 'border-success';
      let iconClass = 'fa-circle-check text-success';
      if (s.type === 'warning') {
        borderClass = 'border-warning';
        iconClass = 'fa-triangle-exclamation text-warning';
      } else if (s.type === 'danger') {
        borderClass = 'border-danger';
        iconClass = 'fa-circle-xmark text-danger';
      } else if (s.type === 'info') {
        borderClass = 'border-primary';
        iconClass = 'fa-circle-info text-primary';
      }

      return `
        <div class="col-md-6">
          <div class="p-3 bg-light rounded-3 border-start border-4 ${borderClass} h-100">
            <div class="d-flex align-items-center gap-2 mb-1">
              <i class="fa-solid ${iconClass}"></i>
              <h6 class="fw-bold mb-0 text-dark small">${s.title}</h6>
            </div>
            <p class="small text-muted mb-0">${s.description}</p>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Forecast Chart if forecast data exists
  if (data.forecast && data.forecast.length > 0) {
    renderForecastChart(data.forecast);
  }
}

function renderForecastChart(forecastList) {
  const ctx = document.getElementById('weatherForecastChart');
  if (!ctx) return;

  const labels = forecastList.map(item => item.dt_txt.slice(5, 16));
  const temps = forecastList.map(item => item.temp);
  const humidities = forecastList.map(item => item.humidity);

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: temps,
          borderColor: '#e76f51',
          backgroundColor: 'rgba(231, 111, 81, 0.1)',
          yAxisID: 'yTemp',
          tension: 0.35,
          fill: true
        },
        {
          label: 'Humidity (%)',
          data: humidities,
          borderColor: '#2a9d8f',
          backgroundColor: 'rgba(42, 157, 143, 0.1)',
          yAxisID: 'yHumidity',
          tension: 0.35,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          backgroundColor: '#1b4332',
          padding: 10,
          cornerRadius: 6
        }
      },
      scales: {
        yTemp: {
          type: 'linear',
          display: true,
          position: 'left',
          title: { display: true, text: 'Temperature (°C)' }
        },
        yHumidity: {
          type: 'linear',
          display: true,
          position: 'right',
          title: { display: true, text: 'Humidity (%)' },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

