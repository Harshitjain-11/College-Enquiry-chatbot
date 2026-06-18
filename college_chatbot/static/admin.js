// ── Intent Chart ──────────────────────────────────────────────
const intentData = window.intentData || [];
const labels = intentData.map(d => d.intent);
const counts = intentData.map(d => d.cnt);

new Chart(document.getElementById('intentChart'), {
  type: 'bar',
  data: {
    labels,
    datasets: [{
      label: 'Queries',
      data: counts,
      backgroundColor: counts.map((_, i) =>
        i === 0 ? 'rgba(123,20,20,0.85)' : `rgba(123,20,20,${0.55 - i * 0.03})`
      ),
      borderColor: 'rgba(123,20,20,0.9)',
      borderWidth: 1,
      borderRadius: 6,
      borderSkipped: false,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#5A0E0E',
        titleColor: '#fff',
        bodyColor: '#ffcccc',
        cornerRadius: 8,
        padding: 10,
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#7A6060', font: { size: 11 } }
      },
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(123,20,20,0.06)' },
        ticks: { color: '#7A6060', stepSize: 1, font: { size: 11 } }
      }
    }
  }
});

// ── Update appointment status ─────────────────────────────────
async function updateStatus(bookingId, action) {
  const url = `/admin/appointment/${bookingId}/${action}`;
  try {
    const res  = await fetch(url, { method: 'POST' });
    const data = await res.json();
    if (data.success) location.reload();
    else alert('Update failed. Please try again.');
  } catch (e) {
    alert('Network error. Please try again.');
  }
}