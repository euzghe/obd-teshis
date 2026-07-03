"""Arıza kodu (DTC) okuma servisi."""
from app.models.schemas import DTCCode
from app.obd import get_connection


def get_dtc_codes() -> list[DTCCode]:
    """Bağlı adaptörden (ya da mock kaynaktan) ham arıza kodu listesini döndürür."""
    connection = get_connection()
    return connection.read_dtc_codes()


def clear_dtc_codes() -> None:
    """Araçtaki arıza kodlarını temizler."""
    connection = get_connection()
    connection.clear_dtc_codes()
