import { useEffect, useRef, useState } from 'react';
import { api } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import { formatNumber } from '../utils/formatNumber';
import CircularGauge from './CircularGauge';

const REALTIME_POLL_MS = 1500;
const ANNOUNCE_INTERVAL_MS = 4000; // ekran okuyucuya her pollingde değil, ~4 saniyede bir duyur

const MAX_RPM = 7000;
const MAX_TEMP_C = 130;
const MAX_SPEED_KMH = 220;

export default function LiveGauges() {
  const { data, error } = usePolling(() => api.getRealtime(), REALTIME_POLL_MS);
  const [announcement, setAnnouncement] = useState('');
  const lastAnnouncedAt = useRef(0);

  useEffect(() => {
    if (!data) return;
    const now = Date.now();
    if (now - lastAnnouncedAt.current < ANNOUNCE_INTERVAL_MS) return;
    lastAnnouncedAt.current = now;
    setAnnouncement(
      `Motor devri ${formatNumber(data.rpm, 0)} rpm, motor sıcaklığı ${formatNumber(data.coolant_temp_c, 1)} derece, ` +
        `hız ${formatNumber(data.speed_kmh, 0)} kilometre saat, yakıt seviyesi yüzde ${formatNumber(data.fuel_level_pct, 1)}.`
    );
  }, [data]);

  return (
    <section className="live-gauges" aria-label="Canlı gösterge paneli">
      {/* Görsel olarak gizli; ekran okuyucular için throttle'lı özet duyuru */}
      <p className="sr-only" aria-live="polite" aria-atomic="true">
        {announcement}
      </p>

      {error && (
        <p className="section-error" role="alert">
          Gerçek zamanlı veri alınamıyor: {error.message}
        </p>
      )}
      <div className="gauge-grid">
        <CircularGauge
          label="Motor Devri"
          value={data?.rpm}
          unit="rpm"
          max={MAX_RPM}
          formatValue={(v) => formatNumber(v, 0)}
          formatTick={(v) => (v >= 1000 ? `${v / 1000}k` : v)}
          zones={[
            { from: 0.65, to: 0.85, className: 'zone-warn' },
            { from: 0.85, to: 1, className: 'zone-danger' },
          ]}
        />
        <CircularGauge
          label="Motor Sıcaklığı"
          value={data?.coolant_temp_c}
          unit="°C"
          max={MAX_TEMP_C}
          formatValue={(v) => formatNumber(v, 1)}
          zones={[
            { from: 0.6, to: 0.8, className: 'zone-warn' },
            { from: 0.8, to: 1, className: 'zone-danger' },
          ]}
        />
        <CircularGauge
          label="Hız"
          value={data?.speed_kmh}
          unit="km/s"
          max={MAX_SPEED_KMH}
          formatValue={(v) => formatNumber(v, 0)}
          zones={[]}
        />
        <CircularGauge
          label="Yakıt Seviyesi"
          value={data?.fuel_level_pct}
          unit="%"
          max={100}
          formatValue={(v) => formatNumber(v, 1)}
          formatTick={(v) => (v === 0 ? 'E' : v === 100 ? 'F' : v)}
          secondaryLabel={
            typeof data?.fuel_rate_lph === 'number' ? `Tüketim: ${formatNumber(data.fuel_rate_lph, 1)} L/sa` : null
          }
          zones={[
            { from: 0, to: 0.15, className: 'zone-danger' },
            { from: 0.15, to: 0.3, className: 'zone-warn' },
          ]}
        />
      </div>
    </section>
  );
}
