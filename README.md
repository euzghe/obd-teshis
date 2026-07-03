# OBD-II Akıllı Araç Teşhis Asistanı

ELM327 Bluetooth/WiFi adaptör üzerinden araç arıza kodlarını (DTC) okuyup Claude (Anthropic API) ile sade Türkçe açıklamaya çeviren, motor RPM/sıcaklık/hız/yakıt verisini gerçek zamanlı gösteren bir uygulama.

Her DTC kodu için: sade açıklama, olası sebepler, aciliyet seviyesi ve "yaklaşık" ifadesiyle sunulan tahmini TL maliyet aralığı üretilir. SAE genel kodları (P0xxx) ile üretici-özel kodlar (P1xxx vb.) ayırt edilir.

## Ekran görüntüsü

Kokpit temalı, koyu zeminli dashboard — dairesel gösterge (ibre + kadran), bağlantı durumu rozeti, genişletilebilir DTC kartları.

## Teknoloji Yığını

- **Backend:** Python 3.11+, FastAPI, [`obd`](https://pypi.org/project/obd/) (python-OBD), pyserial, Anthropic SDK
- **Frontend:** React + Vite, plain CSS (framework yok)
- **Veri:** Şimdilik gerçek zamanlı veri için mock üretici; geçmiş/trend kaydı için SQLite planlanıyor

## Klasör Yapısı

```
obd-teshis/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI giriş noktası
│   │   ├── config.py          # .env okuma
│   │   ├── obd/
│   │   │   ├── connection.py  # Gerçek ELM327 bağlantısı (retry/timeout'lu)
│   │   │   └── mock.py        # Adaptörsüz geliştirme için sahte veri üreticisi
│   │   ├── services/
│   │   │   ├── dtc_service.py
│   │   │   ├── realtime_service.py
│   │   │   ├── ai_service.py      # Anthropic API ile DTC açıklama + cache
│   │   │   └── history_service.py # (stub — henüz detaylandırılmadı)
│   │   ├── models/schemas.py  # Pydantic modelleri
│   │   └── api/routes.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── src/
        ├── components/  # StatusBadge, CircularGauge, DtcList, DtcCard
        ├── services/api.js
        ├── hooks/usePolling.js
        └── utils/formatNumber.js
```

## Kurulum

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY'i ekle (bkz. aşağı)
uvicorn app.main:app --reload
```

API varsayılan olarak `http://localhost:8000` üzerinde çalışır.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Varsayılan olarak `http://localhost:5173` (dolu ise Vite otomatik başka porta geçer) üzerinde açılır.

## Ortam Değişkenleri

**`backend/.env`**

| Değişken | Açıklama |
|---|---|
| `OBD_MOCK_MODE` | `true` ise gerçek adaptör yerine sahte veri kullanılır (adaptörünüz yoksa `true` bırakın) |
| `OBD_ADAPTER_PORT` | Gerçek modda kullanılacak seri port (boşsa otomatik taranır) |
| `ANTHROPIC_API_KEY` | AI açıklama katmanı için gerekli — [console.anthropic.com](https://console.anthropic.com) üzerinden alınır |
| `ANTHROPIC_MODEL` | Varsayılan `claude-opus-4-8` |
| `DATABASE_PATH` | Geçmiş veri için SQLite dosya yolu |
| `CORS_ORIGINS` | Frontend'in çalıştığı origin(ler), virgülle ayrılmış |

**`frontend/.env`**

| Değişken | Açıklama |
|---|---|
| `VITE_API_URL` | Backend'in adresi (örn. `http://localhost:8000`) |

## Durum

- ✅ Mock OBD veri üretici + gerçek zamanlı gösterge paneli
- ✅ DTC listesi + AI açıklama katmanı (Anthropic API, yapılandırılmış JSON, cache'li)
- ✅ Erişilebilirlik: `aria-live` duyuruları, `prefers-reduced-motion` desteği, renk-tek-başına-kodlama yok
- ⏳ Gerçek ELM327 bağlantısı — `connection.py` iskeleti hazır, python-obd komutları henüz eklenmedi
- ⏳ Geçmiş veri kaydı / trend grafiği (SQLite) — henüz başlanmadı
- ⏳ Bakım takvimi hatırlatması, PDF rapor çıktısı — planlanan ileri özellikler

## Dikkat

- Tahmini maliyet aralıkları kesin fiyat değildir; bölgeye ve servise göre değişir.
- Üretici-özel (P1xxx vb.) kodlarda AI açıklaması daha az kesin olabilir — kart üzerinde bu durum ayrıca belirtilir.
- Anthropic API anahtarınızı asla koda gömmeyin; `.env` dosyaları `.gitignore` ile hariç tutulmuştur.
