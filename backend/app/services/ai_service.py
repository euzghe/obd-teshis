"""AI açıklama katmanı — Anthropic API ile DTC kodlarını sade Türkçeye çevirir.

Her kod için Claude'a gönderilen istek, `DTCExplanation` şemasına birebir uyan
yapılandırılmış JSON döndürür (output_config.format ile garanti edilir).
Aynı kod için tekrar API çağrısı yapmamak adına basit bir in-memory cache tutulur.
"""
import logging

import anthropic
from pydantic import ValidationError

from app import config
from app.models.schemas import DTCExplanation

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Sen deneyimli bir oto elektrik/motor teşhis uzmanısın. Sana bir OBD-II arıza kodu \
(DTC) verilecek; bunu bir aracın sahibi olan, teknik bilgisi olmayan bir sürücü \
için sade Türkçe açıklayacaksın.

Kurallar:
1. Yanıtın SADECE verilen JSON şemasına uyan geçerli bir JSON nesnesi olmalı. \
Şema dışında hiçbir açıklama, giriş cümlesi, markdown ya da ek metin ekleme.
2. Kodun SAE genel kodu mu (P0xxx, P2xxx, P3xxx gibi standart/jenerik kodlar — \
tüm üreticilerde aynı anlama gelir) yoksa üretici-özel bir kod mu (P1xxx, B1xxx, \
C1xxx, U1xxx gibi üreticiye özgü kodlar) olduğunu ayırt et ve `kod_tipi` alanında belirt. \
Kod üretici-özel ise, üretici/model bilgisi olmadan yorumun daha az kesin olabileceğini \
`guven_notu` alanında kısaca belirt (örn. "Bu kod üretici-özeldir; kesin anlamı marka ve \
modele göre değişebilir, aracınızın servis kitapçığına ya da yetkili servise danışmanız \
önerilir."). SAE genel kodlarda `guven_notu` boş bırakılabilir.
3. Maliyet tahminlerini KESİN rakam olarak değil, her zaman bir aralık ve "yaklaşık" \
ifadesiyle ver (örn. "yaklaşık 800 - 1500 TL"). `not` alanında bu tahminin bölgeye ve \
servise göre değişebileceğini mutlaka belirt.
4. Maliyet tahminlerinde Türkiye'deki güncel piyasa koşullarını (TL cinsinden, Türkiye'deki \
yedek parça ve işçilik fiyat seviyelerini) referans al.
5. `aciliyet` alanı şu dört değerden biri olmalı: "düşük", "orta", "yüksek", \
"acil - sürüşe devam etme". Motor hasarına, güvenliğe ya da emisyon sistemine ciddi \
zarar verebilecek durumlarda "acil - sürüşe devam etme" kullan.
6. `aciklama` alanı 2-3 cümleyi geçmesin, sade ve anlaşılır olsun.
"""

_cache: dict[str, DTCExplanation] = {}


class AIServiceError(Exception):
    """AI açıklama katmanında oluşan, kullanıcıya gösterilebilir hata."""


def _get_client() -> anthropic.Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise AIServiceError(
            "ANTHROPIC_API_KEY tanımlı değil. backend/.env dosyasına gerçek bir "
            "Anthropic API anahtarı ekleyin (bkz. .env.example)."
        )
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def explain_dtc_code(code: str, use_cache: bool = True) -> DTCExplanation:
    """Verilen DTC kodu için AI destekli, sade Türkçe açıklama üretir.

    Aynı kod daha önce açıklanmışsa (use_cache=True ise) tekrar API çağrısı yapmadan
    önbellekten döner.
    """
    normalized_code = code.strip().upper()
    if not normalized_code:
        raise AIServiceError("Geçersiz DTC kodu: boş olamaz.")

    if use_cache and normalized_code in _cache:
        logger.info("DTC açıklaması cache'ten döndü: %s", normalized_code)
        return _cache[normalized_code]

    client = _get_client()

    try:
        response = client.messages.parse(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1500,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"DTC kodu: {normalized_code}\n\nBu kodu yukarıdaki kurallara göre açıkla.",
                }
            ],
            output_format=DTCExplanation,
        )
    except anthropic.APIConnectionError as exc:
        raise AIServiceError(f"Anthropic API'ye bağlanılamadı: {exc}") from exc
    except anthropic.RateLimitError as exc:
        raise AIServiceError("Anthropic API oran sınırına takıldı, lütfen biraz sonra tekrar deneyin.") from exc
    except anthropic.APIStatusError as exc:
        raise AIServiceError(f"Anthropic API hatası ({exc.status_code}): {exc.message}") from exc
    except Exception as exc:  # beklenmeyen SDK/ağ hataları — uygulamayı çökertme
        logger.exception("DTC açıklaması alınırken beklenmeyen hata: %s", normalized_code)
        raise AIServiceError(f"AI açıklaması alınamadı: {exc}") from exc

    if response.stop_reason == "refusal":
        raise AIServiceError(f"Model bu kod için açıklama üretmeyi reddetti: {normalized_code}")

    parsed = response.parsed_output
    if parsed is None:
        raise AIServiceError(
            f"AI yanıtı beklenen JSON formatına uymuyor (kod: {normalized_code}). Lütfen tekrar deneyin."
        )

    try:
        explanation = DTCExplanation.model_validate(parsed)
    except ValidationError as exc:
        raise AIServiceError(
            f"AI yanıtı şemayla eşleşmedi (kod: {normalized_code}): {exc}"
        ) from exc

    _cache[normalized_code] = explanation
    return explanation


def clear_cache() -> None:
    """Test/geliştirme amaçlı: açıklama önbelleğini temizler."""
    _cache.clear()
