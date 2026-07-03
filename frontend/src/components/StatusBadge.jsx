import { api } from '../services/api';
import { usePolling } from '../hooks/usePolling';

const STATUS_POLL_MS = 5000;

const STATE_CONFIG = {
  connected: { label: 'Bağlı', className: 'status-ok' },
  connecting: { label: 'Bağlanıyor…', className: 'status-warn' },
  disconnected: { label: 'Bağlantı yok', className: 'status-neutral' },
  error: { label: 'Hata', className: 'status-critical' },
};

export default function StatusBadge() {
  const { data: status, error } = usePolling(() => api.getStatus(), STATUS_POLL_MS);

  if (!status) {
    return (
      <span className={`status-badge ${error ? 'status-critical' : 'status-neutral'}`}>
        <span className="status-dot" />
        {error ? "Backend'e ulaşılamıyor" : 'Kontrol ediliyor…'}
      </span>
    );
  }

  const config = STATE_CONFIG[status.state] || STATE_CONFIG.disconnected;
  const label = status.state === 'connected' && status.mock_mode ? 'Bağlı (mock mod)' : config.label;

  return (
    <span className={`status-badge ${config.className}`} title={status.message || undefined}>
      <span className="status-dot" />
      {label}
    </span>
  );
}
