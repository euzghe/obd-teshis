"""Adaptörsüz geliştirme için sahte OBD-II veri üreticisi.

Gerçekçi bir sürüş döngüsünü simüle eder: rölanti -> hızlanma -> seyir -> yavaşlama.
OBD_MOCK_MODE=true olduğunda connection.py yerine bu modül kullanılır.
"""
import math
import random
import time
from datetime import datetime, timezone

from app.models.schemas import DTCCode, RealtimeData

# Sabit test DTC kodları: biri genel (SAE), biri üretici-özel örneği
_MOCK_DTC_CODES = [
    DTCCode(code="P0301", raw_description="Cylinder 1 Misfire Detected"),
    DTCCode(code="P0420", raw_description="Catalyst System Efficiency Below Threshold"),
]

_start_time = time.monotonic()


def _drive_cycle_phase(elapsed: float) -> float:
    """0..1 arası, ~60 saniyelik bir döngüde rölanti/hızlanma/seyir/yavaşlama fazını döndürür."""
    cycle = (elapsed % 60.0) / 60.0
    return (math.sin(cycle * 2 * math.pi - math.pi / 2) + 1) / 2


class MockOBDConnection:
    """python-obd bağlantısıyla aynı arayüzü taklit eden sahte kaynak."""

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self._fuel_level = 68.0  # başlangıç yakıt seviyesi (%)

    def is_connected(self) -> bool:
        return True

    def read_realtime(self) -> RealtimeData:
        elapsed = time.monotonic() - _start_time
        phase = _drive_cycle_phase(elapsed)  # 0: rölanti, 1: tam gaz

        rpm = 800 + phase * 3200 + self._rng.uniform(-50, 50)
        speed = max(0.0, phase * 120 + self._rng.uniform(-3, 3))
        coolant_temp = min(95.0, 20 + elapsed * 0.6) + self._rng.uniform(-1, 1)
        fuel_rate = 0.8 + phase * 6.5 + self._rng.uniform(-0.2, 0.2)

        # Yakıt seviyesi zamanla yavaşça düşer
        self._fuel_level = max(0.0, self._fuel_level - fuel_rate / 3600 * 5)

        return RealtimeData(
            rpm=round(rpm, 1),
            coolant_temp_c=round(coolant_temp, 1),
            speed_kmh=round(speed, 1),
            fuel_level_pct=round(self._fuel_level, 1),
            fuel_rate_lph=round(fuel_rate, 2),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def read_dtc_codes(self) -> list[DTCCode]:
        return list(_MOCK_DTC_CODES)

    def clear_dtc_codes(self) -> None:
        _MOCK_DTC_CODES.clear()


if __name__ == "__main__":
    # Basit örnek/test script: mock modülün çalıştığını gösterir.
    conn = MockOBDConnection(seed=42)
    print("Bağlantı durumu:", conn.is_connected())
    print("\nArıza kodları:")
    for dtc in conn.read_dtc_codes():
        print(f"  {dtc.code}: {dtc.raw_description}")

    print("\n5 örnek gerçek zamanlı veri okuması (1sn arayla):")
    for _ in range(5):
        data = conn.read_realtime()
        print(f"  RPM={data.rpm:>7.1f}  Hız={data.speed_kmh:>6.1f} km/h  "
              f"Sıcaklık={data.coolant_temp_c:>5.1f}°C  Yakıt={data.fuel_level_pct:>5.1f}%  "
              f"Tüketim={data.fuel_rate_lph:>5.2f} L/s")
        time.sleep(1)
