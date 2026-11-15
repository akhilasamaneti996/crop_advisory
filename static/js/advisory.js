/**
 * Multimodal Adaptive Advisory Engine JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('advisoryForm');
  const btnSubmit = document.getElementById('btnSubmitAdvisory');
  const btnLoadContext = document.getElementById('btnLoadSavedContext');
  const placeholder = document.getElementById('advisoryPlaceholder');
  const resultCard = document.getElementById('advisoryResultCard');

  // Auto-fill from recent scans if available
  autoLoadSavedContext();

  if (btnLoadContext) {
    btnLoadContext.addEventListener('click', () => {
      const loaded = autoLoadSavedContext(true);
      if (!loaded) {
        showNotification('No saved crop or leaf scan data found in this browser session.', 'info');
      }
    });
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      btnSubmit.disabled = true;
      btnSubmit.innerHTML = '<span class="agro-spinner me-2"></span> Synthesizing Multimodal Rules...';

      const payload = {
        crop_name: document.getElementById('advCropName').value.trim(),
        growth_stage: document.getElementById('advGrowthStage').value,
        soil: {
          nitrogen: parseFloat(document.getElementById('advNitrogen').value) || 0,
          phosphorus: parseFloat(document.getElementById('advPhosphorus').value) || 0,
          potassium: parseFloat(document.getElementById('advPotassium').value) || 0,
          ph: parseFloat(document.getElementById('advPh').value) || 6.5,
          soil_type: document.getElementById('advSoilType').value
        },
        weather: {
          temperature: parseFloat(document.getElementById('advTemp').value) || 25.0,
          humidity: parseFloat(document.getElementById('advHumidity').value) || 60.0,
          wind_speed_kmh: parseFloat(document.getElementById('advWind').value) || 10.0,
          upcoming_rain: document.getElementById('advUpcomingRain').checked
        },
        disease: {
          predicted_disease: document.getElementById('advDiseaseName').value,
          is_healthy: document.getElementById('advIsHealthy').value === 'true'
        },
        farmer_query: document.getElementById('advFarmerQuery').value.trim()
      };

      try {
        const response = await fetch('/api/advisory/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const res = await response.json();

        if (response.ok && res.status === 'success') {
          displayAdvisoryResults(res.data);
          showNotification('Comprehensive adaptive advisory synthesized successfully!', 'success');
        } else {
          showNotification(res.message || 'Error generating advisory.', 'error');
        }
      } catch (err) {
        console.error('Advisory generation error:', err);
        showNotification('Network error contacting advisory engine.', 'error');
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fa-solid fa-gears me-2"></i> Synthesize Multimodal Advisory';
      }
    });
  }

  function autoLoadSavedContext(notify = false) {
    let loaded = false;
    const cropData = localStorage.getItem('advisory_crop_context');
    const diseaseData = localStorage.getItem('advisory_disease_context');

    if (cropData) {
      try {
        const parsed = JSON.parse(cropData);
        if (parsed.crop_name) document.getElementById('advCropName').value = parsed.crop_name;
        if (parsed.growth_stage) document.getElementById('advGrowthStage').value = parsed.growth_stage;
        if (parsed.soil) {
          if (parsed.soil.nitrogen !== undefined) document.getElementById('advNitrogen').value = parsed.soil.nitrogen;
          if (parsed.soil.phosphorus !== undefined) document.getElementById('advPhosphorus').value = parsed.soil.phosphorus;
          if (parsed.soil.potassium !== undefined) document.getElementById('advPotassium').value = parsed.soil.potassium;
          if (parsed.soil.ph !== undefined) document.getElementById('advPh').value = parsed.soil.ph;
          if (parsed.soil.soil_type) document.getElementById('advSoilType').value = parsed.soil.soil_type;
        }
        loaded = true;
      } catch (e) {}
    }

    if (diseaseData) {
      try {
        const parsed = JSON.parse(diseaseData);
        if (parsed.crop_name && !cropData) document.getElementById('advCropName').value = parsed.crop_name;
        if (parsed.disease) {
          const disSelect = document.getElementById('advDiseaseName');
          const isHealthySelect = document.getElementById('advIsHealthy');

          if (parsed.disease.is_healthy) {
            disSelect.value = '';
            isHealthySelect.value = 'true';
          } else {
            // Check if matches one of the options
            for (let i = 0; i < disSelect.options.length; i++) {
              if (disSelect.options[i].value.toLowerCase().includes(parsed.disease.predicted_disease.toLowerCase())) {
                disSelect.selectedIndex = i;
                break;
              }
            }
            isHealthySelect.value = 'false';
          }
        }
        loaded = true;
      } catch (e) {}
    }

    if (notify && loaded) {
      showNotification('Loaded parameters from recent crop and leaf scans.', 'success');
    }
    return loaded;
  }

  function displayAdvisoryResults(data) {
    placeholder.classList.add('d-none');
    resultCard.classList.remove('d-none');

    // Risk Banner
    const riskBanner = document.getElementById('advRiskBanner');
    const riskText = document.getElementById('advRiskText');
    riskText.innerText = `${data.risk_level} Risk Level`;

    if (data.risk_level === 'Critical') {
      riskBanner.className = 'agro-card p-3 mb-3 border-start border-4 border-danger bg-danger bg-opacity-10';
      riskText.className = 'fw-bold mb-0 text-danger';
    } else if (data.risk_level === 'High') {
      riskBanner.className = 'agro-card p-3 mb-3 border-start border-4 border-warning bg-warning bg-opacity-10';
      riskText.className = 'fw-bold mb-0 text-dark';
    } else if (data.risk_level === 'Moderate') {
      riskBanner.className = 'agro-card p-3 mb-3 border-start border-4 border-info bg-info bg-opacity-10';
      riskText.className = 'fw-bold mb-0 text-info-emphasis';
    } else {
      riskBanner.className = 'agro-card p-3 mb-3 border-start border-4 border-success bg-success bg-opacity-10';
      riskText.className = 'fw-bold mb-0 text-success';
    }

    document.getElementById('advCropBadge').innerText = data.crop_name;
    document.getElementById('advStageBadge').innerText = data.growth_stage;

    // Decision Factors List
    const factorsList = document.getElementById('advDecisionFactorsList');
    if (data.decision_factors && data.decision_factors.length > 0) {
      factorsList.innerHTML = data.decision_factors.map(f => `<li>${f}</li>`).join('');
    } else {
      factorsList.innerHTML = '<li>Baseline agronomic parameters evaluated.</li>';
    }

    // Advice sections
    document.getElementById('advIrrigationText').innerText = data.irrigation_advice;
    document.getElementById('advFertilizerText').innerText = data.fertilizer_advice;
    document.getElementById('advDiseaseText').innerText = data.disease_advice;
    document.getElementById('advWeatherText').innerText = data.weather_advice;
    document.getElementById('advGeneralText').innerText = data.general_advice;

    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

