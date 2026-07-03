"""Geçmiş veri kaydı — gerçek zamanlı verileri SQLite'a periyodik kaydeder, trend sorguları sunar.

Bu servis henüz iskelet aşamasındadır. Detaylandırma ileride yapılacak:
- SQLite şeması (data/history.db, DATABASE_PATH üzerinden)
- Periyodik kayıt görevi (RPM, sıcaklık, hız, yakıt)
- Zaman aralığına göre trend sorgusu
"""
from app.models.schemas import RealtimeData


def record_snapshot(data: RealtimeData) -> None:
    """Anlık gösterge verisini geçmiş kayıtlara ekler.

    TODO: SQLite entegrasyonu ileride eklenecek.
    """
    raise NotImplementedError("Geçmiş veri servisi henüz detaylandırılmadı.")


def get_history(limit: int = 100) -> list[RealtimeData]:
    """Son kaydedilen gösterge verilerini döndürür.

    TODO: SQLite entegrasyonu ileride eklenecek.
    """
    raise NotImplementedError("Geçmiş veri servisi henüz detaylandırılmadı.")
