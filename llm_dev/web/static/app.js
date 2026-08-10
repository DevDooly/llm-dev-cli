async function loadAllData() {
    try {
        const [diagRes, taskRes] = await Promise.all([
            fetch('/api/diagnostics').then(r => r.json()),
            fetch('/api/tasks').then(r => r.json())
        ]);

        renderDiagnostics(diagRes);
        renderTasks(taskRes);
    } catch (e) {
        console.error("Failed to load dashboard data:", e);
    }
}

function renderDiagnostics(data) {
    const scoreEl = document.getElementById('complianceScore');
    const detailEl = document.getElementById('complianceDetail');
    const badgeEl = document.getElementById('complianceBadge');
    const listEl = document.getElementById('diagnosticsList');
    const countEl = document.getElementById('diagnosticCount');

    scoreEl.textContent = `${data.score}%`;
    detailEl.textContent = `${data.passed}/${data.total} 항목 통과`;
    countEl.textContent = `${data.results.length} checks`;

    badgeEl.className = 'metric-badge ' + (data.score >= 80 ? 'badge-green' : (data.score >= 60 ? 'badge-yellow' : 'badge-red'));
    badgeEl.textContent = data.score >= 80 ? 'GOOD' : 'WARNING';

    listEl.innerHTML = '';
    data.results.forEach(res => {
        const item = document.createElement('div');
        item.className = 'diagnostic-item';
        
        let statusBadge = res.passed 
            ? `<span class="metric-badge badge-green">PASS</span>`
            : (res.severity === 'ERROR' ? `<span class="metric-badge badge-red">ERROR</span>` : `<span class="metric-badge badge-yellow">WARN</span>`);

        item.innerHTML = `
            <div class="diag-top">
                <span class="diag-name">${res.name}</span>
                ${statusBadge}
            </div>
            <div class="diag-msg">${res.message}</div>
            ${res.suggestion ? `<div class="diag-sugg">💡 조치: ${res.suggestion}</div>` : ''}
        `;
        listEl.appendChild(item);
    });
}

function renderTasks(data) {
    const overallEl = document.getElementById('overallProgress');
    const taskDetailEl = document.getElementById('taskDetail');
    const listEl = document.getElementById('tasksList');
    const countEl = document.getElementById('documentCount');

    overallEl.textContent = `${data.grand_percent}%`;
    taskDetailEl.textContent = `${data.total_checked}/${data.grand_total} 작업 완료`;
    countEl.textContent = `${data.files.length} files`;

    listEl.innerHTML = '';
    if (!data.files || data.files.length === 0) {
        listEl.innerHTML = '<div class="loading-spinner">체크리스트 문서를 찾을 수 없습니다.</div>';
        return;
    }

    data.files.forEach(f => {
        const item = document.createElement('div');
        item.className = 'task-item';
        item.innerHTML = `
            <div class="task-top">
                <span class="task-file">${f.file}</span>
                <span style="font-size:0.85rem; font-weight:700; color:${f.percent === 100 ? '#34d399' : '#9ca3af'};">
                    ${f.checked}/${f.total} (${f.percent}%)
                </span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: ${f.percent}%"></div>
            </div>
        `;
        listEl.appendChild(item);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
});
