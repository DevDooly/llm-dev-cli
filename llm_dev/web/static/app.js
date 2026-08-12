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
        item.className = 'task-item clickable';
        item.onclick = () => openDocModal(f.file);
        item.innerHTML = `
            <div class="task-top">
                <span class="task-file">📄 ${f.file}</span>
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

async function openDocModal(fileName) {
    const modal = document.getElementById('docModal');
    const titleEl = document.getElementById('modalDocTitle');
    const pathEl = document.getElementById('modalDocPath');
    const bodyEl = document.getElementById('modalDocBody');

    titleEl.textContent = fileName;
    pathEl.textContent = '문서 로딩 중...';
    bodyEl.innerHTML = '<div class="loading-spinner">문서를 불러오는 중...</div>';
    modal.classList.add('active');

    try {
        const res = await fetch(`/api/doc?name=${encodeURIComponent(fileName)}`);
        if (!res.ok) throw new Error('문서를 불러올 수 없습니다.');
        const docData = await res.json();

        pathEl.textContent = docData.path || fileName;
        if (window.marked) {
            bodyEl.innerHTML = marked.parse(docData.content);
        } else {
            bodyEl.textContent = docData.content;
        }
    } catch (e) {
        bodyEl.innerHTML = `<div class="diag-sugg" style="color:#f87171;">⚠️ ${e.message}</div>`;
    }
}

function closeDocModal(event) {
    if (event && event.target !== document.getElementById('docModal') && !event.target.classList.contains('btn-close')) {
        return;
    }
    const modal = document.getElementById('docModal');
    modal.classList.remove('active');
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('docModal');
        if (modal) modal.classList.remove('active');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
});

