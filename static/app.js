// AI Interview Agent - Frontend Application Logic with Live Execution Tracing & Server Sync

let currentCandidate = null;
let currentSessionId = null;
let questionCount = 0;
let isWaitingForResponse = false;
let debugLogCount = 0;
let nonsenseWarnings = 0;
let lastFeedbackData = null;
const MAX_NONSENSE_WARNINGS = 2;

// ─── Client-Side Gibberish / Nonsense Detector ───────────────────────
const COMMON_WORDS = new Set([
    'the','be','to','of','and','a','in','that','have','i','it','for','not','on','with',
    'he','as','you','do','at','this','but','his','by','from','they','we','her','she',
    'or','an','will','my','one','all','would','there','their','what','so','up','out',
    'if','about','who','get','which','go','me','when','make','can','like','time','no',
    'just','him','know','take','people','into','year','your','good','some','could',
    'them','see','other','than','then','now','look','only','come','its','over','think',
    'also','back','after','use','two','how','our','work','first','well','way','even',
    'new','want','because','any','these','give','day','most','us','is','are','was',
    'were','been','has','had','did','does','am','may','should','must','shall','need',
    'yes','no','ok','okay','sure','right','yeah','true','false','maybe','perhaps',
    'vector','embedding','database','model','training','data','api','server','deploy',
    'agent','prompt','rag','retrieval','query','index','token','llm','fine','tune',
    'function','code','python','docker','kubernetes','security','memory','context',
    'chatbot','pipeline','inference','weight','layer','neural','network','transformer',
    'attention','gradient','loss','accuracy','precision','recall','cluster','node',
    'architecture','scalable','production','monitoring','logging','testing','debug',
    'langchain','openai','gemini','ollama','chromadb','pinecone','weaviate','mcp',
    'orchestration','multi','agentic','tool','calling','structured','output','chain'
]);

function analyzeInputQuality(text) {
    const trimmed = text.trim();
    if (trimmed.length < 8) {
        const shortAcceptable = ['yes', 'no', 'ok', 'okay', 'sure', 'true', 'false', 'maybe'];
        if (!shortAcceptable.includes(trimmed.toLowerCase())) {
            return { isNonsense: true, reason: 'Response is too short to be a meaningful technical answer.' };
        }
    }

    const words = trimmed.toLowerCase().split(/\s+/).filter(w => w.length > 0);
    
    // If it's a substantive multi-word technical explanation (10+ words or 5+ words with recognized terms), it is NOT nonsense
    if (words.length >= 5) {
        const recognizedWords = words.filter(w => COMMON_WORDS.has(w.replace(/[^a-z]/g, '')));
        const recognizedRatio = recognizedWords.length / words.length;
        if (words.length >= 12 || recognizedRatio >= 0.15) {
            return { isNonsense: false, reason: null };
        }
    }

    // Individual word consonant cluster check (6+ consecutive non-vowels, excluding 'y')
    const consonantClusterRegex = /[bcdfghjklmnpqrstvwxz]{6,}/i;
    for (const w of words) {
        const cleanW = w.replace(/[^a-zA-Z]/g, '');
        if (consonantClusterRegex.test(cleanW)) {
            return { isNonsense: true, reason: 'Input appears to contain keyboard mashing or random characters.' };
        }
    }

    const repeatedCharRegex = /(.)(\1{6,})/;
    if (repeatedCharRegex.test(trimmed)) {
        return { isNonsense: true, reason: 'Input contains excessive character repetition.' };
    }

    const singleWord = trimmed.replace(/[^a-zA-Z]/g, '').toLowerCase();
    const lowEffortSingles = ['hi','hello','hey','yo','sup','lol','lmao','bruh',
        'haha','ok','hmm','idk','nah','meh','wat','huh','wow','omg','nice','cool',
        'test','asdf','qwerty','asd','xyz'];
    if (lowEffortSingles.includes(singleWord)) {
        return { isNonsense: true, reason: `"${trimmed}" is not a substantive technical response.` };
    }

    const alphaChars = trimmed.replace(/[^a-zA-Z]/g, '');
    if (alphaChars.length < 3 && trimmed.length > 2) {
        return { isNonsense: true, reason: 'Input contains no meaningful text content.' };
    }

    return { isNonsense: false, reason: null };
}

function showNonsenseWarning(reason) {
    const existing = document.getElementById('nonsenseToast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'nonsenseToast';
    toast.className = 'nonsense-toast';
    toast.innerHTML = `
        <div class="nonsense-icon">🛑</div>
        <div class="nonsense-body">
            <strong>Low-Quality Response Detected</strong>
            <p>${reason}</p>
            <p class="nonsense-hint">Please provide a thoughtful technical answer. (Warning ${nonsenseWarnings}/${MAX_NONSENSE_WARNINGS})</p>
        </div>
    `;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function debugLog(type, message, detail = null) {
    debugLogCount++;
    const formatted = `[${new Date().toISOString().split('T')[1].slice(0, 8)}] [${type.toUpperCase()}] ${message}`;
    console.log(formatted, detail || '');

    const toggleBtn = document.getElementById('debugToggleBtn');
    if (toggleBtn) {
        toggleBtn.textContent = `🐞 Debug Log (${debugLogCount})`;
    }

    const debugContent = document.getElementById('debugContent');
    if (debugContent) {
        const entry = document.createElement('div');
        entry.className = `debug-log-entry ${type}`;
        entry.textContent = `${formatted}${detail ? ' → ' + (typeof detail === 'object' ? JSON.stringify(detail) : detail) : ''}`;
        debugContent.appendChild(entry);
        debugContent.scrollTop = debugContent.scrollHeight;
    }
}

function setupDebugDrawer() {
    const toggleBtn = document.getElementById('debugToggleBtn');
    const closeBtn = document.getElementById('closeDebugBtn');
    const drawer = document.getElementById('debugDrawer');

    if (toggleBtn && drawer) {
        toggleBtn.addEventListener('click', () => {
            drawer.style.display = drawer.style.display === 'none' ? 'flex' : 'none';
        });
    }
    if (closeBtn && drawer) {
        closeBtn.addEventListener('click', () => {
            drawer.style.display = 'none';
        });
    }
}

function setupExportButtons() {
    const copyBtn = document.getElementById('copyFbBtn');
    const downloadBtn = document.getElementById('downloadFbBtn');

    if (copyBtn) {
        copyBtn.addEventListener('click', () => copyFeedbackAsMarkdown());
    }
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => downloadFeedbackAsMarkdown());
    }
}

function initApp() {
    debugLog('info', 'Initializing application...');
    loadCandidates();
    setupEventListeners();
    setupDebugDrawer();
    setupExportButtons();
}

function setupEventListeners() {
    const candidateSelect = document.getElementById('candidateSelect');
    const startBtn = document.getElementById('startInterviewBtn');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');

    candidateSelect.addEventListener('change', (e) => {
        const candidateId = e.target.value;
        debugLog('info', `Candidate dropdown changed: ID='${candidateId}'`);
        if (candidateId && window.candidatesMap) {
            currentCandidate = window.candidatesMap[candidateId];
            renderProfileCard(currentCandidate);
        } else {
            document.getElementById('profileCard').style.display = 'none';
        }
    });

    startBtn.addEventListener('click', () => {
        if (currentCandidate) {
            debugLog('info', `Start button clicked for candidate '${currentCandidate.member?.name}'`);
            startInterview(currentCandidate);
        } else {
            debugLog('error', 'Start button clicked but no candidate selected!');
        }
    });

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (text && !isWaitingForResponse) {
            sendUserMessage(text);
        }
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}

function setupCustomDropdown() {
    const trigger = document.getElementById('dropdownTrigger');
    const menu = document.getElementById('dropdownMenu');
    const searchInput = document.getElementById('dropdownSearchInput');

    if (trigger && menu) {
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = menu.style.display === 'block';
            menu.style.display = isOpen ? 'none' : 'block';
            if (!isOpen && searchInput) {
                searchInput.value = '';
                renderCustomDropdownItems('');
                setTimeout(() => searchInput.focus(), 100);
            }
        });

        document.addEventListener('click', (e) => {
            if (!document.getElementById('customDropdownContainer').contains(e.target)) {
                menu.style.display = 'none';
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            renderCustomDropdownItems(e.target.value);
        });
        searchInput.addEventListener('click', (e) => e.stopPropagation());
    }
}

function renderCustomDropdownItems(filterText = '') {
    const container = document.getElementById('dropdownItems');
    if (!container || !window.candidatesMap) return;

    container.innerHTML = '';
    const query = filterText.toLowerCase().trim();
    let count = 0;

    Object.values(window.candidatesMap).forEach(cand => {
        const member = cand.member || {};
        const name = member.name || 'Candidate';
        const role = member.jobRole || 'Engineer';
        const exp = member.yearsExperience || 0;

        if (query && !name.toLowerCase().includes(query) && !role.toLowerCase().includes(query)) {
            return;
        }

        count++;
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        if (currentCandidate && currentCandidate.member?.id === member.id) {
            item.classList.add('selected');
        }

        const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();

        item.innerHTML = `
            <div class="item-avatar">${initials}</div>
            <div class="item-info">
                <span class="item-name">${name}</span>
                <span class="item-meta">${role} • ${exp} yrs exp</span>
            </div>
            ${currentCandidate && currentCandidate.member?.id === member.id ? '<span class="item-check">✓</span>' : ''}
        `;

        item.addEventListener('click', (e) => {
            e.stopPropagation();
            currentCandidate = cand;
            document.getElementById('selectedCandidateText').textContent = `${name} (${role})`;
            document.getElementById('dropdownMenu').style.display = 'none';
            
            // Sync hidden select element
            const select = document.getElementById('candidateSelect');
            if (select) select.value = member.id;

            debugLog('info', `Selected candidate via custom dropdown: '${name}'`);
            renderProfileCard(currentCandidate);
        });

        container.appendChild(item);
    });

    if (count === 0) {
        container.innerHTML = '<div class="dropdown-empty">No matching candidates found</div>';
    }
}

async function loadCandidates() {
    debugLog('info', 'Fetching /api/candidates...');
    try {
        const response = await fetch('/api/candidates');
        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        const candidates = data.candidates || [];
        debugLog('success', `Loaded ${candidates.length} candidates from backend.`);
        
        window.candidatesMap = {};
        const select = document.getElementById('candidateSelect');
        select.innerHTML = '<option value="" disabled selected>-- Choose a Graduating Member --</option>';

        candidates.forEach(cand => {
            const member = cand.member;
            if (member && member.id) {
                window.candidatesMap[member.id] = cand;
                const opt = document.createElement('option');
                opt.value = member.id;
                opt.textContent = `${member.name} (${member.jobRole} • ${member.yearsExperience} yrs exp)`;
                select.appendChild(opt);
            }
        });

        setupCustomDropdown();
        renderCustomDropdownItems('');

    } catch (err) {
        debugLog('error', 'Failed to load candidates', err.message);
        alert(`Failed to load candidates: ${err.message}`);
    }
}

function renderProfileCard(candidate) {
    const member = candidate.member || {};
    const missions = candidate.missions || [];
    const signals = candidate.signals || {};

    debugLog('info', `Rendering profile card for ${member.name}`);

    document.getElementById('candName').textContent = member.name || 'Unknown';
    document.getElementById('candRole').textContent = member.jobRole || 'Engineer';
    document.getElementById('candExp').textContent = `${member.yearsExperience || 0} Years`;
    
    let difficulty = 'Foundational';
    if (member.yearsExperience >= 10) difficulty = 'Senior';
    else if (member.yearsExperience >= 3) difficulty = 'Intermediate';
    document.getElementById('candDifficulty').textContent = difficulty;

    const struggleChips = document.getElementById('struggleChips');
    const masteryChips = document.getElementById('masteryChips');
    struggleChips.innerHTML = '';
    masteryChips.innerHTML = '';

    missions.forEach(m => {
        const chip = document.createElement('span');
        if (m.skipped) {
            chip.className = 'chip struggle';
            chip.textContent = `Day ${m.day} (Skipped)`;
            struggleChips.appendChild(chip);
        } else if (m.passed && m.attempts >= 3) {
            chip.className = 'chip struggle';
            chip.textContent = `Day ${m.day} (${m.attempts} Att)`;
            struggleChips.appendChild(chip);
        } else if (m.passed && m.attempts === 1) {
            chip.className = 'chip mastery';
            chip.textContent = `Day ${m.day} (1st Try)`;
            masteryChips.appendChild(chip);
        }
    });

    if (struggleChips.children.length === 0) {
        struggleChips.innerHTML = '<span class="chip mastery">None recorded</span>';
    }
    if (masteryChips.children.length === 0) {
        masteryChips.innerHTML = '<span class="chip">Standard pace</span>';
    }

    document.getElementById('profileCard').style.display = 'flex';
}

async function startInterview(candidate) {
    currentSessionId = 'sess_' + Math.random().toString(36).substring(2, 9);
    questionCount = 0;

    debugLog('info', `Initializing session ID '${currentSessionId}' for '${candidate.member?.name}'`);

    const viewport = document.getElementById('chatViewport');
    const messages = viewport.querySelectorAll('.message-bubble, .welcome-banner');
    messages.forEach(el => el.remove());
    document.getElementById('feedbackPanel').style.display = 'none';

    document.getElementById('statusIndicator').classList.add('active');
    document.getElementById('sessionStatus').textContent = `Interviewing: ${candidate.member.name}`;

    document.getElementById('progressContainer').style.display = 'flex';
    document.getElementById('topicIndicatorBar').style.display = 'flex';
    document.getElementById('phaseBadge').style.display = 'inline-block';
    updateProgress(0);

    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.placeholder = "Type your technical response...";

    showTypingIndicator(true);

    try {
        const response = await fetch('/api/interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: currentSessionId,
                candidate: candidate
            })
        });

        debugLog('info', `POST /api/interview status: ${response.status} ${response.statusText}`);
        const data = await response.json();
        showTypingIndicator(false);

        if (!response.ok) {
            const errDetail = data.detail || 'Unknown server error';
            debugLog('error', `Server error starting interview (${response.status})`, errDetail);
            appendMessage('error', `⚠️ Server Error (${response.status}): ${errDetail}`);
            return;
        }

        debugLog('success', `Received response reply length: ${data.reply?.length || 0} characters`, data.reply);

        if (data.reply) {
            appendMessage('bot', data.reply);
            questionCount = 1;
            if (data.meta) updateProgressFromMeta(data.meta);
            else updateProgress(questionCount);
        } else {
            debugLog('error', 'API returned success status but data.reply was empty!');
            appendMessage('error', '⚠️ Server returned an empty reply.');
        }

    } catch (err) {
        showTypingIndicator(false);
        debugLog('error', 'Network or client error starting interview', err.message);
        appendMessage('error', `⚠️ Network Error: ${err.message}. Please verify backend server on http://127.0.0.1:8000`);
    }
}

async function sendUserMessage(text) {
    debugLog('info', `User sending message: "${text}"`);
    
    const quality = analyzeInputQuality(text);
    if (quality.isNonsense) {
        nonsenseWarnings++;
        debugLog('error', `Nonsense detected (strike ${nonsenseWarnings}/${MAX_NONSENSE_WARNINGS}): ${quality.reason}`);
        
        if (nonsenseWarnings <= MAX_NONSENSE_WARNINGS) {
            showNonsenseWarning(quality.reason);
            const inputEl = document.getElementById('userInput');
            inputEl.classList.add('shake');
            setTimeout(() => inputEl.classList.remove('shake'), 600);
            return;
        }
        debugLog('info', 'Max warnings exceeded — sending flagged message to server.');
    } else {
        nonsenseWarnings = 0;
    }

    appendMessage('user', text);

    const userInput = document.getElementById('userInput');
    userInput.value = '';

    isWaitingForResponse = true;
    showTypingIndicator(true);

    try {
        const response = await fetch('/api/interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: currentSessionId,
                message: text
            })
        });

        debugLog('info', `POST /api/interview status: ${response.status} ${response.statusText}`);
        const data = await response.json();
        showTypingIndicator(false);
        isWaitingForResponse = false;

        if (!response.ok) {
            const errDetail = data.detail || 'Unknown server error';
            debugLog('error', `Server error on turn (${response.status})`, errDetail);
            appendMessage('error', `⚠️ Server Error (${response.status}): ${errDetail}`);
            return;
        }

        debugLog('success', `Turn response received. reply length: ${data.reply?.length || 0}, done: ${data.done}`);

        if (data.reply) {
            appendMessage('bot', data.reply);
            questionCount += 1;
            if (data.meta) updateProgressFromMeta(data.meta);
            else updateProgress(questionCount);
        }

        if (data.done) {
            debugLog('info', 'Interview flagged as done. Processing feedback modal.');
            handleInterviewComplete(data.feedback);
        }

    } catch (err) {
        showTypingIndicator(false);
        isWaitingForResponse = false;
        debugLog('error', 'Network error in interview turn', err.message);
        appendMessage('error', `⚠️ Network Error: ${err.message}`);
    }
}

function formatMessageMarkdown(text) {
    if (!text) return '';
    // 1. Escape HTML
    let escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // 2. Bold **text**
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 3. Italic *text*
    escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 4. Code `text`
    escaped = escaped.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // 5. Linebreaks
    escaped = escaped.replace(/\n/g, '<br>');
    
    return escaped;
}

function appendMessage(sender, text) {
    const viewport = document.getElementById('chatViewport');
    const indicator = document.getElementById('typingIndicator');
    
    if (!viewport) {
        debugLog('error', '#chatViewport DOM element not found!');
        return;
    }

    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${sender}`;
    bubble.innerHTML = formatMessageMarkdown(text);

    debugLog('info', `Appending message bubble [${sender}], length: ${text?.length}`);

    if (indicator && indicator.parentNode === viewport) {
        viewport.insertBefore(bubble, indicator);
    } else {
        viewport.appendChild(bubble);
    }

    bubble.style.display = 'block';
    bubble.style.visibility = 'visible';
    bubble.style.opacity = '1';

    viewport.scrollTop = viewport.scrollHeight;
}

function showTypingIndicator(show) {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = show ? 'flex' : 'none';
    }
    if (show) {
        const viewport = document.getElementById('chatViewport');
        if (viewport) {
            viewport.scrollTop = viewport.scrollHeight;
        }
    }
}

function updateProgress(count) {
    const total = 8;
    const pct = Math.min(Math.round((count / total) * 100), 100);
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');
    if (fill) fill.style.width = `${pct}%`;
    if (text) text.textContent = `${count} / ${total} Primary Questions`;
}

function updateProgressFromMeta(meta) {
    if (!meta) return;
    const count = meta.primary_questions || questionCount;
    updateProgress(count);

    const phaseBadge = document.getElementById('phaseBadge');
    if (phaseBadge) {
        phaseBadge.textContent = meta.phase || 'CORE';
    }

    const topicEl = document.getElementById('currentTopicIndicator');
    if (topicEl) {
        topicEl.textContent = `Day ${meta.current_day}: ${meta.current_title || ''}`;
    }

    // Rich LLM Telemetry Debug Drawer Trace
    if (meta.llm_provider || meta.llm_model) {
        const providerName = (meta.llm_provider || 'ollama').toUpperCase();
        const modelName = meta.llm_model || 'unknown-model';
        const latency = meta.llm_latency_ms ? `${meta.llm_latency_ms}ms` : 'N/A';
        const isFallback = meta.llm_fallback ? ' [FALLBACK ACTIVE]' : '';
        const statusType = meta.llm_fallback ? 'error' : 'success';

        debugLog(statusType, `🤖 [LLM DEBUG TRACE] Provider: ${providerName} | Model: ${modelName} | Latency: ${latency} | Status: ${meta.llm_status || 'OK'}${isFallback}`);
    }
}

function handleInterviewComplete(feedback) {
    lastFeedbackData = feedback;
    document.getElementById('sessionStatus').textContent = 'Interview Complete';
    const statusInd = document.getElementById('statusIndicator');
    if (statusInd) statusInd.classList.remove('active');

    const input = document.getElementById('userInput');
    const btn = document.getElementById('sendBtn');
    if (input) {
        input.disabled = true;
        input.placeholder = "Interview completed. View evaluation below.";
    }
    if (btn) btn.disabled = true;

    if (feedback) {
        document.getElementById('fbSummary').textContent = feedback.summary || 'Interview concluded successfully.';

        const strengthsList = document.getElementById('fbStrengths');
        if (strengthsList) {
            strengthsList.innerHTML = '';
            (feedback.strengths || []).forEach(s => {
                const li = document.createElement('li');
                li.textContent = s;
                strengthsList.appendChild(li);
            });
        }

        const gapsList = document.getElementById('fbGaps');
        if (gapsList) {
            gapsList.innerHTML = '';
            (feedback.gaps || []).forEach(g => {
                const li = document.createElement('li');
                li.textContent = g;
                gapsList.appendChild(li);
            });
        }

        const topicScoresGrid = document.getElementById('fbTopicScores');
        if (topicScoresGrid) {
            topicScoresGrid.innerHTML = '';
            const scores = feedback.topic_scores || [];
            scores.forEach(ts => {
                const card = document.createElement('div');
                card.className = 'topic-score-card';
                card.innerHTML = `
                    <div class="topic-score-header">
                        <span class="topic-score-title">Day ${ts.day}: ${ts.title}</span>
                        <span class="topic-score-badge">${ts.score}/10</span>
                    </div>
                    <p class="topic-score-note">${ts.note || ''}</p>
                `;
                topicScoresGrid.appendChild(card);
            });
        }

        const nextList = document.getElementById('fbNext');
        if (nextList) {
            nextList.innerHTML = '';
            (feedback.next || []).forEach(n => {
                const li = document.createElement('li');
                li.textContent = n;
                nextList.appendChild(li);
            });
        }

        const panel = document.getElementById('feedbackPanel');
        if (panel) {
            panel.style.display = 'flex';
            panel.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

function generateMarkdownFeedback(fb) {
    if (!fb) return "# Technical Interview Evaluation\n\nNo evaluation available.";
    const candName = currentCandidate?.member?.name || "Candidate";
    let md = `# Technical Interview Evaluation — ${candName}\n\n`;
    md += `## Executive Summary\n${fb.summary}\n\n`;
    md += `## Key Strengths\n`;
    (fb.strengths || []).forEach(s => md += `- ${s}\n`);
    md += `\n## Growth Areas & Gaps\n`;
    (fb.gaps || []).forEach(g => md += `- ${g}\n`);
    if (fb.topic_scores && fb.topic_scores.length > 0) {
        md += `\n## Topic Scores\n`;
        fb.topic_scores.forEach(ts => {
            md += `- **Day ${ts.day} (${ts.title})**: ${ts.score}/10 — ${ts.note}\n`;
        });
    }
    md += `\n## Recommended Next Steps\n`;
    (fb.next || []).forEach(n => md += `- ${n}\n`);
    return md;
}

function copyFeedbackAsMarkdown() {
    const md = generateMarkdownFeedback(lastFeedbackData);
    navigator.clipboard.writeText(md).then(() => {
        const copyBtn = document.getElementById('copyFbBtn');
        if (copyBtn) {
            const orig = copyBtn.textContent;
            copyBtn.textContent = '✅ Copied!';
            setTimeout(() => copyBtn.textContent = orig, 2000);
        }
    }).catch(err => {
        alert('Failed to copy feedback to clipboard');
    });
}

function downloadFeedbackAsMarkdown() {
    const md = generateMarkdownFeedback(lastFeedbackData);
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const candName = (currentCandidate?.member?.name || "Candidate").replace(/\s+/g, '_');
    a.download = `interview_evaluation_${candName}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
