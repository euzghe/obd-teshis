"""RPM, sıcaklık, hız ve yakıt verisini okuyan gerçek zamanlı servis."""
from app.models.schemas import RealtimeData
from app.obd import get_connection


def get_realtime_data() -> RealtimeData:
    """Bağlı adaptörden (ya da mock kaynaktan) anlık gösterge verisini döndürür."""
    connection = get_connection()
    return connection.read_realtime()
