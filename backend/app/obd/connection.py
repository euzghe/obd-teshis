"""Gerçek ELM327 (Bluetooth/USB) bağlantısı — python-obd kütüphanesini sarmalar.

Ucuz/eski ELM327 klonlarında bağlantı kopmaları sık görüldüğü için burada
yeniden deneme (retry) ve zaman aşımı mantığı bulunur; hata mesajları
kullanıcı dostu tutulur.
"""
import logging
import time
from typing import Optional

from app.models.schemas import ConnectionState, ConnectionStatus, DTCCode, RealtimeData

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 2
_CONNECT_TIMEOUT_SECONDS = 10


class OBDConnectionError(Exception):
    """Kullanıcıya gösterilecek, anlaşılır bir mesaj taşıyan bağlantı hatası."""


class ELM327Connection:
    """Gerçek bir ELM327 adaptörüne python-obd ile bağlanır.

    `port=None` verilirse python-obd mevcut portları otomatik tarar.
    """

    def __init__(self, port: Optional[str] = None):
        self._port = port
        self._conn = None  # obd.OBD örneği, connect() çağrılana kadar None
        self._status = ConnectionStatus(
            state=ConnectionState.DISCONNECTED, mock_mode=False, adapter_port=port
        )

    @property
    def status(self) -> ConnectionStatus:
        return self._status

    def connect(self) -> ConnectionStatus:
        import obd  # python-obd; sadece gerçek modda gerekli

        self._status = ConnectionStatus(
            state=ConnectionState.CONNECTING, mock_mode=False, adapter_port=self._port
        )

        last_error: Optional[str] = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                connection = obd.OBD(
                    portstr=self._port,
                    timeout=_CONNECT_TIMEOUT_SECONDS,
                )
                if connection.is_connected():
                    self._conn = connection
                    self._status = ConnectionStatus(
                        state=ConnectionState.CONNECTED,
                        mock_mode=False,
                        adapter_port=self._port,
                        message="Adaptöre başarıyla bağlanıldı.",
                    )
                    return self._status
                last_error = "Adaptör bulundu ama araçla iletişim kurulamadı."
            except Exception as exc:  # pragma: no cover - donanıma bağlı
                last_error = str(exc)
                logger.warning("ELM327 bağlantı denemesi %d/%d başarısız: %s", attempt, _MAX_RETRIES, exc)

            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY_SECONDS)

        self._status = ConnectionStatus(
            state=ConnectionState.ERROR,
            mock_mode=False,
            adapter_port=self._port,
            message=(
                "Adaptöre bağlanılamadı. Bluetooth eşleştirmesini, adaptörün araca "
                "takılı ve kontağın açık olduğunu kontrol edin. "
                f"(Son hata: {last_error})"
            ),
        )
        raise OBDConnectionError(self._status.message)

    def is_connected(self) -> bool:
        return self._conn is not None and self._conn.is_connected()

    def read_realtime(self) -> RealtimeData:
        if not self.is_connected():
            raise OBDConnectionError("Araç bağlantısı yok — gerçek zamanlı veri okunamıyor.")
        raise NotImplementedError("python-obd komutları DTC okuma servisi detaylandırılırken eklenecek.")

    def read_dtc_codes(self) -> list[DTCCode]:
        if not self.is_connected():
            raise OBDConnectionError("Araç bağlantısı yok — arıza kodları okunamıyor.")
        raise NotImplementedError("python-obd komutları DTC okuma servisi detaylandırılırken eklenecek.")

    def clear_dtc_codes(self) -> None:
        if not self.is_connected():
            raise OBDConnectionError("Araç bağlantısı yok — arıza kodları silinemiyor.")
        raise NotImplementedError("python-obd komutları DTC okuma servisi detaylandırılırken eklenecek.")
