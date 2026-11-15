/**
 * Dashboard JavaScript - Backend Data Fetching & Chart.js Rendering
 */

let cropChartInstance = null;
let diseaseChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  fetchDashboardData();

  const btnRefresh = document.getElementById('btnRefreshDashboard');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      btnRefresh.innerHTML = '<span class="agro-spinner me-1"></span> Refreshing...';
      fetchDashboardData().finally(() => {
        btnRefresh.innerHTML = '<i class="fa-solid fa-arrows-rotate me-1"></i> Refresh Data';
      });
    });
  }
});

async function fetchDashboardData() {
  try {
    const response = await fetch('/api/dashboard/stats');
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const res = await response.json();

    if (res.status === 'success') {
      updateStatCounters(res.stats);
      renderRecentActivities(res.recent_activities);
      renderCharts(res.charts);
    }
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    showNotification('Unable to fetch live dashboard data.', 'error');
  }
}

function updateStatCounters(stats) {
  document.getElementById('statCrops').innerText = stats.total_crop_recommendations || 0;
  document.getElementById('statDiseases').innerText = stats.total_disease_analyses || 0;
  document.getElementById('statQueries').innerText = stats.total_farmer_queries || 0;
  document.getElementById('statAdvisories').innerText = stats.total_advisories || 0;
}

function renderRecentActivities(activities) {
  const tbody = document.getElementById('activityTableBody');
  if (!tbody) return;

  if (!activities || activities.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center py-4 text-muted">
          <i class="fa-solid fa-seedling me-1"></i> No activity recorded yet. Start by requesting a crop recommendation or scanning a plant leaf.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = activities.map(act => {
    let badgeClass = 'badge-agro-info';
    let iconClass = 'fa-circle-info';
    if (act.type === 'crop') {
      badgeClass = 'badge-agro-success';
      iconClass = 'fa-wheat-awn';
    } else if (act.type === 'disease') {
      badgeClass = act.badge === 'Healthy' ? 'badge-agro-success' : 'badge-agro-danger';
      iconClass = 'fa-leaf';
    } else if (act.type === 'advisory') {
      badgeClass = 'badge-agro-warning';
      iconClass = 'fa-brain';
    }

    return `
      <tr>
        <td>
          <span class="badge ${badgeClass}">
            <i class="fa-solid ${iconClass} me-1"></i> ${act.badge}
          </span>
        </td>
        <td>
          <div class="fw-semibold text-dark small">${act.title}</div>
        </td>
        <td>
          <div class="text-muted small">${act.subtitle}</div>
        </td>
        <td>
          <span class="text-muted small">${act.timestamp}</span>
        </td>
      </tr>
    `;
  }).join('');
}

function renderCharts(charts) {
  renderCropChart(charts.crop_distribution);
  renderDiseaseChart(charts.disease_breakdown);
}

function renderCropChart(cropData) {
  const ctx = document.getElementById('cropChart');
  const emptyPlaceholder = document.getElementById('cropChartEmpty');
  if (!ctx) return;

  if (!cropData || !cropData.labels || cropData.labels.length === 0) {
    ctx.classList.add('d-none');
    if (emptyPlaceholder) emptyPlaceholder.classList.remove('d-none');
    return;
  }

  ctx.classList.remove('d-none');
  if (emptyPlaceholder) emptyPlaceholder.classList.add('d-none');

  if (cropChartInstance) {
    cropChartInstance.destroy();
  }

  cropChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: cropData.labels,
      datasets: [{
        label: 'Recommendations Count',
        data: cropData.data,
        backgroundColor: '#2d6a4f',
        borderRadius: 6,
        maxBarThickness: 45
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1b4332',
          padding: 10,
          cornerRadius: 6
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 },
          grid: { color: '#eef2ee' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderDiseaseChart(diseaseData) {
  const ctx = document.getElementById('diseaseChart');
  const emptyPlaceholder = document.getElementById('diseaseChartEmpty');
  if (!ctx) return;

  const total = (diseaseData.data || []).reduce((a, b) => a + b, 0);
  if (total === 0) {
    ctx.classList.add('d-none');
    if (emptyPlaceholder) emptyPlaceholder.classList.remove('d-none');
    return;
  }

  ctx.classList.remove('d-none');
  if (emptyPlaceholder) emptyPlaceholder.classList.add('d-none');

  if (diseaseChartInstance) {
    diseaseChartInstance.destroy();
  }

  diseaseChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: diseaseData.labels,
      datasets: [{
        data: diseaseData.data,
        backgroundColor: ['#52b788', '#e63946'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 15, font: { size: 12 } }
        },
        tooltip: {
          backgroundColor: '#1b4332',
          padding: 10,
          cornerRadius: 6
        }
      },
      cutout: '65%'
    }
  });
}

