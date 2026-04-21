const API = 'http://localhost:8000/api';
let profile = JSON.parse(localStorage.getItem('amma_profile') || '{}');
let currentLang = profile.language || 'english';
let selectedImageFile = null;
let recognition = null;
let isRecording = false;

// ── INIT ──
function init() {
  if (!profile.user_id) { window.location.href = 'index.html'; return; }

  document.getElementById('profile-info').innerHTML = `
    <div><strong>${profile.name}</strong></div>
    ${profile.gestational_week ? `<div>Week ${profile.gestational_week} of pregnancy</div>` : ''}
    ${profile.child_dob ? `<div>Baby DOB: ${profile.child_dob}</div>` : ''}
    ${profile.location ? `<div>${profile.location}</div>` : ''}
  `;

  document.querySelector(`[onclick="setLang(this,'${currentLang}')"]`)?.classList.add('active');
  loadReminders();
  setupVoice();
}

// ── LANGUAGE ──
function setLang(el, lang) {
  currentLang = lang;
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  profile.language = lang;
  localStorage.setItem('amma_profile', JSON.stringify(profile));
  if (recognition) {
    const langMap = { english: 'en-IN', kannada: 'kn-IN', hindi: 'hi-IN' };
    recognition.lang = langMap[lang] || 'en-IN';
  }
}

// ── VOICE INPUT ──
function setupVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    document.getElementById('voice-btn').style.opacity = '0.4';
    document.getElementById('voice-btn').title = 'Voice not supported in this browser';
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;

  const langMap = { english: 'en-IN', kannada: 'kn-IN', hindi: 'hi-IN' };
  recognition.lang = langMap[currentLang] || 'en-IN';

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(r => r[0].transcript).join('');
    document.getElementById('chat-input').value = transcript;
    autoResize(document.getElementById('chat-input'));
  };

  recognition.onend = () => {
    stopRecording();
    const text = document.getElementById('chat-input').value.trim();
    if (text) sendMessage();
  };

  recognition.onerror = () => stopRecording();
}

function toggleVoice() {
  if (!recognition) {
    alert('Voice input is not supported in your browser. Please use Chrome.');
    return;
  }
  isRecording ? stopRecording() : startRecording();
}

function startRecording() {
  isRecording = true;
  recognition.start();
  document.getElementById('voice-btn').classList.add('recording');
  document.getElementById('voice-btn').textContent = '⏹';
  document.getElementById('voice-status').classList.add('visible');
}

function stopRecording() {
  isRecording = false;
  if (recognition) { try { recognition.stop(); } catch(e) {} }
  document.getElementById('voice-btn').classList.remove('recording');
  document.getElementById('voice-btn').textContent = '🎤';
  document.getElementById('voice-status').classList.remove('visible');
}

// ── IMAGE UPLOAD ──
function previewImage(input) {
  const file = input.files[0];
  if (!file) return;
  selectedImageFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('preview-img').src = e.target.result;
    document.getElementById('preview-name').textContent = file.name;
    document.getElementById('image-preview').classList.add('visible');
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  selectedImageFile = null;
  document.getElementById('img-input').value = '';
  document.getElementById('image-preview').classList.remove('visible');
}

// ── SEND MESSAGE ──
async function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text && !selectedImageFile) return;

  input.value = '';
  input.style.height = 'auto';
  document.getElementById('send-btn').disabled = true;

  if (selectedImageFile) {
    await sendImageMessage(text);
  } else {
    await sendTextMessage(text);
  }

  document.getElementById('send-btn').disabled = false;
  input.focus();
}

async function sendTextMessage(text) {
  addMessage('user', text);
  addTypingIndicator();

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: profile.user_id,
        message: text,
        language: currentLang,
        gestational_week: profile.gestational_week || null,
        child_dob: profile.child_dob || null,
      }),
    });
    const data = await res.json();
    removeTypingIndicator();
    addMessage('ai', data.reply, data.is_high_risk, data.risk_message, data.suggested_action);
  } catch (e) {
    removeTypingIndicator();
    addMessage('ai', 'Sorry, could not connect. Please call Karnataka 104 health helpline.');
  }
}

async function sendImageMessage(caption) {
  addMessage('user', caption || '📷 Photo uploaded for analysis', false, null, null, selectedImageFile);
  const imageFile = selectedImageFile;
  removeImage();
  addTypingIndicator();

  try {
    const formData = new FormData();
    formData.append('user_id', profile.user_id);
    formData.append('message', caption || 'Please analyze this image');
    formData.append('language', currentLang);
    if (profile.gestational_week) formData.append('gestational_week', profile.gestational_week);
    if (profile.child_dob) formData.append('child_dob', profile.child_dob);
    formData.append('image', imageFile);

    const res = await fetch(`${API}/chat/image`, { method: 'POST', body: formData });
    const data = await res.json();
    removeTypingIndicator();
    addMessage('ai', data.reply, data.is_high_risk, data.risk_message, data.suggested_action);
  } catch (e) {
    removeTypingIndicator();
    addMessage('ai', 'Sorry, could not analyze the image. Please describe your symptoms in text.');
  }
}

// ── MESSAGES UI ──
function addMessage(role, text, isRisk = false, riskMessage = null, action = null, imageFile = null) {
  const messages = document.getElementById('messages');
  messages.querySelector('.welcome-msg')?.remove();

  const div = document.createElement('div');
  div.className = `message ${role}`;
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (role === 'user') {
    let imgHtml = '';
    if (imageFile) {
      const url = URL.createObjectURL(imageFile);
      imgHtml = `<img src="${url}" class="msg-image" alt="uploaded"/>`;
    }
    div.innerHTML = `
      ${imgHtml}
      <div class="bubble bubble-user">${escapeHtml(text)}</div>
      <span class="message-meta">${time}</span>
    `;
  } else {
    let extra = '';
    if (isRisk && riskMessage) {
      extra = `
        <div class="risk-alert" style="margin-top:0.5rem;max-width:80%;">
          ⚠️ <strong>${riskMessage}</strong>
          ${action ? `<div style="margin-top:0.4rem;font-size:0.85rem;">${action}</div>` : ''}
          <div style="margin-top:0.5rem;font-size:0.82rem;">📞 Call <strong>108</strong> for emergency · <strong>104</strong> for health helpline</div>
        </div>
      `;
    }
    div.innerHTML = `
      <div class="bubble bubble-ai">${formatText(text)}</div>
      ${extra}
      <span class="message-meta">Amma AI · ${time}</span>
    `;
  }

  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function addTypingIndicator() {
  const messages = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = 'message ai';
  div.id = 'typing-indicator';
  div.innerHTML = `<div class="bubble bubble-ai"><div class="typing"><span></span><span></span><span></span></div></div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTypingIndicator() {
  document.getElementById('typing-indicator')?.remove();
}

// ── REMINDERS ──
async function loadReminders() {
  try {
    const res = await fetch(`${API}/reminders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: profile.user_id,
        gestational_week: profile.gestational_week || null,
        child_dob: profile.child_dob || null,
      }),
    });
    const data = await res.json();
    const el = document.getElementById('reminders-list');
    if (!data.reminders?.length) {
      el.innerHTML = '<p style="font-size:0.82rem;color:var(--text-muted)">No reminders right now.</p>';
      return;
    }
    el.innerHTML = data.reminders.map(r => `
      <div class="reminder-item ${r.priority === 'HIGH' ? 'high' : ''}">
        <div class="r-title">${r.title}</div>
        <div class="r-desc">${r.description}</div>
      </div>
    `).join('');
  } catch (e) {
    document.getElementById('reminders-list').innerHTML = '<p style="font-size:0.82rem;color:var(--text-muted)">Could not load reminders.</p>';
  }
}

// ── HELPERS ──
function sendQuick(text) {
  document.getElementById('chat-input').value = text;
  sendMessage();
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatText(text) {
  return text
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
    .replace(/\n- /g,'<br>• ')
    .replace(/\n/g,'<br>');
}

init();