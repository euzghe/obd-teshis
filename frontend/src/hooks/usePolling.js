import { useEffect, useRef, useState } from 'react';

// Verilen fetch fonksiyonunu belirli aralıklarla çağırır; önceki istek bitmeden
// yenisini başlatmaz (setTimeout zinciri) ve unmount olunca temizlenir.
export function usePolling(fetchFn, intervalMs) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const fetchFnRef = useRef(fetchFn);
  fetchFnRef.current = fetchFn;

  useEffect(() => {
    let cancelled = false;
    let timeoutId;

    async function tick() {
      try {
        const result = await fetchFnRef.current();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) {
          timeoutId = setTimeout(tick, intervalMs);
        }
      }
    }

    tick();

    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [intervalMs]);

  return { data, error };
}
