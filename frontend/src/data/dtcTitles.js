// Sık görülen DTC kodları için statik Türkçe başlık haritası.
// Kart kapalıyken (AI açıklaması henüz çekilmeden) İngilizce ham açıklamanın yanında
// gösterilir; her açılışta AI'ya sormak yerine anlık ve ücretsiz bir önizleme sağlar.
// Bilinmeyen kodlarda sadece ham açıklama (varsa) gösterilir — kart açıldığında
// gerçek AI açıklaması (`baslik`) zaten Türkçe geliyor.
export const KNOWN_DTC_TITLES = {
  P0301: 'Silindir 1 Ateşleme Hatası',
  P0420: 'Katalitik Konvertör Verimlilik Sorunu',
};
