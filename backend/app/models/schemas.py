"""Pydantic modelleri: bağlantı durumu, gerçek zamanlı veri, DTC ve AI açıklaması."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConnectionState(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"


class ConnectionStatus(BaseModel):
    state: ConnectionState
    mock_mode: bool
    adapter_port: Optional[str] = None
    message: Optional[str] = None


class RealtimeData(BaseModel):
    rpm: float = Field(..., description="Motor devri (RPM)")
    coolant_temp_c: float = Field(..., description="Motor soğutma suyu sıcaklığı (°C)")
    speed_kmh: float = Field(..., description="Araç hızı (km/h)")
    fuel_level_pct: float = Field(..., description="Yakıt seviyesi (%)")
    fuel_rate_lph: Optional[float] = Field(None, description="Anlık yakıt tüketimi (L/saat)")
    timestamp: str = Field(..., description="ISO 8601 zaman damgası")


class DTCCode(BaseModel):
    code: str = Field(..., description="Ham arıza kodu, örn. P0301")
    raw_description: Optional[str] = Field(None, description="Adaptörden gelen ham açıklama (varsa)")


class Aciliyet(str, Enum):
    DUSUK = "düşük"
    ORTA = "orta"
    YUKSEK = "yüksek"
    ACIL = "acil - sürüşe devam etme"


class KodTipi(str, Enum):
    SAE_GENEL = "SAE genel"
    URETICI_OZEL = "üretici özel"


class MaliyetAraligi(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    parca_tl: str = Field(..., description='Parça maliyeti aralığı, örn. "yaklaşık 800 - 1500 TL"')
    iscilik_tl: str = Field(..., description='İşçilik maliyeti aralığı, örn. "yaklaşık 300 - 600 TL"')
    not_: str = Field(
        "Kesin fiyat değildir, bölgeye ve servise göre değişir.",
        alias="not",
    )


class DTCExplanation(BaseModel):
    kod: str = Field(..., description='Arıza kodu, örn. "P0301"')
    baslik: str = Field(..., description="Kısa başlık")
    aciklama: str = Field(..., description="2-3 cümlelik sade Türkçe açıklama")
    olasi_sebepler: list[str] = Field(..., description="Olası sebepler listesi")
    aciliyet: Aciliyet
    tahmini_maliyet_araligi: MaliyetAraligi
    kod_tipi: KodTipi = Field(..., description="SAE genel (P0xxx/P2xxx) mi, üretici özel (P1xxx vb.) mi")
    guven_notu: str = Field(
        "",
        description="Üretici-özel kodlarda modelin daha az kesin olabileceğine dair kısa not; SAE genel kodlarda boş",
    )
