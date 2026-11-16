const $ = selector => document.querySelector(selector);
const state = { busy: false, view: 'structures' };
const pendingRequests = new Map();
let requestId = 0;
let toastTimer;

function icon(name) {
  return `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function toast(message) {
  clearTimeout(toastTimer);
  $('#toast').textContent = message;
  $('#toast').classList.add('visible');
  toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 3500);
}

async function requestBackend(action, data = {}) {
  if (!window.webkit?.messageHandlers?.lab1) {
    if (action === 'export') {
      const blob = new Blob([data.csv], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.name || 'structure-tests.csv';
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      return { saved: true };
    }
    if (window.location.protocol === 'file:') {
      throw new Error('Запустите python3 server.py и откройте адрес, указанный в терминале.');
    }
    let response;
    try {
      response = await fetch('/api', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...data })
      });
    } catch (error) {
      throw new Error('Нет связи с C++ программой. Проверьте, что server.py запущен.');
    }
    const result = await response.json();
    if (!response.ok || result.error) throw new Error(result.error || 'Не удалось выполнить запрос.');
    return result;
  }
  return new Promise((resolve, reject) => {
    const id = ++requestId;
    pendingRequests.set(id, { resolve, reject });
    window.webkit.messageHandlers.lab1.postMessage({ id, action, ...data });
  });
}

window.onNativeMessage = message => {
  const request = pendingRequests.get(message.id);
  if (!request) return;
  pendingRequests.delete(message.id);
  if (message.error) request.reject(new Error(message.error));
  else request.resolve(message);
};

$('#export-button').addEventListener('click', async () => {
  try {
    const response = await requestBackend('export', { csv: structureCSV(), name: 'structure-tests.csv' });
    if (response.saved) toast('CSV сохранён.');
  } catch (error) { toast(error.message); }
});

bindStructureControls();
$('#server-notice').hidden = window.location.protocol !== 'file:' || !!window.webkit?.messageHandlers?.lab1;
