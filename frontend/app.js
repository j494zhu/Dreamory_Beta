const API = '';

const $ = (sel, el) => (el || document).querySelector(sel);
const $$ = (sel, el) => [...(el || document).querySelectorAll(sel)];

const els = {
  userIdDisplay: $('#userIdDisplay'),
  btnNewUser: $('#btnNewUser'),
  btnNewChat: $('#btnNewChat'),
  chatList: $('#chatList'),
  noChatSelected: $('#noChatSelected'),
  chatArea: $('#chatArea'),
  chatTitle: $('#chatTitle'),
  btnRename: $('#btnRename'),
  messages: $('#messages'),
  inputMsg: $('#inputMsg'),
  btnSend: $('#btnSend'),
  btnShowMessages: $('#btnShowMessages'),
  btnShowThinking: $('#btnShowThinking'),
  btnPersona: $('#btnPersona'),
  debugPanel: $('#debugPanel'),
};

let state = {
  userId: localStorage.getItem('dreamory_user_id') || '',
  chatId: null,
  chatTitle: '',
  messages: [],
  persona: null,
  lastDebug: null,
};

function api(path, opts = {}) {
  const url = API + path;
  const init = { headers: { 'Content-Type': 'application/json' }, ...opts };
  if (init.body && typeof init.body === 'object') init.body = JSON.stringify(init.body);
  return fetch(url, init).then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
}

async function createUser() {
  const { user_id } = await api('/users/', { method: 'POST' });
  state.userId = user_id;
  localStorage.setItem('dreamory_user_id', user_id);
  els.userIdDisplay.textContent = user_id.slice(0, 8) + '…';
  els.btnNewChat.disabled = false;
  await loadChatList();
}

async function loadChatList() {
  if (!state.userId) return;
  els.chatList.innerHTML = '<li style="color:var(--text-muted)">加载中…</li>';
  try {
    const chats = await api(`/users/${state.userId}/chats`);
    renderChatList(chats);
  } catch (e) {
    els.chatList.innerHTML = '<li style="color:red">加载失败</li>';
  }
}

function renderChatList(chats) {
  els.chatList.innerHTML = '';
  if (!chats.length) {
    els.chatList.innerHTML = '<li style="color:var(--text-muted);font-size:12px">暂无对话</li>';
    return;
  }
  chats.forEach(ch => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span class="chat-name${ch.chat_id === state.chatId ? ' active' : ''}" data-id="${ch.chat_id}">${escapeHtml(ch.title || ch.chat_id.slice(0, 8))}</span>
      <button class="btn-icon" data-action="rename" data-id="${ch.chat_id}" title="重命名">&#9998;</button>
    `;
    li.querySelector('.chat-name').addEventListener('click', () => selectChat(ch.chat_id));
    li.querySelector('.btn-icon').addEventListener('click', (e) => { e.stopPropagation(); showRenameDialog(ch.chat_id, ch.title); });
    els.chatList.appendChild(li);
  });
}

async function createChat() {
  if (!state.userId) return;
  try {
    const { chat_id } = await api('/chats/', { method: 'POST', body: { user_id: state.userId, title: '新对话' } });
    await loadChatList();
    selectChat(chat_id);
  } catch (e) {
    alert('创建对话失败');
  }
}

async function selectChat(chatId) {
  state.chatId = chatId;
  els.noChatSelected.classList.add('hidden');
  els.chatArea.classList.remove('hidden');
  els.inputMsg.disabled = false;
  els.btnSend.disabled = false;
  els.debugPanel.classList.add('hidden');
  els.messages.innerHTML = '<div class="msg assistant" style="color:var(--text-muted)">加载中…</div>';
  try {
    const chat = await api(`/chats/${chatId}`);
    state.chatTitle = chat.title || chatId.slice(0, 8);
    state.messages = chat.messages || [];
    state.persona = chat.persona || null;
    state.lastDebug = null;
    els.chatTitle.textContent = state.chatTitle;
    renderMessages();
  } catch (e) {
    els.messages.innerHTML = '<div class="msg assistant" style="color:red">加载失败</div>';
  }
  await loadChatList();
}

function renderMessages() {
  els.messages.innerHTML = '';
  state.messages.forEach(m => {
    if (m.role === 'system') return;
    const div = document.createElement('div');
    div.className = `msg ${m.role}`;
    div.textContent = m.content;
    els.messages.appendChild(div);
  });
  els.messages.scrollTop = els.messages.scrollHeight;
}

async function sendMessage() {
  const content = els.inputMsg.value.trim();
  if (!content || !state.chatId) return;
  els.inputMsg.value = '';
  els.inputMsg.disabled = true;
  els.btnSend.disabled = true;

  const userDiv = document.createElement('div');
  userDiv.className = 'msg user';
  userDiv.textContent = content;
  els.messages.appendChild(userDiv);
  els.messages.scrollTop = els.messages.scrollHeight;

  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'msg assistant';
  loadingDiv.innerHTML = '<span class="spinner"></span>思考中…';
  els.messages.appendChild(loadingDiv);
  els.messages.scrollTop = els.messages.scrollHeight;

  try {
    const res = await api(`/chats/${state.chatId}/messages`, { method: 'POST', body: { content } });
    loadingDiv.remove();

    const assistantDiv = document.createElement('div');
    assistantDiv.className = 'msg assistant';
    assistantDiv.textContent = res.content || '(空)';
    els.messages.appendChild(assistantDiv);
    els.messages.scrollTop = els.messages.scrollHeight;

    state.lastDebug = res.debug || null;
  } catch (e) {
    loadingDiv.remove();
    const errDiv = document.createElement('div');
    errDiv.className = 'msg assistant';
    errDiv.style.color = 'red';
    errDiv.textContent = '发送失败: ' + e.message;
    els.messages.appendChild(errDiv);
  }

  els.inputMsg.disabled = false;
  els.btnSend.disabled = false;
  els.inputMsg.focus();
}

function showRenameDialog(chatId, currentTitle) {
  const overlay = document.createElement('div');
  overlay.className = 'dialog-overlay';
  overlay.innerHTML = `
    <div class="dialog">
      <h3>重命名对话</h3>
      <input type="text" id="renameInput" value="${escapeHtml(currentTitle || '')}" maxlength="255" autofocus>
      <div class="dialog-actions">
        <button class="btn btn-sm" id="renameCancel">取消</button>
        <button class="btn btn-sm" id="renameConfirm">确定</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const input = $('#renameInput', overlay);
  input.select();

  $('#renameCancel', overlay).addEventListener('click', () => overlay.remove());
  $('#renameConfirm', overlay).addEventListener('click', async () => {
    const title = input.value.trim();
    if (!title) return;
    try {
      await api(`/chats/${chatId}/title`, { method: 'PUT', body: { title } });
      overlay.remove();
      if (state.chatId === chatId) {
        state.chatTitle = title;
        els.chatTitle.textContent = title;
      }
      await loadChatList();
    } catch (e) {
      alert('重命名失败');
    }
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') $('#renameConfirm', overlay).click();
    if (e.key === 'Escape') overlay.remove();
  });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

async function showPersonaDialog() {
  let presets = {};
  try { presets = await api('/chats/presets'); } catch (e) { alert('加载预设失败'); return; }

  const presetKeys = Object.keys(presets);
  if (!presetKeys.length) { alert('无可用预设'); return; }

  const curPersona = state.persona || {};
  const curPreset = presetKeys.includes(curPersona.preset) ? curPersona.preset : presetKeys[0];

  const overlay = document.createElement('div');
  overlay.className = 'dialog-overlay';
  overlay.innerHTML = `
    <div class="dialog dialog-wide">
      <h3>修改初始人设</h3>
      <label>预设人格</label>
      <select id="personaPreset">${presetKeys.map(k => {
        const p = presets[k];
        return `<option value="${k}"${k === curPreset ? ' selected' : ''}>${k} (anx=${p.anxiety} / avo=${p.avoidance} / expr=${p.expressiveness})</option>`;
      }).join('')}</select>
      <label>名字</label>
      <input type="text" id="personaName" value="${escapeHtml(curPersona.name || presets[curPreset].name || '')}" placeholder="${escapeHtml(presets[curPreset].name || '')}">
      <label>简介 profile</label>
      <textarea id="personaProfile" rows="3" placeholder="${escapeHtml(presets[curPreset].profile || '')}">${escapeHtml(curPersona.profile || '')}</textarea>
      <p class="dialog-hint">名字/简介留空则用所选预设的默认值。</p>
      <div class="dialog-actions">
        <button class="btn btn-sm" id="personaCancel">取消</button>
        <button class="btn btn-sm" id="personaConfirm">保存</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const sel = $('#personaPreset', overlay);
  const nameInput = $('#personaName', overlay);
  const profileInput = $('#personaProfile', overlay);

  sel.addEventListener('change', () => {
    const p = presets[sel.value];
    nameInput.placeholder = p.name || '';
    profileInput.placeholder = p.profile || '';
  });

  $('#personaCancel', overlay).addEventListener('click', () => overlay.remove());
  $('#personaConfirm', overlay).addEventListener('click', async () => {
    const preset = sel.value;
    const name = nameInput.value.trim() || null;
    const profile = profileInput.value.trim() || null;
    try {
      const res = await api(`/chats/${state.chatId}/persona`, { method: 'PUT', body: { preset, name, profile } });
      state.persona = res;
      overlay.remove();
    } catch (e) {
      alert('保存人设失败');
    }
  });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

function toggleMessagesArray() {
  if (!state.messages.length) return;
  els.debugPanel.classList.toggle('hidden');
  if (!els.debugPanel.classList.contains('hidden')) {
    els.debugPanel.innerHTML = '<strong>消息数组 (JSON):</strong>\n\n' + JSON.stringify(state.messages, null, 2);
  }
}

function toggleThinking() {
  els.debugPanel.classList.toggle('hidden');
  if (!els.debugPanel.classList.contains('hidden')) {
    if (!state.lastDebug) {
      els.debugPanel.textContent = '(无思考数据 — 请先发送一条消息)';
    } else {
      const d = state.lastDebug;
      let text = '';
      text += '🧠 模式: ' + (d.mode || '?') + '\n\n';
      text += '── 内心独白 ──\n' + (d.thinking || '(无)') + '\n\n';
      text += '── 标量 ──\n' + JSON.stringify(d.scalars || {}, null, 2) + '\n\n';
      text += '── trace ──\n' + JSON.stringify(d.trace || [], null, 2);
      if (d.open_loops && d.open_loops.length) {
        text += '\n\n── 挂起回路 ──\n' + JSON.stringify(d.open_loops, null, 2);
      }
      if (d.grievances && d.grievances.length) {
        text += '\n\n── 旧账 ──\n' + JSON.stringify(d.grievances, null, 2);
      }
      els.debugPanel.textContent = text;
    }
  }
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// ── Event bindings ──
els.btnNewUser.addEventListener('click', createUser);
els.btnNewChat.addEventListener('click', createChat);
els.btnSend.addEventListener('click', sendMessage);
els.btnRename.addEventListener('click', () => showRenameDialog(state.chatId, state.chatTitle));
els.btnShowMessages.addEventListener('click', toggleMessagesArray);
els.btnShowThinking.addEventListener('click', toggleThinking);
els.btnPersona.addEventListener('click', showPersonaDialog);

els.inputMsg.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ── Init ──
if (state.userId) {
  els.userIdDisplay.textContent = state.userId.slice(0, 8) + '…';
  els.btnNewChat.disabled = false;
  loadChatList();
}
