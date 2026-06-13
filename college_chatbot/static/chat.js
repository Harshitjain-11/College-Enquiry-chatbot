/**
 * chat.js — ITM Gwalior College Enquiry Chatbot
 */

// ── Session ───────────────────────────────────────────────────
const SESSION_KEY = 'itm_chatbot_session';
let sessionId = localStorage.getItem(SESSION_KEY);
if (!sessionId) {
  sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
  localStorage.setItem(SESSION_KEY, sessionId);
}

// ── Today label ───────────────────────────────────────────────
document.getElementById('todayLabel').textContent =
  new Date().toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long'
  });

// ── DOM ───────────────────────────────────────────────────────
const chatWindow = document.getElementById('chatWindow');
const userInput  = document.getElementById('userInput');
const sendBtn    = document.getElementById('sendBtn');
const typingRow  = document.getElementById('typingRow');

// ── Helpers ───────────────────────────────────────────────────
const getTime = () =>
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

function renderMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
}

function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ── Append Message ────────────────────────────────────────────
function appendMessage(text, role, quickReplies = []) {
  const row = document.createElement('div');
  row.className = 'row ' + role;

  // Bot avatar — gold ITM badge
  if (role === 'bot') {
    const av = document.createElement('div');
    av.className = 'av';
    av.textContent = 'ITM';
    row.appendChild(av);
  }

  const bwrap = document.createElement('div');
  bwrap.className = 'bwrap';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = renderMarkdown(text);
  bwrap.appendChild(bubble);

  const ts = document.createElement('div');
  ts.className = 'ts';
  ts.textContent = getTime();
  bwrap.appendChild(ts);

  // Quick reply buttons
  if (quickReplies && quickReplies.length > 0) {
    const qrs = document.createElement('div');
    qrs.className = 'qrs';
    quickReplies.forEach(label => {
      const btn = document.createElement('button');
      btn.className = 'qr-btn';
      btn.textContent = label;
      btn.onclick = () => sendUserMessage(label);
      qrs.appendChild(btn);
    });
    bwrap.appendChild(qrs);
  }

  row.appendChild(bwrap);
  chatWindow.appendChild(row);
  scrollToBottom();
}

// ── Typing ────────────────────────────────────────────────────
function showTyping()  { typingRow.style.display = 'flex'; scrollToBottom(); }
function hideTyping()  { typingRow.style.display = 'none'; }

// ── Input State ───────────────────────────────────────────────
function setInputEnabled(on) {
  userInput.disabled = !on;
  sendBtn.disabled   = !on || userInput.value.trim().length === 0;
  if (on) userInput.focus();
}

userInput.addEventListener('input', () => {
  sendBtn.disabled = userInput.value.trim().length === 0;
});

// ── Send ──────────────────────────────────────────────────────
async function sendUserMessage(text) {
  const msg = text.trim();
  if (!msg) return;

  appendMessage(msg, 'user');
  userInput.value = '';
  setInputEnabled(false);

  await new Promise(r => setTimeout(r, 380));
  showTyping();

  try {
    const res = await fetch('/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: msg, session_id: sessionId }),
    });

    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    hideTyping();
    appendMessage(
      data.reply || 'Something went wrong. Please try again.',
      'bot',
      data.quick_replies || []
    );

    if (data.booking_id) {
      appendMessage(
        '✅ Your **Booking ID**: **' + data.booking_id + '**\nPlease save this for your visit.',
        'bot',
        ['Contact Us']
      );
    }

  } catch (err) {
    hideTyping();
    appendMessage(
      '⚠️ Network error. Please check your connection and try again.',
      'bot',
      ['Retry']
    );
  } finally {
    setInputEnabled(true);
  }
}

function sendMessage() {
  const text = userInput.value.trim();
  if (text) sendUserMessage(text);
}

// Enter key
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Send button click
sendBtn.addEventListener('click', sendMessage);

// ── Welcome Message ───────────────────────────────────────────
(function showWelcome() {
  appendMessage(
    '👋 Welcome to **Institute of Technology & Management, Gwalior**!\n\n' +
    'I\'m your virtual admission counsellor. I can help you with:\n' +
    '📚 Courses & Eligibility (B.Tech affiliated to RGPV Bhopal)\n' +
    '💰 Fee Structure & Scholarships\n' +
    '📝 Admission Process & Dates\n' +
    '📅 Book a Campus Visit\n\n' +
    'What would you like to know? 😊',
    'bot',
    ['Admission Process', 'Courses Offered', 'Fee Structure', 'Book Appointment']
  );
  sendBtn.disabled = true;
  userInput.focus();
})();