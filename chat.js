/* chat.js — FAQ Chatbot frontend */
'use strict';

const messagesEl  = document.getElementById('messages');
const chatForm    = document.getElementById('chatForm');
const userInput   = document.getElementById('userInput');
const quickList   = document.getElementById('quick-list');
const suggestEl   = document.getElementById('suggestions');
const clearBtn    = document.getElementById('clearBtn');
const menuBtn     = document.getElementById('menuBtn');
const sidebar     = document.getElementById('sidebar');

// ── Bot SVG avatar (reusable) ───────────────────────────────────────────────
const BOT_AVATAR_SVG = `<svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="18" cy="18" r="18" fill="#6366f1"/>
  <rect x="9" y="11" width="18" height="14" rx="4" fill="white" opacity="0.9"/>
  <circle cx="14" cy="18" r="2" fill="#6366f1"/>
  <circle cx="22" cy="18" r="2" fill="#6366f1"/>
  <rect x="14" y="25" width="8" height="2" rx="1" fill="white" opacity="0.7"/>
  <rect x="12" y="7" width="3" height="5" rx="1.5" fill="white" opacity="0.6"/>
  <rect x="21" y="7" width="3" height="5" rx="1.5" fill="white" opacity="0.6"/>
</svg>`;

// ── Suggested follow-ups (static set, could be dynamic) ────────────────────
const FOLLOW_UPS = [
  'What is your return policy?',
  'How can I track my order?',
  'What payment methods do you accept?',
  'Do you ship internationally?',
  'How do I reset my password?',
];

// ── Init ────────────────────────────────────────────────────────────────────
(async function init() {
  renderWelcome();
  await loadQuickPicks();
  renderSuggestions(FOLLOW_UPS.slice(0, 4));
})();

// ── Sidebar toggle (mobile) ─────────────────────────────────────────────────
menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
document.addEventListener('click', (e) => {
  if (sidebar.classList.contains('open') &&
      !sidebar.contains(e.target) &&
      e.target !== menuBtn) {
    sidebar.classList.remove('open');
  }
});

// ── Clear chat ──────────────────────────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  messagesEl.innerHTML = '';
  renderWelcome();
  renderSuggestions(FOLLOW_UPS.slice(0, 4));
});

// ── Form submit ─────────────────────────────────────────────────────────────
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  userInput.value = '';
  suggestEl.innerHTML = '';

  appendUserBubble(text);
  const typingId = appendTyping();

  try {
    const res  = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    removeTyping(typingId);
    appendBotBubble(data);
  } catch {
    removeTyping(typingId);
    appendBotBubble({
      answer: 'Something went wrong connecting to the server. Please try again.',
      confidence_label: 'none',
      matched_question: null,
    });
  }
});

// ── Load quick-pick buttons from /api/faqs ──────────────────────────────────
async function loadQuickPicks() {
  try {
    const res  = await fetch('/api/faqs');
    const data = await res.json();
    // Show a random selection of 6
    const sample = shuffle(data.questions).slice(0, 6);
    sample.forEach(q => {
      const btn = document.createElement('button');
      btn.className = 'quick-btn';
      btn.textContent = q;
      btn.addEventListener('click', () => sendMessage(q));
      quickList.appendChild(btn);
    });
  } catch { /* silently fail */ }
}

// ── Render helpers ──────────────────────────────────────────────────────────
function renderWelcome() {
  appendBotBubble({
    answer: "👋 Hi there! I'm your FAQ assistant. Ask me anything about shipping, returns, payments, accounts, and more. What can I help you with today?",
    confidence_label: 'high',
    matched_question: null,
  });
}

function renderSuggestions(items) {
  suggestEl.innerHTML = '';
  items.forEach(text => {
    const chip = document.createElement('button');
    chip.className = 'suggestion-chip';
    chip.textContent = text;
    chip.addEventListener('click', () => sendMessage(text));
    suggestEl.appendChild(chip);
  });
}

function appendUserBubble(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `
    <div class="msg-avatar user-av">U</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;
  messagesEl.appendChild(row);
  scrollBottom();
}

function appendBotBubble(data) {
  const row = document.createElement('div');
  row.className = 'msg-row bot';

  let extra = '';

  if (data.matched_question) {
    const label   = data.confidence_label;
    const pct     = data.confidence !== undefined ? Math.round(data.confidence * 100) : '—';
    const dot     = label === 'high' ? '●' : label === 'medium' ? '◐' : '○';
    extra += `
      <div class="matched-q">
        <strong>Matched:</strong> ${escapeHtml(data.matched_question)}
      </div>
      <div class="confidence-badge ${label}">
        ${dot} ${label} confidence &nbsp;·&nbsp; ${pct}%
      </div>`;
  }

  row.innerHTML = `
    <div class="msg-avatar">${BOT_AVATAR_SVG}</div>
    <div class="bubble">
      ${escapeHtml(data.answer)}
      ${extra}
    </div>
  `;
  messagesEl.appendChild(row);
  scrollBottom();
}

let _typingCounter = 0;
function appendTyping() {
  const id  = 'typing-' + (++_typingCounter);
  const row = document.createElement('div');
  row.className = 'msg-row bot';
  row.id = id;
  row.innerHTML = `
    <div class="msg-avatar">${BOT_AVATAR_SVG}</div>
    <div class="typing-bubble">
      <span></span><span></span><span></span>
    </div>
  `;
  messagesEl.appendChild(row);
  scrollBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ── Utilities ────────────────────────────────────────────────────────────────
function sendMessage(text) {
  userInput.value = text;
  chatForm.dispatchEvent(new Event('submit'));
}

function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;')
    .replace(/'/g,  '&#39;');
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
