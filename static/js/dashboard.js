// Dashboard Logic & Visualizations for ResumeAI

let trendChartInstance = null;
let radarChartInstance = null;
let currentAnalysisData = null; // Store active analysis details

document.addEventListener('DOMContentLoaded', () => {
    // Only run if on dashboard page
    if (!document.querySelector('.dashboard-layout')) return;
    
    initDashboardTabs();
    initDragAndDrop();
    initAnalysisSubmit();
    initHistorySearch();
    initPasswordChange();
    
    // Load initial data
    loadDashboardOverview();
    loadAnalysisHistory();
});

// 1. Sidebar Tab Swapping
function initDashboardTabs() {
    const menuItems = document.querySelectorAll('.sidebar-menu .menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            switchToTab(tabName);
        });
    });
}

function switchToTab(tabName) {
    // Update active menu link
    document.querySelectorAll('.sidebar-menu .menu-item').forEach(link => {
        if (link.getAttribute('data-tab') === tabName) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Hide all views, display selected
    document.querySelectorAll('.dashboard-view').forEach(view => {
        view.classList.remove('active');
    });
    
    const activeView = document.getElementById(`view-${tabName}`);
    if (activeView) {
        activeView.classList.add('active');
    }
    
    // URL Hash matching (silent)
    window.history.pushState(null, null, `#${tabName}`);
    
    // Specific tab loading events
    if (tabName === 'overview') {
        loadDashboardOverview();
    } else if (tabName === 'history') {
        loadAnalysisHistory();
    } else if (tabName === 'profile') {
        loadUserProfile();
    }
}

// 2. Drag & Drop File Upload handler
function initDragAndDrop() {
    const dropArea = document.getElementById('drag-drop-area');
    const fileInput = document.getElementById('resume-file');
    const fileDetails = document.getElementById('selected-file-details');
    const displayFileName = document.getElementById('display-file-name');
    const displayFileSize = document.getElementById('display-file-size');
    const removeFileBtn = document.getElementById('remove-file-btn');
    
    if (!dropArea || !fileInput) return;
    
    // Trigger file selection on click
    dropArea.addEventListener('click', (e) => {
        // Prevent trigger if clicking remove file btn
        if (e.target.closest('#remove-file-btn')) return;
        fileInput.click();
    });
    
    fileInput.addEventListener('change', () => {
        handleFileSelection(fileInput.files[0]);
    });
    
    // Drag events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropArea.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropArea.classList.remove('drag-over');
        }, false);
    });
    
    dropArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelection(files[0]);
        }
    });
    
    function handleFileSelection(file) {
        if (!file) return;
        
        // Validation
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'pdf' && ext !== 'docx') {
            showToast('Invalid file type. Please upload PDF or DOCX.', 'error');
            fileInput.value = '';
            return;
        }
        
        // Hide default texts, show selected file detail panel
        const textElements = dropArea.querySelectorAll('.upload-box-icon, .drag-drop-text');
        textElements.forEach(el => el.style.display = 'none');
        
        displayFileName.textContent = file.name;
        displayFileSize.textContent = formatBytes(file.size);
        fileDetails.style.display = 'flex';
    }
    
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        fileDetails.style.display = 'none';
        
        const textElements = dropArea.querySelectorAll('.upload-box-icon, .drag-drop-text');
        textElements.forEach(el => el.style.display = 'block');
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 3. Analysis Submit Logic (REST API + simulated progress delay)
function initAnalysisSubmit() {
    const form = document.getElementById('analysis-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('resume-file');
        const jobTitle = document.getElementById('job-title').value;
        const jobDesc = document.getElementById('job-description').value;
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showToast('Please select a resume file.', 'error');
            return;
        }
        
        const file = fileInput.files[0];
        
        // Prepare multipart form data
        const formData = new FormData();
        formData.append('resume', file);
        formData.append('job_title', jobTitle);
        formData.append('job_description', jobDesc);
        
        // Show progress bar
        const progressBarContainer = document.getElementById('upload-progress-container');
        const progressBarFill = document.getElementById('progress-fill');
        const progressPercent = document.getElementById('progress-percent');
        const submitBtn = document.getElementById('analyze-submit-btn');
        const skeletonOverlay = document.getElementById('analysis-loading-skeleton');
        
        progressBarContainer.style.display = 'block';
        submitBtn.disabled = true;
        
        // Simulate uploading state progress
        let percent = 0;
        const interval = setInterval(() => {
            percent += 15;
            if (percent >= 90) {
                clearInterval(interval);
                percent = 90;
            }
            progressBarFill.style.width = `${percent}%`;
            progressPercent.textContent = `${percent}%`;
        }, 300);
        
        try {
            // Trigger skeleton loading overlay at 90%
            setTimeout(() => {
                if (percent === 90) {
                    skeletonOverlay.style.display = 'flex';
                }
            }, 1800);
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
            
            clearInterval(interval);
            progressBarFill.style.width = '100%';
            progressPercent.textContent = '100%';
            
            const result = await response.json();
            
            // Short delay to let progress bar finish animation
            setTimeout(() => {
                progressBarContainer.style.display = 'none';
                progressBarFill.style.width = '0%';
                progressPercent.textContent = '0%';
                submitBtn.disabled = false;
                skeletonOverlay.style.display = 'none';
                
                if (result.success) {
                    showToast('Analysis completed successfully!', 'success');
                    displayAnalysisResults(result.analysis);
                } else {
                    showToast(result.message || 'Analysis failed.', 'error');
                }
            }, 600);
            
        } catch (err) {
            clearInterval(interval);
            progressBarContainer.style.display = 'none';
            submitBtn.disabled = false;
            skeletonOverlay.style.display = 'none';
            showToast('Server connection failed. Try again.', 'error');
            console.error(err);
        }
    });
}

// 4. Render Parsed Reports & Suggestion lists
function displayAnalysisResults(analysis) {
    currentAnalysisData = analysis;
    const results = analysis.analysis_results;
    const extracted = analysis.extracted_data;
    
    // Switch active panel tab
    switchToTab('result');
    
    // Set score indicator circle
    const gaugeFill = document.getElementById('result-gauge-fill');
    const scoreVal = document.getElementById('result-ats-score');
    
    // SVG circular gauge calculation: radius=50 -> perimeter = 2 * PI * r = 314
    const offset = 314 - (314 * analysis.ats_score) / 100;
    gaugeFill.style.strokeDashoffset = offset;
    scoreVal.textContent = `${analysis.ats_score}%`;
    
    // Set subscores meters progress bars
    setMeterValue('meter-match', analysis.resume_match_score);
    setMeterValue('meter-skills', analysis.skills_score);
    setMeterValue('meter-keywords', analysis.keywords_score);
    setMeterValue('meter-exp', analysis.experience_score);
    setMeterValue('meter-edu', analysis.education_score);
    setMeterValue('meter-fmt', analysis.formatting_score);
    
    // Set Parsed details Overview table
    document.getElementById('res-name').textContent = extracted.name || 'Not Found';
    document.getElementById('res-email').textContent = extracted.email || 'Not Found';
    document.getElementById('res-phone').textContent = extracted.phone || 'Not Found';
    document.getElementById('res-years').textContent = `${results.experience_details.candidate_years} Years`;
    document.getElementById('res-education').textContent = extracted.education.join(', ') || 'Not Found';
    document.getElementById('res-github').textContent = extracted.github || 'Not Found';
    document.getElementById('res-skills-count').textContent = `${extracted.skills.length} skills recognized`;
    
    // Populate Skills matching lists
    populateBadgeList('list-matched-skills', results.matched_skills, 'skill-matched');
    populateBadgeList('list-missing-skills', results.missing_skills, 'skill-missing');
    populateBadgeList('list-recommended-skills', results.recommended_skills, 'skill-recommended');
    
    // Populate Keyword & alignments summaries
    document.getElementById('audit-top-kw').textContent = `${results.matched_keywords.length} / ${results.top_keywords.length} matched`;
    document.getElementById('audit-repeated-kw').textContent = results.repeated_keywords.length > 0 ? 
        results.repeated_keywords.map(k => `${k.keyword} (${k.count}x)`).join(', ') : 'None';
        
    document.getElementById('audit-req-exp').textContent = `${results.experience_details.required_years} Years`;
    const expBadge = document.getElementById('audit-exp-status');
    expBadge.textContent = results.experience_details.match_status;
    expBadge.className = 'status-badge ' + (analysis.experience_score >= 80 ? 'score-high' : 'score-medium');
    
    document.getElementById('audit-req-edu').textContent = results.education_details.required_degree;
    const eduBadge = document.getElementById('audit-edu-status');
    eduBadge.textContent = results.education_details.match_status;
    eduBadge.className = 'status-badge ' + (analysis.education_score >= 90 ? 'score-high' : 'score-low');
    
    // Formatting Checklist setup
    const checklist = document.getElementById('formatting-checklist');
    checklist.innerHTML = '';
    
    const checks = [
        { label: 'Email Address included', passed: results.formatting_details.has_email },
        { label: 'Phone Number included', passed: results.formatting_details.has_phone },
        { label: 'LinkedIn or GitHub profile links', passed: results.formatting_details.has_links },
        { label: 'Appropriate document word count', passed: results.formatting_details.word_count >= 200 && results.formatting_details.word_count <= 1500 },
        { label: 'Identified Work Experience header', passed: results.formatting_details.headings_found.includes('experience') || results.formatting_details.headings_found.includes('work') },
        { label: 'Identified Education header', passed: results.formatting_details.headings_found.includes('education') },
        { label: 'Identified Skills header', passed: results.formatting_details.headings_found.includes('skills') }
    ];
    
    checks.forEach(c => {
        const div = document.createElement('div');
        div.className = `format-check-item ${c.passed ? 'passed' : 'failed'}`;
        div.innerHTML = `
            <i class="fa-solid ${c.passed ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
            <span>${c.label}</span>
        `;
        checklist.appendChild(div);
    });
    
    // Suggestions cards lists
    const sugContainer = document.getElementById('suggestions-container');
    sugContainer.innerHTML = '';
    
    results.suggestions.forEach(s => {
        const card = document.createElement('div');
        card.className = `suggestion-bullet-card ${s.category}-cat`;
        card.innerHTML = `
            <h4>${s.title}</h4>
            <p>${s.description}</p>
        `;
        sugContainer.appendChild(card);
    });
    
    // Bind action export links
    document.getElementById('btn-print-report').href = `/api/history/${analysis.id}/report`;
    
    document.getElementById('btn-export-json').onclick = () => {
        const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resume_analysis_${analysis.id}.json`;
        a.click();
        showToast('JSON Analysis exported!', 'success');
    };
}

function setMeterValue(elementId, value) {
    const valText = document.getElementById(`${elementId}-val`);
    const fill = document.getElementById(`${elementId}-fill`);
    if (valText && fill) {
        valText.textContent = `${value}%`;
        fill.style.width = `${value}%`;
        
        // Dynamic coloring
        if (value >= 80) fill.style.background = 'var(--success)';
        else if (value >= 50) fill.style.background = 'var(--warning)';
        else fill.style.background = 'var(--error)';
    }
}

function populateBadgeList(elementId, items, className) {
    const ul = document.getElementById(elementId);
    if (!ul) return;
    ul.innerHTML = '';
    items.forEach(item => {
        const li = document.createElement('li');
        li.className = className;
        li.textContent = item;
        ul.appendChild(li);
    });
    if (items.length === 0) {
        const li = document.createElement('li');
        li.className = 'text-muted';
        li.style.border = 'none';
        li.style.background = 'none';
        li.textContent = elementId.includes('missing') ? 'No missing skills!' : 'None';
        ul.appendChild(li);
    }
}

// 5. Load and Populate Dashboard Overview cards & ChartJS instances
async function loadDashboardOverview() {
    try {
        const res = await fetch('/api/auth/profile');
        const profileData = await res.json();
        
        if (profileData.success) {
            const prof = profileData.profile;
            document.getElementById('stat-avg-score').textContent = prof.average_score > 0 ? `${prof.average_score}%` : '--';
            document.getElementById('stat-resume-count').textContent = prof.resume_count;
            document.getElementById('stat-analysis-count').textContent = prof.analysis_count;
        }
        
        // Fetch history logs to compile trends
        const historyRes = await fetch('/api/history');
        const histData = await historyRes.json();
        
        if (histData.success) {
            const list = histData.history;
            
            // Set average match %
            if (list.length > 0) {
                const totalMatch = list.reduce((sum, item) => sum + item.resume_match_score, 0);
                document.getElementById('stat-avg-match').textContent = `${Math.round(totalMatch / list.length)}%`;
            } else {
                document.getElementById('stat-avg-match').textContent = '--';
            }
            
            // Compile charts datasets
            initOverviewCharts(list);
        }
    } catch (err) {
        console.error("Failed to load dashboard overview stats:", err);
    }
}

function initOverviewCharts(historyList) {
    // 1. Line Chart: Scores Trends (Newest is last in index)
    const trendsCtx = document.getElementById('atsTrendsChart');
    if (!trendsCtx) return;
    
    // Sort chronological: oldest first
    const sortedChron = [...historyList].reverse();
    
    // Extract last 7 records
    const subset = sortedChron.slice(-7);
    const dates = subset.map(item => {
        const d = new Date(item.created_at);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const scores = subset.map(item => item.ats_score);
    const matches = subset.map(item => item.resume_match_score);
    
    if (trendChartInstance) {
        trendChartInstance.destroy();
    }
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
    const textColor = isDark ? '#E2E8F0' : '#475569';
    
    trendChartInstance = new Chart(trendsCtx, {
        type: 'line',
        data: {
            labels: dates.length > 0 ? dates : ['No Scans Yet'],
            datasets: [
                {
                    label: 'ATS Score',
                    data: scores.length > 0 ? scores : [0],
                    borderColor: '#2563EB',
                    backgroundColor: 'rgba(37, 99, 235, 0.05)',
                    tension: 0.3,
                    fill: true,
                    borderWidth: 3
                },
                {
                    label: 'Match %',
                    data: matches.length > 0 ? matches : [0],
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.05)',
                    tension: 0.3,
                    fill: true,
                    borderWidth: 2,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: textColor }
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });
    
    // 2. Radar Chart: Subscores distribution for the latest scan (or average if none)
    const radarCtx = document.getElementById('subScoresRadarChart');
    if (!radarCtx) return;
    
    let radarData = [0, 0, 0, 0, 0, 0];
    if (historyList.length > 0) {
        const latest = historyList[0]; // history list is sorted newest first
        radarData = [
            latest.skills_score,
            latest.keywords_score,
            latest.experience_score,
            latest.education_score,
            latest.formatting_score,
            latest.resume_match_score
        ];
    }
    
    if (radarChartInstance) {
        radarChartInstance.destroy();
    }
    
    radarChartInstance = new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: ['Skills', 'Keywords', 'Experience', 'Education', 'Formatting', 'Content Match'],
            datasets: [{
                label: 'Score Breakdown',
                data: radarData,
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderColor: '#8B5CF6',
                borderWidth: 2,
                pointBackgroundColor: '#8B5CF6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: textColor }
                }
            },
            scales: {
                r: {
                    grid: { color: gridColor },
                    angleLines: { color: gridColor },
                    pointLabels: { color: textColor, font: { size: 10, weight: 'bold' } },
                    ticks: { display: false },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// 6. Manage History Logs (Table reload, Search Filter, Delete logs API calls)
async function loadAnalysisHistory(searchFilter = '') {
    const tableBody = document.getElementById('history-table-body');
    if (!tableBody) return;
    
    try {
        let url = '/api/history';
        if (searchFilter) {
            url += `?search=${encodeURIComponent(searchFilter)}`;
        }
        
        const res = await fetch(url);
        const data = await res.json();
        
        if (data.success) {
            const list = data.history;
            tableBody.innerHTML = '';
            
            if (list.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="table-empty-state">
                            <i class="fa-solid fa-folder-open" style="font-size: 24px; color: var(--text-muted); margin-bottom: 8px;"></i>
                            <p>${searchFilter ? 'No matching history logs found.' : 'No analyses scanned yet. Begin by matching a resume!'}</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            list.forEach(item => {
                const tr = document.createElement('tr');
                
                // Score badge color
                let scoreClass = 'score-low';
                if (item.ats_score >= 80) scoreClass = 'score-high';
                else if (item.ats_score >= 50) scoreClass = 'score-medium';
                
                const date = new Date(item.created_at);
                const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                
                tr.innerHTML = `
                    <td class="text-bold" style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${item.resume_name}
                    </td>
                    <td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${item.job_title}
                    </td>
                    <td>${formattedDate}</td>
                    <td><span class="score-badge ${scoreClass}">${item.ats_score}%</span></td>
                    <td>${item.resume_match_score}%</td>
                    <td>
                        <div class="table-actions">
                            <button class="btn-icon view-row-btn" data-id="${item.id}" title="View Analysis Details">
                                <i class="fa-solid fa-chart-line"></i>
                            </button>
                            <a href="/api/history/${item.id}/report" target="_blank" class="btn-icon" title="Print/Export Report Page">
                                <i class="fa-solid fa-print"></i>
                            </a>
                            <button class="btn-icon delete-btn" data-id="${item.id}" title="Delete Record">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
            
            // Bind view events
            tableBody.querySelectorAll('.view-row-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = parseInt(btn.getAttribute('data-id'));
                    const selected = list.find(item => item.id === id);
                    if (selected) {
                        displayAnalysisResults(selected);
                    }
                });
            });
            
            // Bind delete events
            tableBody.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    if (confirm('Are you sure you want to permanently delete this resume analysis record?')) {
                        try {
                            const delRes = await fetch(`/api/history/${id}`, { method: 'DELETE' });
                            const delResult = await delRes.json();
                            
                            if (delResult.success) {
                                showToast('Record deleted successfully!', 'success');
                                loadAnalysisHistory(searchFilter);
                            } else {
                                showToast(delResult.message || 'Failed to delete.', 'error');
                            }
                        } catch (err) {
                            showToast('Failed to connect to server.', 'error');
                        }
                    }
                });
            });
        }
    } catch (err) {
        console.error("Failed to load history list:", err);
    }
}

// History Search debounce
function initHistorySearch() {
    const input = document.getElementById('history-search-input');
    if (!input) return;
    
    let timeout = null;
    input.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            loadAnalysisHistory(input.value.trim());
        }, 400);
    });
}

// 7. Profile settings loaders
async function loadUserProfile() {
    try {
        const res = await fetch('/api/auth/profile');
        const data = await res.json();
        
        if (data.success) {
            const p = data.profile;
            document.getElementById('profile-name-display').textContent = p.full_name;
            document.getElementById('profile-email-display').textContent = p.email;
            document.getElementById('profile-joined-display').textContent = `Joined ${p.created_at}`;
            document.getElementById('profile-count-resumes').textContent = p.resume_count;
            document.getElementById('profile-avg-score-display').textContent = p.average_score > 0 ? `${p.average_score}%` : '--';
        }
    } catch (err) {
        console.error("Failed to load user profile:", err);
    }
}

function initPasswordChange() {
    const form = document.getElementById('password-reset-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const current_password = document.getElementById('current_password').value;
        const new_password = document.getElementById('new_password').value;
        const confirm_new_password = document.getElementById('confirm_new_password').value;
        
        if (new_password !== confirm_new_password) {
            showToast('New passwords do not match.', 'error');
            return;
        }
        
        try {
            const res = await fetch('/api/auth/profile/password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_password,
                    new_password,
                    confirm_new_password
                })
            });
            const result = await res.json();
            
            if (result.success) {
                showToast('Password updated successfully!', 'success');
                form.reset();
            } else {
                showToast(result.message || 'Failed to change password.', 'error');
            }
        } catch (err) {
            showToast('Connection error. Try again.', 'error');
        }
    });
}
