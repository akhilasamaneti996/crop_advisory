/**
 * Crop Recommendation JavaScript
 */

const PRESET_SAMPLES = {
  rice: {
    nitrogen: 90, phosphorus: 42, potassium: 43,
    temperature: 20.88, humidity: 82.0, ph: 6.5, rainfall: 202.9,
    location: 'Telangana Rice Belt', soil_type: 'Clayey', season: 'Kharif (Monsoon)', growth_stage: 'Vegetative Stage'
  },
  cotton: {
    nitrogen: 120, phosphorus: 45, potassium: 20,
    temperature: 24.5, humidity: 65.0, ph: 6.8, rainfall: 80.0,
    location: 'Deccan Plateau', soil_type: 'Black Cotton', season: 'Kharif (Monsoon)', growth_stage: 'Vegetative Stage'
  },
  chickpea: {
    nitrogen: 40, phosphorus: 65, potassium: 80,
    temperature: 18.5, humidity: 16.5, ph: 7.2, rainfall: 75.0,
    location: 'Central Plains', soil_type: 'Loamy', season: 'Rabi (Winter)', growth_stage: 'Flowering / Reproductive'
  },
  coffee: {
    nitrogen: 100, phosphorus: 30, potassium: 30,
    temperature: 26.5, humidity: 60.0, ph: 6.2, rainfall: 160.0,
    location: 'Western Ghats', soil_type: 'Red Sandy', season: 'Year-round', growth_stage: 'Vegetative Stage'
  }
};

let lastCropResult = null;

function fillSample(cropKey) {
  const sample = PRESET_SAMPLES[cropKey];
  if (!sample) return;

  for (const [key, val] of Object.entries(sample)) {
    const el = document.getElementById(key);
    if (el) el.value = val;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('cropForm');
  const btnSubmit = document.getElementById('btnSubmitCrop');
  const errorBox = document.getElementById('cropFormErrors');
  const placeholder = document.getElementById('cropResultPlaceholder');
  const resultCard = document.getElementById('cropResultCard');
  const btnSendAdvisory = document.getElementById('btnSendToAdvisory');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorBox.classList.add('d-none');
      errorBox.innerHTML = '';

      btnSubmit.disabled = true;
      btnSubmit.innerHTML = '<span class="agro-spinner me-2"></span> Analyzing Parameters...';

      const formData = new FormData(form);
      const payload = Object.fromEntries(formData.entries());

      try {
        const response = await fetch('/api/crop/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const res = await response.json();

        if (response.ok && res.status === 'success') {
          lastCropResult = res.data;
          displayCropResult(res.data);
          showNotification(`Recommended: ${res.data.recommended_crop} with ${res.data.confidence}% confidence`, 'success');
        } else {
          // Display validation or server error
          let msg = res.message || 'Validation failed. Please verify your inputs.';
          if (res.errors) {
            msg = '<ul class="mb-0 ps-3">' + Object.values(res.errors).map(err => `<li>${err}</li>`).join('') + '</ul>';
          }
          errorBox.innerHTML = msg;
          errorBox.classList.remove('d-none');
        }
      } catch (err) {
        console.error('Crop prediction error:', err);
        errorBox.innerText = 'Network error communicating with the recommendation engine.';
        errorBox.classList.remove('d-none');
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fa-solid fa-calculator me-2"></i> Predict Best Crop';
      }
    });
  }

  function displayCropResult(data) {
    placeholder.classList.add('d-none');
    resultCard.classList.remove('d-none');

    document.getElementById('resCropName').innerText = data.recommended_crop;
    document.getElementById('resScientificName').innerText = data.crop_info.scientific_name;
    document.getElementById('resConfidence').innerText = `${data.confidence}%`;
    document.getElementById('resCategory').innerText = data.crop_info.category;
    document.getElementById('resSeason').innerText = data.crop_info.season;
    document.getElementById('resDuration').innerText = data.crop_info.duration;
    document.getElementById('resIdealPh').innerText = data.crop_info.ideal_ph;
    document.getElementById('resSuitability').innerText = data.suitability_explanation;
    document.getElementById('resGuidance').innerText = data.cultivation_guidance;

    // Render top candidates
    const candidatesContainer = document.getElementById('resTopCandidates');
    candidatesContainer.innerHTML = (data.top_candidates || []).map(c => `
      <span class="badge bg-light text-dark border">
        ${c.crop}: <strong>${c.confidence}%</strong>
      </span>
    `).join('');
  }

  if (btnSendAdvisory) {
    btnSendAdvisory.addEventListener('click', () => {
      if (lastCropResult) {
        localStorage.setItem('advisory_crop_context', JSON.stringify({
          crop_name: lastCropResult.recommended_crop,
          growth_stage: lastCropResult.input_summary.growth_stage,
          soil: {
            nitrogen: lastCropResult.input_summary.nitrogen,
            phosphorus: lastCropResult.input_summary.phosphorus,
            potassium: lastCropResult.input_summary.potassium,
            ph: lastCropResult.input_summary.ph,
            soil_type: lastCropResult.input_summary.soil_type
          }
        }));
        window.location.href = '/advisory';
      }
    });
  }
});

