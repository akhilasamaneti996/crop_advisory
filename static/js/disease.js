/**
 * Plant Disease Detection JavaScript
 */

let selectedFile = null;
let lastDiseaseResult = null;

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzoneArea');
  const fileInput = document.getElementById('leafImageInput');
  const dropzonePrompt = document.getElementById('dropzonePrompt');
  const previewContainer = document.getElementById('previewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const fileNameBadge = document.getElementById('fileNameBadge');
  const btnRemove = document.getElementById('btnRemoveImage');
  const btnAnalyze = document.getElementById('btnAnalyzeImage');
  const form = document.getElementById('diseaseForm');
  const errorBox = document.getElementById('diseaseErrorBox');
  const placeholder = document.getElementById('diseaseResultPlaceholder');
  const resultCard = document.getElementById('diseaseResultCard');
  const btnSendAdvisory = document.getElementById('btnSendDiseaseAdvisory');

  // Trigger file selection on dropzone click (if not clicking remove button)
  if (dropzone) {
    dropzone.addEventListener('click', (e) => {
      if (e.target.closest('#btnRemoveImage')) return;
      fileInput.click();
    });

    // Drag-and-drop events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFileSelect(files[0]);
      }
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });
  }

  function handleFileSelect(file) {
    errorBox.classList.add('d-none');
    errorBox.innerHTML = '';

    // Validate type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type.toLowerCase())) {
      showError('Invalid file type. Please upload a JPG, JPEG, or PNG image.');
      return;
    }

    // Validate size (max 16 MB)
    if (file.size > 16 * 1024 * 1024) {
      showError('File exceeds 16 MB limit. Please select a smaller image.');
      return;
    }

    selectedFile = file;
    fileNameBadge.innerText = file.name;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      dropzonePrompt.classList.add('d-none');
      previewContainer.classList.remove('d-none');
      btnAnalyze.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  if (btnRemove) {
    btnRemove.addEventListener('click', (e) => {
      e.stopPropagation();
      resetUpload();
    });
  }

  function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    previewContainer.classList.add('d-none');
    dropzonePrompt.classList.remove('d-none');
    btnAnalyze.disabled = true;
    errorBox.classList.add('d-none');
  }

  function showError(msg) {
    errorBox.innerText = msg;
    errorBox.classList.remove('d-none');
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!selectedFile) {
        showError('Please select or drop an image file first.');
        return;
      }

      errorBox.classList.add('d-none');
      btnAnalyze.disabled = true;
      btnAnalyze.innerHTML = '<span class="agro-spinner me-2"></span> Analyzing Leaf Pathology...';

      const formData = new FormData();
      formData.append('image', selectedFile);

      try {
        const response = await fetch('/api/disease/predict', {
          method: 'POST',
          body: formData
        });

        const res = await response.json();

        if (response.ok && res.status === 'success') {
          lastDiseaseResult = res.data;
          displayDiseaseResult(res.data);
          showNotification(`Diagnosis: ${res.data.predicted_disease} (${res.data.confidence}%)`, 'success');
        } else {
          showError(res.message || 'Disease detection failed.');
        }
      } catch (err) {
        console.error('Analysis error:', err);
        showError('Network error uploading and processing the image.');
      } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-microscope me-2"></i> Analyze Leaf Image';
      }
    });
  }

  function displayDiseaseResult(data) {
    placeholder.classList.add('d-none');
    resultCard.classList.remove('d-none');

    // Health badge
    const badge = document.getElementById('resHealthBadge');
    if (data.is_healthy) {
      badge.className = 'badge badge-agro-success mb-1';
      badge.innerText = 'Healthy Leaf';
    } else {
      badge.className = 'badge badge-agro-danger mb-1';
      badge.innerText = 'Attention Required';
    }

    document.getElementById('resDiseaseName').innerText = data.predicted_disease;
    document.getElementById('resCropDetected').innerText = `Detected Crop: ${data.detected_crop}`;
    document.getElementById('resDiseaseConfidence').innerText = `${data.confidence}%`;
    document.querySelector('#resPathogenType span').innerText = data.pathogen_type || 'Biological Pathogen';
    document.getElementById('resDiseaseDesc').innerText = data.description;

    // Render symptoms
    const symptomsEl = document.getElementById('resSymptomsList');
    symptomsEl.innerHTML = (data.symptoms || []).map(s => `<li>${s}</li>`).join('');

    // Render treatments
    const treatmentsEl = document.getElementById('resTreatmentsList');
    treatmentsEl.innerHTML = (data.treatments || []).map(t => `<li>${t}</li>`).join('');

    // Render preventions
    const preventionsEl = document.getElementById('resPreventionsList');
    preventionsEl.innerHTML = (data.preventions || []).map(p => `<li>${p}</li>`).join('');
  }

  if (btnSendAdvisory) {
    btnSendAdvisory.addEventListener('click', () => {
      if (lastDiseaseResult) {
        localStorage.setItem('advisory_disease_context', JSON.stringify({
          crop_name: lastDiseaseResult.detected_crop,
          disease: {
            predicted_disease: lastDiseaseResult.predicted_disease,
            is_healthy: lastDiseaseResult.is_healthy,
            confidence: lastDiseaseResult.confidence,
            pathogen_type: lastDiseaseResult.pathogen_type
          }
        }));
        window.location.href = '/advisory';
      }
    });
  }
});

