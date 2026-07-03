"""FastAPI uç noktaları: /status, /dtc, /dtc/{code}/explain, /realtime, /history."""
from fastapi import APIRouter, HTTPException

from app import config
from app.models.schemas import ConnectionStatus, DTCCode, DTCExplanation, RealtimeData
from app.obd import get_connection
from app.services import ai_service, dtc_service, history_service, realtime_service

router = APIRouter()


@router.get("/status", response_model=ConnectionStatus)
def get_status() -> ConnectionStatus:
    """Adaptör bağlantı durumunu döndürür (bağlı / bağlantı yok / hata)."""
    connection = get_connection()
    if config.OBD_MOCK_MODE:
        return ConnectionStatus(
            state="connected",
            mock_mode=True,
            message="Mock mod aktif — gerçek adaptör kullanılmıyor.",
        )
    return connection.status


@router.get("/dtc", response_model=list[DTCCode])
def get_dtc_codes() -> list[DTCCode]:
    """Araçtaki ham arıza kodu listesini döndürür."""
    try:
        return dtc_service.get_dtc_codes()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/dtc/{code}/explain", response_model=DTCExplanation)
def explain_dtc_code(code: str) -> DTCExplanation:
    """Belirtilen DTC kodu için AI destekli sade Türkçe açıklama döndürür."""
    try:
        return ai_service.explain_dtc_code(code)
    except ai_service.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/realtime", response_model=RealtimeData)
def get_realtime() -> RealtimeData:
    """Anlık RPM, sıcaklık, hız ve yakıt verisini döndürür."""
    try:
        return realtime_service.get_realtime_data()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/history", response_model=list[RealtimeData])
def get_history(limit: int = 100) -> list[RealtimeData]:
    """Geçmişe kaydedilmiş gösterge verilerini döndürür."""
    try:
        return history_service.get_history(limit=limit)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
