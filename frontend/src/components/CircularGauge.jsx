// Gerçek bir araç göstergesi gibi: ibre + kadran + renkli tehlike bölgeleri (SVG).
// Açı kuralı: 0° = saat 12 yönü, açı arttıkça saat yönünde döner (CSS rotate() ile birebir uyumlu).
const CX = 100;
const CY = 100;
const RADIUS = 78;
const STROKE = 14;
const START_ANGLE = -125;
const END_ANGLE = 125;
const SWEEP = END_ANGLE - START_ANGLE;
const TICK_FRACTIONS = [0, 0.25, 0.5, 0.75, 1];

function angleForRatio(ratio) {
  return START_ANGLE + Math.min(1, Math.max(0, ratio)) * SWEEP;
}

function polarToCartesian(cx, cy, r, angleDeg) {
  const angleRad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.sin(angleRad), y: cy - r * Math.cos(angleRad) };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, startAngle);
  const end = polarToCartesian(cx, cy, r, endAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? 0 : 1;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`;
}

export default function CircularGauge({
  label,
  value,
  unit,
  max,
  min = 0,
  formatValue,
  formatTick = (v) => v,
  zones = [], // [{ from: 0..1, to: 0..1, className: 'zone-warn' | 'zone-danger' }]
  secondaryLabel,
}) {
  const hasValue = typeof value === 'number' && !Number.isNaN(value);
  const ratio = hasValue ? Math.min(1, Math.max(0, (value - min) / (max - min))) : 0;
  const needleAngle = angleForRatio(ratio);

  // Renk tek başına anlam taşımasın diye: değer bir tehlike/uyarı bölgesindeyse
  // metin + ikon içeren bir rozet de gösterilir (bkz. .gauge-status-badge).
  const activeZone = hasValue ? zones.find((zone) => ratio >= zone.from && ratio <= zone.to) : null;
  const isDanger = activeZone?.className.includes('danger');
  const statusBadge = activeZone ? { label: isDanger ? 'Tehlike' : 'Uyarı', icon: isDanger ? '⛔' : '⚠' } : null;

  return (
    <div className="gauge-card">
      <div className="gauge-label">{label}</div>

      {statusBadge && (
        <span className={`gauge-status-badge ${activeZone.className}`}>
          <span aria-hidden="true">{statusBadge.icon}</span> {statusBadge.label}
        </span>
      )}

      <svg viewBox="0 0 200 165" className="gauge-svg" role="img" aria-label={`${label}: ${hasValue ? formatValue(value) : 'veri yok'} ${unit}`}>
        <path d={describeArc(CX, CY, RADIUS, START_ANGLE, END_ANGLE)} className="gauge-track" strokeWidth={STROKE} fill="none" />

        {zones.map((zone) => (
          <path
            key={`${zone.from}-${zone.to}`}
            d={describeArc(CX, CY, RADIUS, angleForRatio(zone.from), angleForRatio(zone.to))}
            className={`gauge-zone ${zone.className}`}
            strokeWidth={STROKE}
            fill="none"
          />
        ))}

        {TICK_FRACTIONS.map((f) => {
          const angle = angleForRatio(f);
          const inner = polarToCartesian(CX, CY, RADIUS - STROKE / 2 - 3, angle);
          const outer = polarToCartesian(CX, CY, RADIUS + STROKE / 2 + 5, angle);
          return <line key={f} x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y} className="gauge-tick" />;
        })}

        <text x={polarToCartesian(CX, CY, RADIUS + 24, angleForRatio(0)).x} y={polarToCartesian(CX, CY, RADIUS + 24, angleForRatio(0)).y} className="gauge-tick-label" textAnchor="middle">
          {formatTick(min)}
        </text>
        <text x={polarToCartesian(CX, CY, RADIUS + 24, angleForRatio(1)).x} y={polarToCartesian(CX, CY, RADIUS + 24, angleForRatio(1)).y} className="gauge-tick-label" textAnchor="middle">
          {formatTick(max)}
        </text>

        <g className="gauge-needle-group" style={{ transform: `rotate(${needleAngle}deg)`, transformOrigin: `${CX}px ${CY}px` }}>
          <line x1={CX} y1={CY} x2={CX} y2={CY - (RADIUS - STROKE)} className="gauge-needle" />
        </g>
        <circle cx={CX} cy={CY} r="6" className="gauge-pivot" />
      </svg>

      <div className="gauge-value">
        <span className="gauge-number">{hasValue ? formatValue(value) : '—'}</span>
        <span className="gauge-unit">{unit}</span>
      </div>
      {secondaryLabel && <div className="gauge-secondary">{secondaryLabel}</div>}
    </div>
  );
}
