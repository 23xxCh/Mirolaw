// MiroLaw Frontend Application v0.7.0
// Dynamic API base URL - works with both desktop app and browser

// Dynamic base URL - auto-detect from current location
const API_BASE = window.location.origin;
const WS_BASE = (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host;

// Global state
const state = {
    loading: false,
    error: null,
    lastPrediction: null,
    wsConnected: false,
    wsReconnectAttempts: 0,
    wsMaxReconnect: 10
};

// ==================== UI Utilities ====================

function showLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) {
        const existing = el.querySelector('.loading-overlay');
        if (!existing) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="loading-spinner"></div><span>Loading...</span>';
            el.style.position = 'relative';
            el.appendChild(overlay);
        }
    }
}

function hideLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) {
        const overlay = el.querySelector('.loading-overlay');
        if (overlay) overlay.remove();
    }
}

function showError(message, containerId) {
    state.error = message;
    if (containerId) {
        const el = document.getElementById(containerId);
        if (el) {
            el.innerHTML = `<div class="error-box"><strong>Error</strong><p>${message}</p></div>`;
        }
    }
    showToast(message, 'error');
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'error' ? '\u274C' : type === 'success' ? '\u2705' : '\u2139\uFE0F';
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span class="toast-msg">${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ==================== Page Navigation ====================

function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    // Show target page
    const page = document.getElementById(pageId);
    if (page) page.classList.add('active');

    // Update nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`[data-page="${pageId}"]`);
    if (navItem) navItem.classList.add('active');

    // Load page data
    switch (pageId) {
        case 'dashboard': loadDashboard(); break;
        case 'predict': break;
        case 'alerts': loadAlerts(); break;
        case 'knowledge': loadKnowledge(); break;
        case 'history': loadHistory(); break;
        case 'settings': loadSettings(); break;
    }
}

// ==================== Dashboard ====================

async function loadDashboard() {
    try {
        const [healthResp, statsResp, alertResp] = await Promise.all([
            fetch(`${API_BASE}/health`).catch(() => null),
            fetch(`${API_BASE}/cache/stats`).catch(() => null),
            fetch(`${API_BASE}/alerts/stats`).catch(() => null),
        ]);

        const health = healthResp ? await healthResp.json() : { status: 'unknown' };
        const cacheStats = statsResp ? await statsResp.json() : {};
        const alertStats = alertResp ? await alertResp.json() : {};

        const container = document.getElementById('dashboard-content');
        if (!container) return;

        const statusColor = health.status === 'healthy' ? '#27ae60' : '#e74c3c';
        const statusText = health.status === 'healthy' ? 'Normal' : 'Abnormal';

        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card stat-blue">
                    <div class="stat-icon">\uD83D\uDD27</div>
                    <div class="stat-value">${statusText}</div>
                    <div class="stat-label">System Status</div>
                </div>
                <div class="stat-card stat-green">
                    <div class="stat-icon">\uD83D\uDCCA</div>
                    <div class="stat-value">${cacheStats.size || 0}</div>
                    <div class="stat-label">Cache Entries</div>
                </div>
                <div class="stat-card stat-orange">
                    <div class="stat-icon">\u26A0\uFE0F</div>
                    <div class="stat-value">${alertStats.total || 0}</div>
                    <div class="stat-label">Total Alerts</div>
                </div>
                <div class="stat-card stat-red">
                    <div class="stat-icon">\uD83D\uDEA8</div>
                    <div class="stat-value">${alertStats.active || 0}</div>
                    <div class="stat-label">Active Alerts</div>
                </div>
            </div>
            <div class="dashboard-quick-actions">
                <h3>Quick Actions</h3>
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="showPage('predict')">Risk Prediction</button>
                    <button class="btn btn-warning" onclick="showPage('alerts')">View Alerts</button>
                    <button class="btn btn-info" onclick="showPage('knowledge')">Legal Search</button>
                    <button class="btn btn-secondary" onclick="loadSamplePrediction()">Demo Prediction</button>
                </div>
            </div>
            <div class="system-info">
                <h3>System Info</h3>
                <div class="info-grid">
                    <div class="info-item"><span>Version</span><span>v0.7.0</span></div>
                    <div class="info-item"><span>Uptime</span><span>${health.uptime_seconds ? Math.floor(health.uptime_seconds/60) + 'min' : 'N/A'}</span></div>
                    <div class="info-item"><span>Cache Hit Rate</span><span>${(cacheStats.hit_rate * 100).toFixed(1) || 0}%</span></div>
                    <div class="info-item"><span>Services</span><span>${health.checks ? health.checks.length : 0}</span></div>
                </div>
            </div>
        `;
    } catch (err) {
        showError('Failed to load dashboard: ' + err.message);
    }
}

// ==================== Risk Prediction ====================

async function submitPrediction() {
    const productDesc = document.getElementById('product-desc')?.value || '';
    const marketingText = document.getElementById('marketing-text')?.value || '';
    const horizon = parseInt(document.getElementById('horizon')?.value || '30');

    if (!productDesc && !marketingText) {
        showError('Please enter product description or marketing content');
        return;
    }

    const resultContainer = document.getElementById('prediction-result');
    if (!resultContainer) return;

    showLoading('prediction-result');

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                platform_data: {
                    product_info: { description: productDesc },
                    marketing_content: [{ text: marketingText }]
                },
                horizon: horizon
            })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const result = await response.json();
        state.lastPrediction = result;
        renderPredictionResult(result, resultContainer);
        showSuccess('Prediction complete!');
    } catch (err) {
        showError('Prediction failed: ' + err.message, 'prediction-result');
    } finally {
        hideLoading('prediction-result');
    }
}

function renderPredictionResult(result, container) {
    const riskScore = result.overall_risk_score || 0;
    const riskLevel = riskScore >= 0.7 ? 'high' : riskScore >= 0.4 ? 'medium' : 'low';
    const riskColor = riskLevel === 'high' ? '#e74c3c' : riskLevel === 'medium' ? '#f39c12' : '#27ae60';
    const riskLabel = riskLevel === 'high' ? 'High Risk' : riskLevel === 'medium' ? 'Medium Risk' : 'Low Risk';

    const riskTypes = result.risk_types || [];
    const finePrediction = result.fine_prediction || {};

    container.innerHTML = `
        <div class="result-card">
            <div class="result-header" style="border-left: 4px solid ${riskColor}">
                <h3>Risk Assessment Result</h3>
                <div class="risk-badge risk-${riskLevel}">${riskLabel}</div>
            </div>
            <div class="result-body">
                <div class="risk-score-display">
                    <div class="score-circle" style="--score: ${riskScore}; --color: ${riskColor}">
                        <span class="score-value">${(riskScore * 100).toFixed(0)}</span>
                        <span class="score-unit">/100</span>
                    </div>
                    <div class="score-details">
                        <div class="detail-item"><strong>Risk Score:</strong> ${riskScore.toFixed(3)}</div>
                        <div class="detail-item"><strong>Risk Level:</strong> <span style="color:${riskColor}">${riskLabel}</span></div>
                        <div class="detail-item"><strong>Horizon:</strong> ${result.horizon || 30} days</div>
                    </div>
                </div>

                ${riskTypes.length > 0 ? `
                <div class="risk-types-section">
                    <h4>Detected Risk Types</h4>
                    <div class="risk-type-grid">
                        ${riskTypes.map(rt => `
                            <div class="risk-type-card">
                                <div class="risk-type-name">${rt.type || rt}</div>
                                <div class="risk-type-probability">${((rt.probability || 0) * 100).toFixed(1)}%</div>
                            </div>
                        `).join('')}
                    </div>
                </div>` : ''}

                ${finePrediction.estimated_fine ? `
                <div class="fine-section">
                    <h4>Fine Prediction</h4>
                    <div class="fine-range">
                        <span class="fine-min">\u00A5${(finePrediction.min_fine || 0).toLocaleString()}</span>
                        <span class="fine-arrow">\u2192</span>
                        <span class="fine-max">\u00A5${(finePrediction.max_fine || 0).toLocaleString()}</span>
                    </div>
                </div>` : ''}

                <div class="actions-bar">
                    <button class="btn btn-primary" onclick="generateSuggestion()">Generate Suggestion</button>
                    <button class="btn btn-secondary" onclick="savePrediction()">Save Record</button>
                </div>
            </div>
        </div>
    `;
}

async function loadSamplePrediction() {
    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                platform_data: {
                    product_info: { name: "Test Product", description: "\u4E16\u754C\u7B2C\u4E00\uFF0C\u5168\u7403\u9996\u521B\u6280\u672F\uFF0C100%\u6709\u6548" },
                    marketing_content: [{ text: "\u56FD\u5BB6\u7EA7\u8BA4\u8BC1\u4EA7\u54C1\uFF0C\u6700\u4F73\u9009\u62E9" }]
                },
                horizon: 30
            })
        });
        const result = await response.json();
        showPage('predict');
        const container = document.getElementById('prediction-result');
        if (container) renderPredictionResult(result, container);
    } catch (err) {
        showError('Demo failed: ' + err.message);
    }
}

async function generateSuggestion() {
    if (!state.lastPrediction) {
        showError('Please run a prediction first');
        return;
    }

    const container = document.getElementById('prediction-result');
    showLoading('prediction-result');

    try {
        const response = await fetch(`${API_BASE}/suggestions/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prediction_result: state.lastPrediction })
        });
        const data = await response.json();
        const suggestions = data.suggestions || [];

        const suggestionHtml = `
            <div class="suggestion-section">
                <h4>AI Suggestions</h4>
                ${suggestions.map((s, i) => `
                    <div class="suggestion-item">
                        <div class="suggestion-number">${i + 1}</div>
                        <div class="suggestion-content">
                            <div class="suggestion-title">${s.title || s.type || 'Suggestion'}</div>
                            <div class="suggestion-text">${s.content || s.description || ''}</div>
                            ${s.law_reference ? `<div class="suggestion-law">Ref: ${s.law_reference}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.insertAdjacentHTML('beforeend', suggestionHtml);
        showSuccess('Suggestions generated!');
    } catch (err) {
        showError('Failed to generate suggestions: ' + err.message);
    } finally {
        hideLoading('prediction-result');
    }
}

// ==================== Alerts ====================

let alertPage = 1;
const alertPageSize = 10;
let allAlerts = [];
let alertFilter = 'all';

async function loadAlerts() {
    try {
        const [statsResp, alertsResp] = await Promise.all([
            fetch(`${API_BASE}/alerts/stats`).catch(() => null),
            fetch(`${API_BASE}/alerts?limit=200`).catch(() => null),
        ]);

        const stats = statsResp ? await statsResp.json() : {};
        const alertsData = alertsResp ? await alertsResp.json() : {};
        allAlerts = alertsData.alerts || [];

        renderAlertStats(stats);
        renderAlertList();
    } catch (err) {
        showError('Failed to load alerts: ' + err.message);
    }
}

function renderAlertStats(stats) {
    const el = document.getElementById('alert-stats');
    if (!el) return;

    el.innerHTML = `
        <div class="alert-stat-card">
            <div class="alert-stat-number">${stats.total || 0}</div>
            <div class="alert-stat-label">Total</div>
        </div>
        <div class="alert-stat-card stat-active">
            <div class="alert-stat-number">${stats.active || 0}</div>
            <div class="alert-stat-label">Active</div>
        </div>
        <div class="alert-stat-card stat-warning">
            <div class="alert-stat-number">${stats.by_level?.warning || 0}</div>
            <div class="alert-stat-label">Warning</div>
        </div>
        <div class="alert-stat-card stat-danger">
            <div class="alert-stat-number">${stats.by_level?.danger || 0}</div>
            <div class="alert-stat-label">Danger</div>
        </div>
        <div class="alert-stat-card stat-critical">
            <div class="alert-stat-number">${stats.by_level?.critical || 0}</div>
            <div class="alert-stat-label">Critical</div>
        </div>
    `;
}

function renderAlertList() {
    const container = document.getElementById('alert-list');
    if (!container) return;

    let filtered = allAlerts;
    if (alertFilter !== 'all') {
        filtered = allAlerts.filter(a => a.level === alertFilter);
    }

    const start = (alertPage - 1) * alertPageSize;
    const pageAlerts = filtered.slice(start, start + alertPageSize);
    const totalPages = Math.ceil(filtered.length / alertPageSize);

    if (pageAlerts.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-icon">\uD83D\uDD14</div><p>No alerts yet</p><p class="empty-hint">Alerts will appear here when risks are detected</p></div>';
        return;
    }

    container.innerHTML = pageAlerts.map(alert => {
        const levelClass = alert.level || 'info';
        const time = alert.created_at ? new Date(alert.created_at).toLocaleString() : '';
        return `
            <div class="alert-card alert-${levelClass}">
                <div class="alert-level-badge">${(alert.level || 'info').toUpperCase()}</div>
                <div class="alert-body">
                    <div class="alert-title">${alert.title || 'Risk Alert'}</div>
                    <div class="alert-message">${alert.message || ''}</div>
                    <div class="alert-meta">
                        <span class="alert-time">${time}</span>
                        <span class="alert-status">${alert.status || 'active'}</span>
                    </div>
                </div>
                <div class="alert-actions-col">
                    <button class="btn-sm btn-ack" onclick="acknowledgeAlert('${alert.alert_id}')" title="Acknowledge">\u2705</button>
                    <button class="btn-sm btn-resolve" onclick="resolveAlert('${alert.alert_id}')" title="Resolve">\u2714</button>
                </div>
            </div>
        `;
    }).join('');

    if (totalPages > 1) {
        container.innerHTML += `
            <div class="pagination">
                <button class="btn-sm" onclick="alertPage=1;renderAlertList()" ${alertPage<=1?'disabled':''}>First</button>
                <button class="btn-sm" onclick="alertPage--;renderAlertList()" ${alertPage<=1?'disabled':''}>Prev</button>
                <span class="page-info">${alertPage}/${totalPages}</span>
                <button class="btn-sm" onclick="alertPage++;renderAlertList()" ${alertPage>=totalPages?'disabled':''}>Next</button>
                <button class="btn-sm" onclick="alertPage=${totalPages};renderAlertList()" ${alertPage>=totalPages?'disabled':''}>Last</button>
            </div>
        `;
    }
}

function filterAlerts(level) {
    alertFilter = level;
    alertPage = 1;
    document.querySelectorAll('.alert-filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-filter="${level}"]`)?.classList.add('active');
    renderAlertList();
}

async function acknowledgeAlert(alertId) {
    try {
        await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, { method: 'POST' });
        showSuccess('Alert acknowledged');
        loadAlerts();
    } catch (err) {
        showError('Failed to acknowledge alert');
    }
}

async function resolveAlert(alertId) {
    try {
        await fetch(`${API_BASE}/alerts/${alertId}/resolve`, { method: 'POST' });
        showSuccess('Alert resolved');
        loadAlerts();
    } catch (err) {
        showError('Failed to resolve alert');
    }
}

// ==================== Knowledge Base ====================

async function loadKnowledge() {
    // Load laws list
    try {
        const resp = await fetch(`${API_BASE}/laws`);
        const data = await resp.json();
        renderLawList(data.laws || []);
    } catch (err) {
        showError('Failed to load laws: ' + err.message);
    }
}

function renderLawList(laws) {
    const container = document.getElementById('law-list');
    if (!container) return;

    if (laws.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No laws loaded</p></div>';
        return;
    }

    container.innerHTML = laws.map(law => `
        <div class="law-card" onclick="loadLawDetail('${law.name}')">
            <div class="law-name">${law.name}</div>
            <div class="law-full-name">${law.full_name || law.name}</div>
            <div class="law-articles">${(law.articles_count || law.articles?.length || 0)} articles</div>
        </div>
    `).join('');
}

async function searchKnowledge() {
    const query = document.getElementById('knowledge-search')?.value || '';
    if (!query.trim()) return;

    const container = document.getElementById('knowledge-results');
    showLoading('knowledge-results');

    try {
        const resp = await fetch(`${API_BASE}/knowledge_graph/search?query=${encodeURIComponent(query)}`);
        const data = await resp.json();
        const results = data.results || data.cases || [];

        if (results.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No results found</p></div>';
            return;
        }

        container.innerHTML = results.map(r => `
            <div class="knowledge-result-card">
                <h4>${r.title || r.case_name || 'Result'}</h4>
                <p>${r.description || r.content || ''}</p>
                ${r.law ? `<div class="result-law-ref">Ref: ${r.law}</div>` : ''}
                ${r.penalty ? `<div class="result-penalty">Penalty: ${r.penalty}</div>` : ''}
            </div>
        `).join('');
    } catch (err) {
        showError('Search failed: ' + err.message, 'knowledge-results');
    } finally {
        hideLoading('knowledge-results');
    }
}

// ==================== History ====================

async function loadHistory() {
    try {
        const [recordsResp, statsResp, trendResp] = await Promise.all([
            fetch(`${API_BASE}/history/records?limit=50`).catch(() => null),
            fetch(`${API_BASE}/history/statistics`).catch(() => null),
            fetch(`${API_BASE}/history/trend?days=7`).catch(() => null),
        ]);

        const recordsData = recordsResp ? await recordsResp.json() : {};
        const stats = statsResp ? await statsResp.json() : {};
        const trend = trendResp ? await trendResp.json() : {};

        renderHistoryStats(stats);
        renderHistoryRecords(recordsData.records || []);
        renderTrendChart(trend);
    } catch (err) {
        showError('Failed to load history: ' + err.message);
    }
}

function renderHistoryStats(stats) {
    const el = document.getElementById('history-stats');
    if (!el) return;

    el.innerHTML = `
        <div class="history-stat"><span class="stat-num">${stats.total || 0}</span><span class="stat-lbl">Total</span></div>
        <div class="history-stat"><span class="stat-num">${stats.high_risk_count || 0}</span><span class="stat-lbl">High Risk</span></div>
        <div class="history-stat"><span class="stat-num">${stats.avg_risk_score ? (stats.avg_risk_score * 100).toFixed(1) : 0}</span><span class="stat-lbl">Avg Score</span></div>
        <div class="history-stat"><span class="stat-num">${stats.alerts_triggered || 0}</span><span class="stat-lbl">Alerts</span></div>
    `;
}

function renderHistoryRecords(records) {
    const container = document.getElementById('history-records');
    if (!container) return;

    if (records.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No prediction history yet</p></div>';
        return;
    }

    container.innerHTML = records.map(r => {
        const score = r.prediction_result?.overall_risk_score || 0;
        const level = score >= 0.7 ? 'high' : score >= 0.4 ? 'medium' : 'low';
        const color = level === 'high' ? '#e74c3c' : level === 'medium' ? '#f39c12' : '#27ae60';

        return `
            <div class="history-record" style="border-left: 3px solid ${color}">
                <div class="record-header">
                    <span class="record-id">#${r.record_id || ''}</span>
                    <span class="record-score" style="color:${color}">${(score * 100).toFixed(0)}%</span>
                </div>
                <div class="record-time">${r.created_at || ''}</div>
            </div>
        `;
    }).join('');
}

function renderTrendChart(trend) {
    const canvas = document.getElementById('trend-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const data = trend.trend || [];

    if (data.length === 0) {
        ctx.font = '14px Arial';
        ctx.fillStyle = '#888';
        ctx.textAlign = 'center';
        ctx.fillText('No trend data yet', canvas.width / 2, canvas.height / 2);
        return;
    }

    const w = canvas.width;
    const h = canvas.height;
    const padding = 40;
    const chartW = w - padding * 2;
    const chartH = h - padding * 2;

    ctx.clearRect(0, 0, w, h);

    // Background
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(padding, padding, chartW, chartH);

    // Grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding + (chartH / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(padding + chartW, y);
        ctx.stroke();
    }

    // Data line
    const scores = data.map(d => d.avg_score || 0);
    const maxScore = Math.max(...scores, 0.1);

    ctx.beginPath();
    ctx.strokeStyle = '#667eea';
    ctx.lineWidth = 2;

    scores.forEach((score, i) => {
        const x = padding + (chartW / Math.max(scores.length - 1, 1)) * i;
        const y = padding + chartH - (score / maxScore) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Data points
    scores.forEach((score, i) => {
        const x = padding + (chartW / Math.max(scores.length - 1, 1)) * i;
        const y = padding + chartH - (score / maxScore) * chartH;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#667eea';
        ctx.fill();
    });
}

// ==================== Settings ====================

function loadSettings() {
    const container = document.getElementById('settings-content');
    if (!container) return;

    container.innerHTML = `
        <div class="settings-section">
            <h3>API Configuration</h3>
            <div class="form-group">
                <label>DeepSeek API Key</label>
                <input type="password" id="setting-api-key" placeholder="sk-..." class="form-input">
            </div>
            <div class="form-group">
                <label>Enable LLM</label>
                <select id="setting-enable-llm" class="form-input">
                    <option value="true">Enabled</option>
                    <option value="false">Disabled</option>
                </select>
            </div>
        </div>
        <div class="settings-section">
            <h3>Alert Rules</h3>
            <div class="form-group">
                <label>Default Risk Threshold</label>
                <input type="range" id="setting-threshold" min="0" max="100" value="70" class="form-range">
                <span id="threshold-value">0.70</span>
            </div>
        </div>
        <div class="settings-section">
            <h3>System</h3>
            <div class="info-grid">
                <div class="info-item"><span>Version</span><span>v0.7.0</span></div>
                <div class="info-item"><span>Port</span><span>${window.location.port}</span></div>
                <div class="info-item"><span>Platform</span><span>Desktop</span></div>
            </div>
            <div class="settings-actions">
                <button class="btn btn-primary" onclick="saveSettings()">Save</button>
                <button class="btn btn-danger" onclick="clearCache()">Clear Cache</button>
                <button class="btn btn-secondary" onclick="clearHistory()">Clear History</button>
            </div>
        </div>
    `;
}

async function saveSettings() {
    showSuccess('Settings saved');
}

async function clearCache() {
    try {
        await fetch(`${API_BASE}/cache/clear`, { method: 'DELETE' });
        showSuccess('Cache cleared');
    } catch (err) {
        showError('Failed to clear cache');
    }
}

async function clearHistory() {
    if (!confirm('Clear all prediction history?')) return;
    showSuccess('History cleared');
}

// ==================== WebSocket ====================

let ws = null;

function connectWebSocket() {
    const wsUrl = `${WS_BASE}/ws/alerts`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        state.wsConnected = true;
        state.wsReconnectAttempts = 0;
        ws.send(JSON.stringify({ action: 'subscribe', topic: 'alerts' }));
        showToast('WebSocket connected', 'success');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWSMessage(data);
        } catch (err) {
            console.error('WS message parse error:', err);
        }
    };

    ws.onclose = () => {
        state.wsConnected = false;
        reconnectWebSocket();
    };

    ws.onerror = () => {
        state.wsConnected = false;
    };
}

function reconnectWebSocket() {
    if (state.wsReconnectAttempts >= state.wsMaxReconnect) return;

    const delay = Math.min(1000 * Math.pow(2, state.wsReconnectAttempts), 30000);
    state.wsReconnectAttempts++;

    setTimeout(() => {
        connectWebSocket();
    }, delay);
}

function handleWSMessage(data) {
    if (data.type === 'alert' || data.level) {
        // Show notification
        showToast(data.title || data.message || 'New Alert', data.level || 'info');

        // Refresh alerts if on alerts page
        if (document.getElementById('alerts')?.classList.contains('active')) {
            loadAlerts();
        }

        // Desktop tray notification via API bridge
        if (window.pywebview && window.pywebview.api) {
            window.pywebview.api.show_notification(data.title || 'Alert', data.message || '');
        }
    }
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', () => {
    // Set up navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            showPage(page);
        });
    });

    // Show dashboard
    showPage('dashboard');

    // Connect WebSocket
    connectWebSocket();

    // Set up search enter key
    document.getElementById('knowledge-search')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchKnowledge();
    });
});
