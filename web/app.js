// --- Tiny state & helpers
const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn  = document.getElementById('micBtn');
const speakToggle = document.getElementById('speakToggle');
const voiceSelect = document.getElementById('voiceSelect');
const statusPill = document.getElementById('status');

const API = '/api/chat';
const MODEL = 'gpt-4o-mini';   // fast, mobile-friendly

// Persist conversation locally so it “feels” self-evolving to the same user
const STORAGE_KEY = 'jarvis.conversation.v1';
let messages = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

// Speech
let voices = [];
function populateVoices() {
  voices = window.speechSynthesis ? speechSynthesis.getVoices() : [];
  voiceSelect.innerHTML = '';
  voices.forEach((v, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = `${v.name} (${v.lang})`;
    voiceSelect.appendChild(opt);
  });
}
if ('speechSynthesis' in window) {
  speechSynthesis.onvoiceschanged = populateVoices;
  populateVoices();
}

function speak(text) {
  if (!speakToggle.checked || !('speechSynthesis' in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  const idx = parseInt(voiceSelect.value || '0', 10);
  if (voices[idx]) u.voice = voices[idx];
  speechSynthesis.cancel(); // interrupt previous
  speechSynthesis.speak(u);
}

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
}

function addMessage(role, content, render = true) {
  messages.push({ role, content });
  save();
  if (!render) return;

  const row = document.createElement('div');
  row.className = `msg ${role === 'user' ? 'user' : 'ai'}`;
  const b = document.createElement('div');
  b.className = 'bubble';
  b.textContent = content;
  row.appendChild(b);
  chatEl.appendChild(row);
  chatEl.scrollTop = chatEl.scrollHeight;
}

// Initial render
messages.forEach(m => addMessage(m.role, m.content, true));

// Network status
function refreshStatus() {
  statusPill.textContent = navigator.onLine ? 'online' : 'offline';
  statusPill.style.color = navigator.onLine ? '#93e6b8' : '#fca5a5';
}
window.addEventListener('online', refreshStatus);
window.addEventListener('offline', refreshStatus);
refreshStatus();

// Send text to backend
async function sendText(text) {
  addMessage('user', text);
  inputEl.value = '';

  try {
    const res = await fetch(API, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ model: MODEL, messages })
    });
    const data = await res.json();
    const reply = data?.content || 'Hmm, I could not think of a reply.';
    addMessage('assistant', reply);
    speak(reply);
  } catch (err) {
    console.error(err);
    const msg = 'Network error. I saved your message — try again when online.';
    addMessage('assistant', msg);
  }
}

// UI events
sendBtn.addEventListener('click', () => {
  const text = inputEl.value.trim();
  if (text) sendText(text);
});
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const text = inputEl.value.trim();
    if (text) sendText(text);
  }
});

// Mic: use browser Web Speech (where available) for hands-free
let recognizing = false;
let rec = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  rec = new SR();
  rec.continuous = false;
  rec.interimResults = false;
  rec.lang = navigator.language || 'en-US';
  rec.onresult = (evt) => {
    const text = evt.results[0][0].transcript;
    sendText(text);
  };
  rec.onend = () => {
    recognizing = false;
    micBtn.style.opacity = '1';
  };
}

micBtn.addEventListener('click', () => {
  if (!rec) {
    alert('Speech recognition not supported on this browser. Try Chrome or mobile Chrome.');
    return;
  }
  if (recognizing) {
    rec.stop();
    recognizing = false;
    micBtn.style.opacity = '1';
  } else {
    speechSynthesis.cancel();
    rec.start();
    recognizing = true;
    micBtn.style.opacity = '0.6';
  }
});
