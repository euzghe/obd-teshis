"""OBD bağlantı fabrikası: OBD_MOCK_MODE ayarına göre mock ya da gerçek bağlantı döndürür."""
from typing import Union

from app import config
from app.obd.connection import ELM327Connection
from app.obd.mock import MockOBDConnection

_connection: Union[ELM327Connection, MockOBDConnection, None] = None


def get_connection() -> Union[ELM327Connection, MockOBDConnection]:
    """Uygulama genelinde tek bir bağlantı örneği (singleton) döndürür."""
    global _connection
    if _connection is None:
        if config.OBD_MOCK_MODE:
            _connection = MockOBDConnection()
        else:
            _connection = ELM327Connection(port=config.OBD_ADAPTER_PORT)
            _connection.connect()
    return _connection


def reset_connection() -> None:
    """Test/geliştirme amaçlı: mevcut bağlantı örneğini sıfırlar."""
    global _connection
    _connection = None
