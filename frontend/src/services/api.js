// Backend fetch wrapper — tüm API çağrıları buradan geçer, component'ler doğrudan fetch çağırmaz.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new Error(`Backend'e ulaşılamıyor (${API_BASE_URL}). Sunucu çalışıyor mu?`);
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // yanıt JSON değilse statusText'i kullanmaya devam et
    }
    throw new Error(detail);
  }

  return response.json();
}

export const api = {
  getStatus: () => request('/status'),
  getRealtime: () => request('/realtime'),
  getDtcCodes: () => request('/dtc'),
  explainDtc: (code) => request(`/dtc/${encodeURIComponent(code)}/explain`),
  getHistory: (limit = 100) => request(`/history?limit=${limit}`),
};
