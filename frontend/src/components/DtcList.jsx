import { useEffect, useState } from 'react';
import { api } from '../services/api';
import DtcCard from './DtcCard';

export default function DtcList() {
  const [codes, setCodes] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api
      .getDtcCodes()
      .then((result) => {
        if (!cancelled) setCodes(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="dtc-list" aria-label="Arıza kodları">
      <h2 className="section-title">Arıza Kodları</h2>

      {error && (
        <p className="section-error" role="alert">
          Arıza kodları alınamadı: {error.message}
        </p>
      )}

      {!error && codes === null && (
        <div className="dtc-skeleton" aria-busy="true">
          <div className="skeleton-line" />
          <div className="skeleton-line skeleton-line-short" />
        </div>
      )}

      {codes !== null && codes.length === 0 && <p className="dtc-list-empty">Kayıtlı arıza kodu yok.</p>}

      {codes && codes.length > 0 && (
        <div className="dtc-cards">
          {codes.map((dtc) => (
            <DtcCard key={dtc.code} code={dtc.code} rawDescription={dtc.raw_description} />
          ))}
        </div>
      )}
    </section>
  );
}
