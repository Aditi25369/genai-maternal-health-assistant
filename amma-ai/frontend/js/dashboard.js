const API = 'http://localhost:8000/api';

async function loadDashboard() {
  try {
    const res = await fetch(`${API}/dashboard`);
    const data = await res.json();

    document.getElementById('stat-total').textContent = data.total_users ?? 0;
    document.getElementById('stat-high-risk').textContent = data.high_risk_count ?? 0;

    const today = new Date().toDateString();
    const todayCount = (data.flagged_cases || []).filter(c => {
      return new Date(c.timestamp).toDateString() === today;
    }).length;
    document.getElementById('stat-flagged').textContent = todayCount;

    renderCases(data.flagged_cases || []);
  } catch (e) {
    renderCases([]);
    document.getElementById('stat-total').textContent = '—';
    document.getElementById('stat-high-risk').textContent = '—';
    document.getElementById('stat-flagged').textContent = '—';
  }
}

function renderCases(cases) {
  const container = document.getElementById('cases-container');

  if (!cases.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="icon">✅</div>
        <p>No flagged cases right now. All clear!</p>
      </div>
    `;
    return;
  }

  const rows = cases.map(c => {
    const level = c.risk_level || 'UNKNOWN';
    const badgeClass = level === 'CRITICAL' ? 'badge-danger' : level === 'HIGH' ? 'badge-warning' : 'badge-info';
    const time = c.timestamp ? new Date(c.timestamp).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
    }) : '—';

    return `
      <tr>
        <td>
          <div class="case-name">${escapeHtml(c.name || 'Unknown')}</div>
          ${c.phone ? `<div class="case-phone">📞 ${escapeHtml(c.phone)}</div>` : ''}
          ${c.location ? `<div class="case-phone">📍 ${escapeHtml(c.location)}</div>` : ''}
        </td>
        <td><span class="badge ${badgeClass}">${level}</span></td>
        <td><div class="case-symptoms">${escapeHtml(c.symptoms || '—')}</div></td>
        <td><div class="case-action">${escapeHtml(c.recommended_action || '—')}</div></td>
        <td><div class="case-time">${time}</div></td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table class="case-table">
      <thead>
        <tr>
          <th>Patient</th>
          <th>Risk level</th>
          <th>Symptoms</th>
          <th>Recommended action</th>
          <th>Time</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function escapeHtml(text) {
  return String(text).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

loadDashboard();
setInterval(loadDashboard, 30000);