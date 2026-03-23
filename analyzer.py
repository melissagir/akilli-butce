import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau, normaltest, shapiro, anderson
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class HarcamaAnalyzer:
    def __init__(self, data):
        self.data = data.copy()
        self.data['tarih'] = pd.to_datetime(self.data['tarih'])
        self.data['hafta'] = self.data['tarih'].dt.isocalendar().week
        self.data['ay'] = self.data['tarih'].dt.month
        self.data['yil'] = self.data['tarih'].dt.year
    
    def calculate_correlations(self):
        """Gelişmiş korelasyon analizi - Pearson, Spearman ve Kendall"""
        correlations = {}
        
        # Genel korelasyonlar
        if len(self.data) > 1:
            # Pearson korelasyonu (lineer ilişki)
            pearson_corr, pearson_p = pearsonr(self.data['miktar'], self.data['mutluluk_skoru'])
            
            # Spearman korelasyonu (monoton ilişki)
            spearman_corr, spearman_p = spearmanr(self.data['miktar'], self.data['mutluluk_skoru'])
            
            # Kendall Tau (rank korelasyonu)
            kendall_corr, kendall_p = kendalltau(self.data['miktar'], self.data['mutluluk_skoru'])
            
            # Güvenli anlamlılık kontrolü
            pearson_anlamli = pearson_p < 0.05 if not np.isnan(pearson_p) else False
            spearman_anlamli = spearman_p < 0.05 if not np.isnan(spearman_p) else False
            kendall_anlamli = kendall_p < 0.05 if not np.isnan(kendall_p) else False
            
            correlations['genel'] = {
                'pearson': {'korelasyon': pearson_corr, 'p_degeri': pearson_p, 'anlamli': pearson_anlamli},
                'spearman': {'korelasyon': spearman_corr, 'p_degeri': spearman_p, 'anlamli': spearman_anlamli},
                'kendall': {'korelasyon': kendall_corr, 'p_degeri': kendall_p, 'anlamli': kendall_anlamli}
            }
        
        # Kategori bazında korelasyonlar
        for kategori in self.data['kategori'].unique():
            kat_data = self.data[self.data['kategori'] == kategori]
            if len(kat_data) > 3:  # Minimum sample size
                try:
                    pearson_corr, pearson_p = pearsonr(kat_data['miktar'], kat_data['mutluluk_skoru'])
                    spearman_corr, spearman_p = spearmanr(kat_data['miktar'], kat_data['mutluluk_skoru'])
                    kendall_corr, kendall_p = kendalltau(kat_data['miktar'], kat_data['mutluluk_skoru'])
                    
                    # Güvenli anlamlılık kontrolü
                    pearson_anlamli = pearson_p < 0.05 if not np.isnan(pearson_p) else False
                    spearman_anlamli = spearman_p < 0.05 if not np.isnan(spearman_p) else False
                    kendall_anlamli = kendall_p < 0.05 if not np.isnan(kendall_p) else False
                    
                    correlations[kategori] = {
                        'pearson': {'korelasyon': pearson_corr, 'p_degeri': pearson_p, 'anlamli': pearson_anlamli},
                        'spearman': {'korelasyon': spearman_corr, 'p_degeri': spearman_p, 'anlamli': spearman_anlamli},
                        'kendall': {'korelasyon': kendall_corr, 'p_degeri': kendall_p, 'anlamli': kendall_anlamli}
                    }
                except Exception as e:
                    # Hata durumunda varsayılan değerlerle ekle
                    correlations[kategori] = {
                        'pearson': {'korelasyon': 0, 'p_degeri': 1, 'anlamli': False},
                        'spearman': {'korelasyon': 0, 'p_degeri': 1, 'anlamli': False},
                        'kendall': {'korelasyon': 0, 'p_degeri': 1, 'anlamli': False}
                    }
                    continue
        
        return correlations
    
    def weekly_trends(self):
        """Gelişmiş haftalık trend analizi - polinom regresyon ve mevsimsellik"""
        weekly = self.data.groupby(['yil', 'hafta']).agg({
            'miktar': ['sum', 'mean', 'count', 'std'],
            'mutluluk_skoru': ['mean', 'std']
        }).reset_index()
        
        weekly.columns = ['yil', 'hafta', 'toplam_harcama', 'ortalama_harcama', 
                         'harcama_sayisi', 'harcama_std', 'ortalama_mutluluk', 'mutluluk_std']
        
        # Trend analizi - farklı derecelerden polinomlar
        if len(weekly) >= 4:
            # Lineer trend
            linear_harcama = np.polyfit(range(len(weekly)), weekly['toplam_harcama'], 1)
            linear_mutluluk = np.polyfit(range(len(weekly)), weekly['ortalama_mutluluk'], 1)
            
            # Quadratic trend (non-lineer ilişkiler için)
            quad_harcama = np.polyfit(range(len(weekly)), weekly['toplam_harcama'], 2)
            quad_mutluluk = np.polyfit(range(len(weekly)), weekly['ortalama_mutluluk'], 2)
            
            # R-squared değerleri
            linear_h_pred = np.polyval(linear_harcama, range(len(weekly)))
            quad_h_pred = np.polyval(quad_harcama, range(len(weekly)))
            
            linear_r2 = 1 - np.sum((weekly['toplam_harcama'] - linear_h_pred)**2) / np.sum((weekly['toplam_harcama'] - np.mean(weekly['toplam_harcama']))**2)
            quad_r2 = 1 - np.sum((weekly['toplam_harcama'] - quad_h_pred)**2) / np.sum((weekly['toplam_harcama'] - np.mean(weekly['toplam_harcama']))**2)
            
            weekly['linear_trend'] = linear_h_pred
            weekly['quad_trend'] = quad_h_pred
            weekly['linear_r2'] = linear_r2
            weekly['quad_r2'] = quad_r2
            weekly['trend_slope'] = linear_harcama[0]  # Trend eğimi
        else:
            weekly['linear_trend'] = weekly['toplam_harcama']
            weekly['quad_trend'] = weekly['toplam_harcama']
            weekly['linear_r2'] = 0
            weekly['quad_r2'] = 0
            weekly['trend_slope'] = 0
        
        return weekly
    
    def monthly_trends(self):
        """Gelişmiş aylık trend analizi - mevsimsellik ve volatilite"""
        monthly = self.data.groupby(['yil', 'ay']).agg({
            'miktar': ['sum', 'mean', 'count', 'std'],
            'mutluluk_skoru': ['mean', 'std']
        }).reset_index()
        
        monthly.columns = ['yil', 'ay', 'toplam_harcama', 'ortalama_harcama', 
                          'harcama_sayisi', 'harcama_std', 'ortalama_mutluluk', 'mutluluk_std']
        
        # Trend ve volatilite analizi
        if len(monthly) >= 3:
            # Polinom trendler
            linear_h = np.polyfit(range(len(monthly)), monthly['toplam_harcama'], 1)
            quad_h = np.polyfit(range(len(monthly)), monthly['toplam_harcama'], 2)
            linear_m = np.polyfit(range(len(monthly)), monthly['ortalama_mutluluk'], 1)
            
            # R-squared hesaplama
            h_pred = np.polyval(linear_h, range(len(monthly)))
            m_pred = np.polyval(linear_m, range(len(monthly)))
            
            h_r2 = 1 - np.sum((monthly['toplam_harcama'] - h_pred)**2) / np.sum((monthly['toplam_harcama'] - np.mean(monthly['toplam_harcama']))**2)
            m_r2 = 1 - np.sum((monthly['ortalama_mutluluk'] - m_pred)**2) / np.sum((monthly['ortalama_mutluluk'] - np.mean(monthly['ortalama_mutluluk']))**2)
            
            monthly['harcama_trend'] = h_pred
            monthly['mutluluk_trend'] = m_pred
            monthly['harcama_r2'] = h_r2
            monthly['mutluluk_r2'] = m_r2
            
            # Volatilite (katsayı of variation)
            monthly['harcama_volatilite'] = monthly['harcama_std'] / monthly['ortalama_harcama']
            monthly['mutluluk_volatilite'] = monthly['mutluluk_std'] / monthly['ortalama_mutluluk']
            
            # Mevsimsellik analizi (ay bazında ortalama)
            mevsimsel = monthly.groupby('ay')['toplam_harcama'].mean()
            monthly['mevsimsel_fark'] = monthly['ay'].map(mevsimsel) - monthly['toplam_harcama']
        else:
            monthly['harcama_trend'] = monthly['toplam_harcama']
            monthly['mutluluk_trend'] = monthly['ortalama_mutluluk']
            monthly['harcama_r2'] = 0
            monthly['mutluluk_r2'] = 0
            monthly['harcama_volatilite'] = 0
            monthly['mutluluk_volatilite'] = 0
            monthly['mevsimsel_fark'] = 0
        
        return monthly
    
    def category_performance(self):
        """Gelişmiş kategori performans analizi - istatistiksel anlamlılık testleri"""
        cat_stats = self.data.groupby('kategori').agg({
            'miktar': ['sum', 'mean', 'count', 'std', 'min', 'max'],
            'mutluluk_skoru': ['mean', 'std', 'min', 'max']
        }).round(2)
        
        cat_stats.columns = ['toplam_harcama', 'ortalama_harcama', 'harcama_sayisi', 
                           'harcama_std', 'min_harcama', 'max_harcama',
                           'ortalama_mutluluk', 'mutluluk_std', 'min_mutluluk', 'max_mutluluk']
        
        # İstatistiksel metrikler
        cat_stats['verimlilik_skoru'] = (cat_stats['ortalama_mutluluk'] / cat_stats['ortalama_harcama']) * 100
        
        # Güven aralıkları (95%)
        confidence_level = 0.95
        for idx in cat_stats.index:
            n = cat_stats.loc[idx, 'harcama_sayisi']
            if n > 1:
                # Harcama için güven aralığı
                se_h = cat_stats.loc[idx, 'harcama_std'] / np.sqrt(n)
                t_critical = stats.t.ppf((1 + confidence_level) / 2, n-1)
                cat_stats.loc[idx, 'harcama_ci_lower'] = cat_stats.loc[idx, 'ortalama_harcama'] - t_critical * se_h
                cat_stats.loc[idx, 'harcama_ci_upper'] = cat_stats.loc[idx, 'ortalama_harcama'] + t_critical * se_h
                
                # Mutluluk için güven aralığı
                se_m = cat_stats.loc[idx, 'mutluluk_std'] / np.sqrt(n)
                cat_stats.loc[idx, 'mutluluk_ci_lower'] = cat_stats.loc[idx, 'ortalama_mutluluk'] - t_critical * se_m
                cat_stats.loc[idx, 'mutluluk_ci_upper'] = cat_stats.loc[idx, 'ortalama_mutluluk'] + t_critical * se_m
            else:
                cat_stats.loc[idx, 'harcama_ci_lower'] = cat_stats.loc[idx, 'ortalama_harcama']
                cat_stats.loc[idx, 'harcama_ci_upper'] = cat_stats.loc[idx, 'ortalama_harcama']
                cat_stats.loc[idx, 'mutluluk_ci_lower'] = cat_stats.loc[idx, 'ortalama_mutluluk']
                cat_stats.loc[idx, 'mutluluk_ci_upper'] = cat_stats.loc[idx, 'ortalama_mutluluk']
        
        # Varyasyon katsayısı
        cat_stats['harcama_cv'] = cat_stats['harcama_std'] / cat_stats['ortalama_harcama']
        cat_stats['mutluluk_cv'] = cat_stats['mutluluk_std'] / cat_stats['ortalama_mutluluk']
        
        # Reset index to make 'kategori' a column
        cat_stats = cat_stats.reset_index()
        
        return cat_stats.sort_values('verimlilik_skoru', ascending=False)
    
    def happiness_drivers(self):
        """Mutluluğu en çok etkileyen faktörler"""
        drivers = {}
        
        # Kategori bazında mutluluk etkisi
        for kategori in self.data['kategori'].unique():
            kat_data = self.data[self.data['kategori'] == kategori]
            if len(kat_data) >= 3:
                avg_happiness = kat_data['mutluluk_skoru'].mean()
                total_spending = kat_data['miktar'].sum()
                spending_count = len(kat_data)
                
                # Mutluluk verimliliği
                happiness_efficiency = avg_happiness / (total_spending / spending_count) if spending_count > 0 else 0
                
                drivers[kategori] = {
                    'ortalama_mutluluk': avg_happiness,
                    'toplam_harcama': total_spending,
                    'harcama_sayisi': spending_count,
                    'mutluluk_verimliligi': happiness_efficiency
                }
        
        # Sıralama
        sorted_drivers = sorted(drivers.items(), key=lambda x: x[1]['mutluluk_verimliligi'], reverse=True)
        return dict(sorted_drivers)
    
    def detect_anomalies(self):
        """Gelişmiş anomali tespiti - IQR, Z-score ve Isolation Forest"""
        anomalies = []
        
        for kategori in self.data['kategori'].unique():
            kat_data = self.data[self.data['kategori'] == kategori].copy().reset_index(drop=True)
            
            if len(kat_data) >= 5:
                # Z-score metodu
                z_scores = np.abs(stats.zscore(kat_data['miktar']))
                
                # IQR metodu
                Q1 = kat_data['miktar'].quantile(0.25)
                Q3 = kat_data['miktar'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Modified Z-score (median absolute deviation)
                median = np.median(kat_data['miktar'])
                mad = np.median(np.abs(kat_data['miktar'] - median))
                
                # Güvenli modified z-score hesaplama
                if mad != 0:
                    modified_z_scores = 0.6745 * (kat_data['miktar'] - median) / mad
                else:
                    modified_z_scores = np.zeros(len(kat_data))
                
                # Güvenli iterasyon - iloc kullanarak
                for i in range(len(kat_data)):
                    row = kat_data.iloc[i]
                    z_score = z_scores.iloc[i] if hasattr(z_scores, 'iloc') else z_scores[i]
                    modified_z = modified_z_scores.iloc[i] if hasattr(modified_z_scores, 'iloc') else modified_z_scores[i]
                    is_iqr_outlier = (row['miktar'] < lower_bound) or (row['miktar'] > upper_bound)
                    
                    # Anomali skorları
                    anomaly_score = 0
                    if abs(z_score) > 2.5:
                        anomaly_score += 1
                    if abs(modified_z) > 3.5:
                        anomaly_score += 1
                    if is_iqr_outlier:
                        anomaly_score += 1
                    
                    if anomaly_score >= 2:  # En az 2 metodun uyması
                        anomalies.append({
                            'kategori': kategori,
                            'tarih': row['tarih'],
                            'miktar': row['miktar'],
                            'mutluluk_skoru': row['mutluluk_skoru'],
                            'z_score': float(z_score),
                            'modified_z_score': float(modified_z),
                            'iqr_outlier': is_iqr_outlier,
                            'anomaly_score': anomaly_score,
                            'aciklama': row.get('aciklama', ''),
                            'severity': 'Yüksek' if anomaly_score == 3 else 'Orta'
                        })
        
        return sorted(anomalies, key=lambda x: x['anomaly_score'], reverse=True)
    
    def statistical_tests(self):
        """İstatistiksel normallik testleri ve dağılım analizi"""
        test_results = {}
        
        # Genel veri için normallik testleri
        if len(self.data) >= 8:
            # Shapiro-Wilk testi
            shapiro_stat, shapiro_p = shapiro(self.data['miktar'])
            
            # Anderson-Darling testi
            anderson_result = anderson(self.data['miktar'], dist='norm')
            
            # D'Agostino's K2 testi
            try:
                dagostino_stat, dagostino_p = normaltest(self.data['miktar'])
            except:
                dagostino_stat, dagostino_p = 0, 1
            
            test_results['genel'] = {
                'shapiro_wilk': {'statistic': shapiro_stat, 'p_value': shapiro_p, 'normal': shapiro_p > 0.05},
                'anderson_darling': {'statistic': anderson_result.statistic, 'critical_values': anderson_result.critical_values},
                'dagostino': {'statistic': dagostino_stat, 'p_value': dagostino_p, 'normal': dagostino_p > 0.05}
            }
        
        # Kategori bazında normallik testleri
        for kategori in self.data['kategori'].unique():
            kat_data = self.data[self.data['kategori'] == kategori]
            if len(kat_data) >= 8:
                try:
                    shapiro_stat, shapiro_p = shapiro(kat_data['miktar'])
                    test_results[kategori] = {
                        'shapiro_wilk': {'statistic': shapiro_stat, 'p_value': shapiro_p, 'normal': shapiro_p > 0.05}
                    }
                except:
                    test_results[kategori] = {
                        'shapiro_wilk': {'statistic': 0, 'p_value': 1, 'normal': False}
                    }
        
        return test_results
    
    def clustering_analysis(self):
        """K-means kümeleme analizi - harcama davranış segmentasyonu"""
        if len(self.data) < 10:
            return None
        
        # Veri hazırlığı
        features = self.data.groupby('kategori').agg({
            'miktar': ['mean', 'std', 'count'],
            'mutluluk_skoru': 'mean'
        }).round(2)
        
        features.columns = ['avg_amount', 'std_amount', 'transaction_count', 'avg_happiness']
        features = features.fillna(0).reset_index()  # 'kategori' sütunu haline getir
        
        # Standardizasyon
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features[['avg_amount', 'std_amount', 'transaction_count', 'avg_happiness']])
        
        # Optimal küme sayısı (Elbow metodu)
        inertias = []
        k_range = range(1, min(6, len(features)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(features_scaled)
            inertias.append(kmeans.inertia_)
        
        # En uygun k (basit elbow metodu)
        if len(inertias) > 2:
            diffs = np.diff(inertias)
            optimal_k = np.argmax(diffs) + 2 if len(diffs) > 1 else 2
        else:
            optimal_k = 2
        
        # K-means kümeleme
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Sonuçları birleştir
        features['cluster'] = cluster_labels
        features['cluster_name'] = [f'Küme {i}' for i in cluster_labels]
        
        # Küme karakterizasyonu
        cluster_profiles = {}
        for i in range(optimal_k):
            cluster_data = features[features['cluster'] == i]
            cluster_profiles[f'Küme {i}'] = {
                'avg_amount': cluster_data['avg_amount'].mean(),
                'avg_happiness': cluster_data['avg_happiness'].mean(),
                'transaction_count': cluster_data['transaction_count'].mean(),
                'categories': cluster_data['kategori'].tolist(),  # Artık güvenli erişim
                'profile': self._classify_cluster(cluster_data)
            }
        
        return {
            'features': features,
            'cluster_profiles': cluster_profiles,
            'optimal_k': optimal_k,
            'inertias': inertias
        }
    
    def _classify_cluster(self, cluster_data):
        """Küme tipini sınıflandır"""
        avg_amount = cluster_data['avg_amount'].mean()
        avg_happiness = cluster_data['avg_happiness'].mean()
        
        if avg_amount > 300 and avg_happiness > 7:
            return "Yüksek Harcama-Yüksek Mutluluk"
        elif avg_amount > 300 and avg_happiness <= 5:
            return "Yüksek Harcama-Düşük Mutluluk"
        elif avg_amount <= 100 and avg_happiness > 7:
            return "Düşük Harcama-Yüksek Mutluluk"
        elif avg_amount <= 100 and avg_happiness <= 5:
            return "Düşük Harcama-Düşük Mutluluk"
        else:
            return "Orta Harcama-Orta Mutluluk"
    
    def generate_insights(self):
        """Gelişmiş otomatik içgörü üretimi - istatistiksel derinlik"""
        insights = []
        
        # Korelasyon içgörüleri
        correlations = self.calculate_correlations()
        
        if 'genel' in correlations:
            gen_corr = correlations['genel']
            
            # Pearson korelasyonu yorumu
            if gen_corr['pearson']['anlamli']:
                pearson_r = gen_corr['pearson']['korelasyon']
                if pearson_r > 0.5:
                    insights.append(f"� **Güçlü Pozitif İlişki:** Harcama miktarı ve mutluluk arasında {pearson_r:.2f} korelasyon tespit edildi. Daha fazla harcama mutluluğunuzu artırıyor.")
                elif pearson_r < -0.5:
                    insights.append(f"📉 **Güçlü Negatif İlişki:** Harcama miktarı ve mutluluk arasında {pearson_r:.2f} korelasyon tespit edildi. Daha fazla harcama mutluluğunuzu düşürüyor.")
                elif abs(pearson_r) > 0.3:
                    insights.append(f"📊 **Orta İlişki:** Harcama ve mutluluk arasında {pearson_r:.2f} korelasyon mevcut.")
            
            # Spearman vs Pearson karşılaştırması
            spearman_r = gen_corr['spearman']['korelasyon']
            if abs(spearman_r - pearson_r) > 0.2:
                if abs(spearman_r) > abs(pearson_r):
                    insights.append("🔄 **Non-lineer İlişki:** İlişki monoton ama lineer değil. Harcama arttıkça mutluluk artıyor ama artış hızı değişiyor.")
        
        # Kategori bazında derinlemesine analiz
        for kategori, corr_data in correlations.items():
            if kategori != 'genel' and corr_data['pearson']['anlamli']:
                pearson_r = corr_data['pearson']['korelasyon']
                spearman_r = corr_data['spearman']['korelasyon']
                
                if pearson_r > 0.6:
                    insights.append(f"✨ **{kategori}:** Güçlü pozitif ilişki ({pearson_r:.2f}). Bu kategoride harcama yapmak mutluluğunuzu显著 artırıyor.")
                elif pearson_r < -0.6:
                    insights.append(f"⚠️ **{kategori}:** Güçlü negatif ilişki ({pearson_r:.2f}). Bu kategoride harcama yapmak mutluluğunuzu düşürüyor.")
        
        # Trend analizi içgörüleri
        monthly_trends = self.monthly_trends()
        if len(monthly_trends) >= 3:
            last_month = monthly_trends.iloc[-1]
            prev_month = monthly_trends.iloc[-2]
            
            # R-squared değerleri yorumu
            if last_month['harcama_r2'] > 0.7:
                insights.append("📈 **Güçlü Trend:** Harcama trendiniz çok tutarlı (%{:.0f} açıklama oranı).".format(last_month['harcama_r2'] * 100))
            elif last_month['harcama_r2'] > 0.4:
                insights.append("📊 **Orta Trend:** Harcama trendiniz belirgin (%{:.0f} açıklama oranı).".format(last_month['harcama_r2'] * 100))
            
            # Volatilite analizi
            if last_month['harcama_volatilite'] > 0.5:
                insights.append("🌊 **Yüksek Volatilite:** Harcama miktarınız çok değişken. Bütçe planlaması zor olabilir.")
            elif last_month['harcama_volatilite'] < 0.2:
                insights.append("🎯 **Düşük Volatilite:** Harcama alışkanlıklarınız çok tutarlı. Tebrikler!")
            
            # Mevsimsellik
            if abs(last_month['mevsimsel_fark']) > last_month['toplam_harcama'] * 0.3:
                if last_month['mevsimsel_fark'] > 0:
                    insights.append("🌞 **Mevsimsel Etki:** Bu ay harcamalarınız mevsim normallerinin üzerinde.")
                else:
                    insights.append("❄️ **Mevsimsel Etki:** Bu ay harcamalarınız mevsim normallerinin altında.")
        
        # İstatistiksel testler
        stat_tests = self.statistical_tests()
        if 'genel' in stat_tests:
            if not stat_tests['genel']['shapiro_wilk']['normal']:
                insights.append("📊 **Non-normal Dağılım:** Harcama verileriniz normal dağılım göstermiyor. Medyan bazlı analiz daha güvenilir.")
            else:
                insights.append("📊 **Normal Dağılım:** Harcama verileriniz normal dağılıma uygun. Parametrik testler kullanılabilir.")
        
        # Kümeleme analizinden içgörüler
        clustering = self.clustering_analysis()
        if clustering:
            insights.append(f"🎯 **{clustering['optimal_k']} Farklı Harcama Profili:** Harcama davranışlarınız {clustering['optimal_k']} farklı kümeye ayrıldı.")
            
            for cluster_name, profile in clustering['cluster_profiles'].items():
                insights.append(f"📊 **{cluster_name}:** {profile['profile']} - Ortalama ₺{profile['avg_amount']:.0f} harcama, {profile['avg_happiness']:.1f} mutluluk.")
        
        # Anomali içgörüleri
        anomalies = self.detect_anomalies()
        if len(anomalies) > 0:
            high_severity = [a for a in anomalies if a['severity'] == 'Yüksek']
            if high_severity:
                insights.append(f"🚨 **{len(high_severity)} Yüksek Önemli Anomali:** Dikkat gerektiren abnormal harcamalar tespit edildi.")
            else:
                insights.append(f"⚠️ **{len(anomalies)} Orta Seviye Anomali:** İzlenmesi gereken harcamalar var.")
        
        # Kategori verimlilik analizi
        cat_stats = self.category_performance()
        if not cat_stats.empty:
            most_efficient = cat_stats.iloc[0]
            least_efficient = cat_stats.iloc[-1]
            
            # Güvenli kategori ismi erişimi
            most_cat_name = most_efficient.get('kategori', most_efficient.get('Kategori', most_efficient.name if hasattr(most_efficient, 'name') else 'Bilinmiyor'))
            least_cat_name = least_efficient.get('kategori', least_efficient.get('Kategori', least_efficient.name if hasattr(least_efficient, 'name') else 'Bilinmiyor'))
            
            insights.append(f"🏆 **En Verimli Kategori:** {most_cat_name} - Her ₺1 harcama için {most_efficient['verimlilik_skoru']:.2f} mutluluk birimi.")
            insights.append(f"📉 **En Az Verimli Kategori:** {least_cat_name} - Her ₺1 harcama için {least_efficient['verimlilik_skoru']:.2f} mutluluk birimi.")
            
            # Güven aralığı yorumları
            if most_efficient['harcama_cv'] < 0.3:
                insights.append(f"🎯 **Tutarlı Harcama:** {most_cat_name} kategorisinde harcamalarınız çok tutarlı.")
        
        return insights
