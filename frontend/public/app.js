// API基础URL
const API_BASE = 'http://localhost:8000';

// 全局状态
const state = {
    loading: false,
    error: null,
    lastPrediction: null
};

// 显示加载状态
function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = '<div class="loading-indicator"><span class="loading"></span> 加载中...</div>';
    }
}

// 隐藏加载状态
function hideLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        const loadingEl = el.querySelector('.loading-indicator');
        if (loadingEl) loadingEl.remove();
    }
}

// 显示错误信息
function showError(message, elementId = null) {
    state.error = message;
    if (elementId) {
        const el = document.getElementById(elementId);
        if (el) {
            el.innerHTML = `<div class="error-message">❌ ${message}</div>`;
        }
    } else {
        showNotification({ level: 'danger', title: '错误', message });
    }
}

// 页面切换
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const target = this.getAttribute('href').substring(1);

        // 更新导航状态
        document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
        this.classList.add('active');

        // 切换内容
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(target).classList.add('active');

        // 加载数据
        if (target === 'cases') loadCases();
    });
});

// 风险预测
async function predictRisk() {
    const productName = document.getElementById('productName').value;
    const productDesc = document.getElementById('productDesc').value;
    const marketingContent = document.getElementById('marketingContent').value.split('\n').filter(x => x.trim());
    const companySize = document.getElementById('companySize').value;
    const annualRevenue = document.getElementById('annualRevenue').value * 10000;

    if (!productName && !productDesc && marketingContent.length === 0) {
        alert('请至少填写一项内容');
        return;
    }

    const platformData = {
        product_info: {
            name: productName,
            description: productDesc
        },
        marketing_content: marketingContent.map(text => ({ text })),
        company_size: companySize,
        annual_revenue: annualRevenue
    };

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform_data: platformData })
        });

        const result = await response.json();
        displayPredictResult(result);
    } catch (error) {
        console.error('预测失败:', error);
        alert('预测请求失败，请确保API服务已启动');
    }
}

// 显示预测结果
function displayPredictResult(result) {
    document.getElementById('predictResult').style.display = 'block';

    // 综合评分
    const score = Math.round(result.overall_risk_score * 100);
    document.getElementById('overallScore').textContent = score;

    // 风险列表
    const riskList = document.getElementById('riskList');
    riskList.innerHTML = result.risk_assessments.map(risk => {
        const levelClass = risk.risk_level === '高' ? 'high' : (risk.risk_level === '中' ? 'medium' : 'low');
        const probability = Math.round(risk.probability * 100);

        return `
            <div class="risk-item ${levelClass}">
                <div class="risk-type">${risk.risk_type}</div>
                <div class="risk-probability">${probability}%</div>
                <span class="risk-level ${levelClass}">${risk.risk_level}风险</span>
            </div>
        `;
    }).join('');

    // 建议
    document.getElementById('recommendation').innerHTML = `
        <strong>💡 建议：</strong> ${result.recommendation}
    `;
}

// 搜索法律
async function searchLaws() {
    const query = document.getElementById('lawSearch').value;
    if (!query) return;

    try {
        const response = await fetch(`${API_BASE}/knowledge_graph/search?query=${encodeURIComponent(query)}`);
        const result = await response.json();
        displayLawResults(result.results);
    } catch (error) {
        console.error('搜索失败:', error);
    }
}

// 显示法律结果
function displayLawResults(results) {
    const container = document.getElementById('lawResults');

    if (results.length === 0) {
        container.innerHTML = '<p>未找到相关法律条文</p>';
        return;
    }

    container.innerHTML = results.map(item => `
        <div class="law-item">
            <div class="law-name">${item.full_name || item.law_name}</div>
            <div class="law-article">${item.article_id}</div>
            <div class="law-content">${item.content || item.data?.content || ''}</div>
        </div>
    `).join('');
}

// 加载案例
async function loadCases() {
    try {
        const response = await fetch(`${API_BASE}/knowledge_graph/cases`);
        const result = await response.json();
        displayCases(result.cases);
    } catch (error) {
        console.error('加载案例失败:', error);
    }
}

// 显示案例
function displayCases(cases) {
    const container = document.getElementById('caseList');

    container.innerHTML = cases.map(c => `
        <div class="case-item">
            <div class="case-header">
                <span class="case-title">${c.title}</span>
                <span class="case-fine">罚款 ${c.fine_amount?.toLocaleString() || 0} 元</span>
            </div>
            <div class="case-meta">
                <span>🏷️ ${c.risk_type}</span>
                <span>🏢 ${c.company_size || '未知'}</span>
                <span>📅 ${c.decision_date || '未知'}</span>
            </div>
            <div class="case-summary">${c.summary || ''}</div>
        </div>
    `).join('');
}

// 筛选案例
async function filterCases() {
    const riskType = document.getElementById('riskTypeFilter').value;

    try {
        let url = `${API_BASE}/knowledge_graph/cases`;
        const response = await fetch(url);
        const result = await response.json();

        let cases = result.cases;
        if (riskType) {
            cases = cases.filter(c => c.risk_type === riskType);
        }

        displayCases(cases);
    } catch (error) {
        console.error('筛选失败:', error);
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('电商合规哨兵已加载');
    loadAlertStats();
    loadAlertRules();
});

// ==================== WebSocket实时预警 ====================

let ws = null;

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('WebSocket已连接');
        return;
    }

    ws = new WebSocket('ws://localhost:8000/ws/alerts');

    ws.onopen = () => {
        console.log('WebSocket已连接');
        updateWsStatus('online');
        ws.send(JSON.stringify({ action: 'subscribe', topic: 'alerts' }));
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('收到消息:', data);

        if (data.type === 'new_alert') {
            showNotification(data.alert);
            loadAlertStats();
        }
    };

    ws.onclose = () => {
        console.log('WebSocket已断开');
        updateWsStatus('offline');
    };

    ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        updateWsStatus('error');
    };
}

function updateWsStatus(status) {
    const badge = document.getElementById('wsStatus');
    badge.className = `status-badge ${status}`;
    badge.textContent = status === 'online' ? '已连接' : (status === 'error' ? '错误' : '未连接');
}

function showNotification(alert) {
    // 创建通知
    const container = document.createElement('div');
    container.className = `notification ${alert.level}`;
    container.innerHTML = `
        <strong>${alert.title}</strong>
        <p>${alert.message}</p>
    `;
    document.body.appendChild(container);

    // 3秒后移除
    setTimeout(() => container.remove(), 5000);
}

// ==================== 预警管理 ====================

let alertPage = 1;
const alertPageSize = 10;
let allAlerts = [];

async function loadAlertStats() {
    try {
        const response = await fetch(`${API_BASE}/alerts/stats`);
        const stats = await response.json();

        document.getElementById('alertTotal').textContent = stats.total || 0;
        document.getElementById('alertActive').textContent = stats.active || 0;
        document.getElementById('alertWarning').textContent = stats.by_level?.warning || 0;
        document.getElementById('alertDanger').textContent = stats.by_level?.danger || 0;
    } catch (error) {
        console.error('加载预警统计失败:', error);
    }
}

async function loadAlertList() {
    try {
        const response = await fetch(`${API_BASE}/alerts?limit=100`);
        const data = await response.json();
        allAlerts = data.alerts || [];
        renderAlertList();
    } catch (error) {
        console.error('加载预警列表失败:', error);
        document.getElementById('alertList').innerHTML = '<p class="error-message">加载失败</p>';
    }
}

function renderAlertList() {
    const container = document.getElementById('alertList');
    const filter = document.getElementById('alertFilter')?.value || 'all';

    // 筛选
    let filtered = allAlerts;
    if (filter !== 'all') {
        filtered = allAlerts.filter(a => a.level === filter || a.status === filter);
    }

    // 分页
    const start = (alertPage - 1) * alertPageSize;
    const pageAlerts = filtered.slice(start, start + alertPageSize);

    if (pageAlerts.length === 0) {
        container.innerHTML = '<p class="empty-message">暂无预警</p>';
        return;
    }

    container.innerHTML = pageAlerts.map(alert => `
        <div class="alert-item ${alert.level}" data-id="${alert.alert_id}">
            <div class="alert-title">${alert.title || '风险预警'}</div>
            <div class="alert-message">${alert.message || ''}</div>
            <div class="alert-meta">
                <span>级别: ${alert.level}</span>
                <span>状态: ${alert.status}</span>
                <span>时间: ${new Date(alert.created_at).toLocaleString()}</span>
            </div>
            <div class="alert-actions">
                <button class="btn-secondary" onclick="acknowledgeAlert('${alert.alert_id}')">确认</button>
                <button class="btn-secondary" onclick="resolveAlert('${alert.alert_id}')">解决</button>
            </div>
        </div>
    `).join('');

    // 分页控件
    const totalPages = Math.ceil(filtered.length / alertPageSize);
    if (totalPages > 1) {
        container.innerHTML += `
            <div class="pagination">
                <button onclick="changeAlertPage(${alertPage - 1})" ${alertPage <= 1 ? 'disabled' : ''}>上一页</button>
                <span>第 ${alertPage} / ${totalPages} 页</span>
                <button onclick="changeAlertPage(${alertPage + 1})" ${alertPage >= totalPages ? 'disabled' : ''}>下一页</button>
            </div>
        `;
    }
}

function changeAlertPage(page) {
    alertPage = Math.max(1, page);
    renderAlertList();
}

function filterAlerts() {
    alertPage = 1;
    renderAlertList();
}

async function loadAlertRules() {
    try {
        const response = await fetch(`${API_BASE}/alerts/rules`);
        const data = await response.json();

        const container = document.getElementById('alertRules');
        container.innerHTML = data.rules.map(rule => `
            <div class="rule-item">
                <div class="rule-name">${rule.name}</div>
                <div class="rule-desc">${rule.description}</div>
                <div class="rule-meta">
                    <span class="tag ${rule.level}">${rule.level}</span>
                    <span>阈值: ${(rule.probability_threshold * 100).toFixed(0)}%</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载预警规则失败:', error);
    }
}

async function acknowledgeAlert(alertId) {
    try {
        await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, { method: 'POST' });
        loadAlertStats();
    } catch (error) {
        console.error('确认预警失败:', error);
    }
}

async function resolveAlert(alertId) {
    try {
        await fetch(`${API_BASE}/alerts/${alertId}/resolve`, { method: 'POST' });
        loadAlertStats();
    } catch (error) {
        console.error('解决预警失败:', error);
    }
}

// ==================== 主动监控 ====================

async function startMonitor() {
    try {
        const response = await fetch(`${API_BASE}/monitor/start`, { method: 'POST' });
        const data = await response.json();
        alert(data.message);
        getMonitorStatus();
    } catch (error) {
        console.error('启动监控失败:', error);
    }
}

async function stopMonitor() {
    try {
        const response = await fetch(`${API_BASE}/monitor/stop`, { method: 'POST' });
        const data = await response.json();
        alert(data.message);
        getMonitorStatus();
    } catch (error) {
        console.error('停止监控失败:', error);
    }
}

async function getMonitorStatus() {
    try {
        const response = await fetch(`${API_BASE}/monitor/status`);
        const status = await response.json();

        const container = document.getElementById('monitorStatus');
        container.innerHTML = `
            <div class="status-info">
                <p>状态: <span class="${status.running ? 'text-success' : 'text-danger'}">${status.running ? '运行中' : '已停止'}</span></p>
                <p>检查间隔: ${status.check_interval}秒</p>
                <p>监控项数量: ${status.monitored_items}</p>
            </div>
        `;
    } catch (error) {
        console.error('获取监控状态失败:', error);
    }
}

// ==================== 实时预测 ====================

async function predictRealtime() {
    const productName = document.getElementById('productName').value;
    const productDesc = document.getElementById('productDesc').value;
    const marketingContent = document.getElementById('marketingContent').value.split('\n').filter(x => x.trim());

    const platformData = {
        product_info: { name: productName, description: productDesc },
        marketing_content: marketingContent.map(text => ({ text }))
    };

    try {
        const response = await fetch(`${API_BASE}/predict/realtime`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform_data: platformData })
        });

        const result = await response.json();
        displayPredictResult(result.prediction);

        if (result.alerts_triggered > 0) {
            showNotification({
                level: 'warning',
                title: '触发预警',
                message: `检测到 ${result.alerts_triggered} 个风险预警`
            });
            loadAlertStats();
        }
    } catch (error) {
        console.error('实时预测失败:', error);
    }
}
