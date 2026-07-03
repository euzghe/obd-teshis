import { useRef, useState } from 'react';
import { api } from '../services/api';
import { KNOWN_DTC_TITLES } from '../data/dtcTitles';

// `key` kart ve rozet için ayrı CSS sınıf önekleri üretir (dtc-card--{key} / urgency-badge--{key}),
// böylece ikisi aynı bare class'ı paylaşıp istemeden birbirini etkilemez.
const URGENCY_CONFIG = {
  düşük: { key: 'low', label: 'Düşük' },
  orta: { key: 'medium', label: 'Orta' },
  yüksek: { key: 'high', label: 'Yüksek' },
  'acil - sürüşe devam etme': { key: 'critical', label: 'Acil — Sürüşe Devam Etme' },
};

// <details>/<summary> native olarak klavye ile açılıp kapanabilir (Enter/Space) ve
// erişilebilirlik için ekstra ARIA gerektirmez.
export default function DtcCard({ code, rawDescription }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fetchedRef = useRef(false);

  async function handleToggle(event) {
    if (!event.target.open || fetchedRef.current) return;
    fetchedRef.current = true;
    setLoading(true);
    setError(null);
    try {
      const result = await api.explainDtc(code);
      setExplanation(result);
    } catch (err) {
      setError(err);
      fetchedRef.current = false; // hata durumunda bir sonraki açılışta tekrar denensin
    } finally {
      setLoading(false);
    }
  }

  const urgency = explanation ? URGENCY_CONFIG[explanation.aciliyet] : null;
  const knownTitle = KNOWN_DTC_TITLES[code.toUpperCase()];

  return (
    <details className={`dtc-card ${urgency ? `dtc-card--${urgency.key}` : ''}`} onToggle={handleToggle}>
      <summary className="dtc-card-summary">
        <span className="dtc-code">{code}</span>
        <div className="dtc-title-group">
          {explanation ? (
            <span className="dtc-title">{explanation.baslik}</span>
          ) : (
            <>
              <span className="dtc-title">{knownTitle || rawDescription || 'Detaylar için tıklayın'}</span>
              {knownTitle && rawDescription && <span className="dtc-title-secondary">{rawDescription}</span>}
            </>
          )}
        </div>
        {urgency && <span className={`urgency-badge urgency-badge--${urgency.key}`}>{urgency.label}</span>}
      </summary>

      <div className="dtc-card-body">
        {loading && (
          <div className="dtc-skeleton" aria-busy="true">
            <div className="skeleton-line" />
            <div className="skeleton-line skeleton-line-short" />
            <div className="skeleton-line" />
          </div>
        )}

        {error && (
          <p className="dtc-card-error" role="alert">
            AI açıklaması alınamadı: {error.message}
          </p>
        )}

        {explanation && (
          <>
            <p className="dtc-explanation">{explanation.aciklama}</p>

            <div className="dtc-section">
              <h4>Olası Sebepler</h4>
              <ul>
                {explanation.olasi_sebepler.map((sebep) => (
                  <li key={sebep}>{sebep}</li>
                ))}
              </ul>
            </div>

            <div className="dtc-section dtc-cost">
              <h4>Tahmini Maliyet</h4>
              <p>Parça: {explanation.tahmini_maliyet_araligi.parca_tl}</p>
              <p>İşçilik: {explanation.tahmini_maliyet_araligi.iscilik_tl}</p>
              <p className="dtc-cost-note">{explanation.tahmini_maliyet_araligi.not}</p>
            </div>

            <p className="dtc-kod-tipi">
              Kod tipi: <strong>{explanation.kod_tipi}</strong>
            </p>

            {explanation.guven_notu && <p className="dtc-guven-notu">{explanation.guven_notu}</p>}
          </>
        )}
      </div>
    </details>
  );
}
