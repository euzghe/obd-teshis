// Tüm sayısal gösterimler için tek yardımcı fonksiyon — tr-TR yerel ayarını kullanır:
// binlik ayracı nokta, ondalık ayracı virgül (örn. formatNumber(1906, 0) -> "1.906",
// formatNumber(95.9, 1) -> "95,9"). Component'ler kendi toFixed/toLocaleString çağrısı yapmaz.
export function formatNumber(value, decimals = 0) {
  return new Intl.NumberFormat('tr-TR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}
