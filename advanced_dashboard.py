import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

class AdvancedDashboard:
    def __init__(self, data, analyzer):
        self.data = data
        self.analyzer = analyzer
    
    def render_statistical_tests(self):
        """İstatistiksel testler sonuçları"""
        st.subheader("🧪 İstatistiksel Normallik Testleri")
        
        stat_tests = self.analyzer.statistical_tests()
        
        if 'genel' in stat_tests:
            general = stat_tests['genel']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Shapiro-Wilk Testi**")
                st.write(f"Statistic: {general['shapiro_wilk']['statistic']:.4f}")
                st.write(f"P-value: {general['shapiro_wilk']['p_value']:.4f}")
                st.write(f"Sonuç: {'✅ Normal' if general['shapiro_wilk']['normal'] else '❌ Non-normal'}")
            
            with col2:
                st.markdown("**D'Agostino Testi**")
                st.write(f"Statistic: {general['dagostino']['statistic']:.4f}")
                st.write(f"P-value: {general['dagostino']['p_value']:.4f}")
                st.write(f"Sonuç: {'✅ Normal' if general['dagostino']['normal'] else '❌ Non-normal'}")
            
            with col3:
                st.markdown("**Anderson-Darling**")
                st.write(f"Statistic: {general['anderson_darling']['statistic']:.4f}")
                critical_5 = general['anderson_darling']['critical_values'][2]  # 5% significance
                st.write(f"Critical (5%): {critical_5:.4f}")
                st.write(f"Sonuç: {'✅ Normal' if general['anderson_darling']['statistic'] < critical_5 else '❌ Non-normal'}")
        
        # Kategori bazında testler
        st.markdown("### 📊 Kategori Bazında Normallik Testleri")
        
        category_tests = {k: v for k, v in stat_tests.items() if k != 'genel'}
        
        if category_tests:
            test_data = []
            for kategori, test in category_tests.items():
                test_data.append({
                    'Kategori': kategori,
                    'Shapiro-Wilk Stat': test['shapiro_wilk']['statistic'],
                    'P-value': test['shapiro_wilk']['p_value'],
                    'Normal': '✅' if test['shapiro_wilk']['normal'] else '❌'
                })
            
            test_df = pd.DataFrame(test_data)
            st.dataframe(test_df, width='stretch')
    
    def render_correlation_analysis(self):
        """Gelişmiş korelasyon analizi"""
        st.subheader("🔗 Gelişmiş Korelasyon Analizi")
        
        correlations = self.analyzer.calculate_correlations()
        
        # Genel korelasyonlar
        if 'genel' in correlations:
            gen_corr = correlations['genel']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pearson (Lineer)", f"{gen_corr['pearson']['korelasyon']:.3f}")
                st.write(f"P-value: {gen_corr['pearson']['p_degeri']:.4f}")
                st.write(f"Anlamlı: {'✅' if gen_corr['pearson']['anlamli'] else '❌'}")
            
            with col2:
                st.metric("Spearman (Monoton)", f"{gen_corr['spearman']['korelasyon']:.3f}")
                st.write(f"P-value: {gen_corr['spearman']['p_degeri']:.4f}")
                st.write(f"Anlamlı: {'✅' if gen_corr['spearman']['anlamli'] else '❌'}")
            
            with col3:
                st.metric("Kendall (Rank)", f"{gen_corr['kendall']['korelasyon']:.3f}")
                st.write(f"P-value: {gen_corr['kendall']['p_degeri']:.4f}")
                st.write(f"Anlamlı: {'✅' if gen_corr['kendall']['anlamli'] else '❌'}")
        
        # Kategori korelasyonları
        st.markdown("### 📊 Kategori Bazında Korelasyonlar")
        
        category_corrs = {k: v for k, v in correlations.items() if k != 'genel' and v['pearson']['anlamli']}
        
        if category_corrs:
            corr_data = []
            for kategori, corr in category_corrs.items():
                corr_data.append({
                    'Kategori': kategori,
                    'Pearson': corr['pearson']['korelasyon'],
                    'Spearman': corr['spearman']['korelasyon'],
                    'Kendall': corr['kendall']['korelasyon'],
                    'Fark (|S-P|)': abs(corr['spearman']['korelasyon'] - corr['pearson']['korelasyon'])
                })
            
            corr_df = pd.DataFrame(corr_data).sort_values('Pearson', key=abs, ascending=False)
            st.dataframe(corr_df, width='stretch')
            
            # Görselleştirme
            fig = go.Figure()
            
            categories = list(category_corrs.keys())
            pearson_vals = [category_corrs[cat]['pearson']['korelasyon'] for cat in categories]
            spearman_vals = [category_corrs[cat]['spearman']['korelasyon'] for cat in categories]
            
            fig.add_trace(go.Bar(name='Pearson', x=categories, y=pearson_vals))
            fig.add_trace(go.Bar(name='Spearman', x=categories, y=spearman_vals))
            
            fig.update_layout(
                title="Kategori Bazında Korelasyon Karşılaştırması",
                xaxis_title="Kategori",
                yaxis_title="Korelasyon Katsayısı",
                barmode='group',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig, width='stretch')
    
    def render_clustering_analysis(self):
        """Kümeleme analizi sonuçları"""
        st.subheader("🎯 Harcama Davranışı Kümeleme")
        
        clustering = self.analyzer.clustering_analysis()
        
        if clustering is None:
            st.warning("⚠️ Kümeleme analizi için yeterli veri bulunmuyor (minimum 10 işlem gerekli).")
            return
        
        # Küme profilleri
        st.markdown("### 📊 Küme Profilleri")
        
        for cluster_name, profile in clustering['cluster_profiles'].items():
            with st.expander(f"🎯 {cluster_name}: {profile['profile']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Ortalama Harcama", f"₺{profile['avg_amount']:.0f}")
                
                with col2:
                    st.metric("Ortalama Mutluluk", f"{profile['avg_happiness']:.1f}/10")
                
                with col3:
                    st.metric("İşlem Sayısı", f"{profile['transaction_count']:.0f}")
                
                st.write(f"**Kategoriler:** {', '.join(profile['categories'])}")
        
        # Elbow grafiği
        st.markdown("### 📈 Optimal Küme Sayısı (Elbow Metodu)")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(clustering['inertias']) + 1)),
            y=clustering['inertias'],
            mode='lines+markers',
            name='Inertia',
            line=dict(color='#00ff41', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_vline(x=clustering['optimal_k'], line_dash="dash", line_color="red", 
                     annotation_text=f"Optimal k={clustering['optimal_k']}")
        
        fig.update_layout(
            title="Elbow Method - Optimal Küme Sayısı",
            xaxis_title="Küme Sayısı",
            yaxis_title="Inertia",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Küme dağılımı
        st.markdown("### 🎯 Küme Dağılımı")
        
        features = clustering['features']
        
        fig = px.scatter(
            features,
            x='avg_amount',
            y='avg_happiness',
            color='cluster_name',
            size='transaction_count',
            hover_data=['kategori'],
            title="Harcama Kategorileri - Kümeleme Sonuçları",
            labels={
                'avg_amount': 'Ortalama Harcama (₺)',
                'avg_happiness': 'Ortalama Mutluluk',
                'cluster_name': 'Küme',
                'transaction_count': 'İşlem Sayısı'
            }
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def render_advanced_anomalies(self):
        """Gelişmiş anomali analizi"""
        st.subheader("🚨 Gelişmiş Anomali Tespiti")
        
        anomalies = self.analyzer.detect_anomalies()
        
        if not anomalies:
            st.success("✅ Anomali tespit edilmedi!")
            return
        
        # Anomali özeti
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_severity = len([a for a in anomalies if a['severity'] == 'Yüksek'])
            st.metric("Yüksek Şiddet", high_severity)
        
        with col2:
            medium_severity = len([a for a in anomalies if a['severity'] == 'Orta'])
            st.metric("Orta Şiddet", medium_severity)
        
        with col3:
            total_anomalies = len(anomalies)
            st.metric("Toplam Anomali", total_anomalies)
        
        # Anomali detayları
        st.markdown("### 📋 Anomali Detayları")
        
        for anomaly in anomalies[:10]:  # İlk 10 anomali
            severity_color = "🔴" if anomaly['severity'] == 'Yüksek' else "🟡"
            
            with st.expander(f"{severity_color} {anomaly['kategori']} - ₺{anomaly['miktar']:.0f} ({anomaly['tarih'].strftime('%d.%m.%Y')})"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Z-Score", f"{anomaly['z_score']:.2f}")
                
                with col2:
                    st.metric("Modified Z-Score", f"{anomaly['modified_z_score']:.2f}")
                
                with col3:
                    st.metric("IQR Outlier", "✅" if anomaly['iqr_outlier'] else "❌")
                
                with col4:
                    st.metric("Anomaly Score", f"{anomaly['anomaly_score']}/3")
                
                st.write(f"**Mutluluk Skoru:** {anomaly['mutluluk_skoru']}/10")
                if anomaly['aciklama']:
                    st.write(f"**Açıklama:** {anomaly['aciklama']}")
                
                st.warning(f"⚠️ **{anomaly['severity']} şiddetli anomali tespit edildi!**")
    
    def render_trend_analysis(self):
        """Gelişmiş trend analizi"""
        st.subheader("📈 Gelişmiş Trend Analizi")
        
        monthly_trends = self.analyzer.monthly_trends()
        
        if len(monthly_trends) < 3:
            st.warning("⚠️ Trend analizi için en az 3 aylık veri gerekli.")
            return
        
        # Trend metrikleri
        last_month = monthly_trends.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("R² (Harcama)", f"{last_month['harcama_r2']:.3f}")
        
        with col2:
            st.metric("R² (Mutluluk)", f"{last_month['mutluluk_r2']:.3f}")
        
        with col3:
            st.metric("Volatilite (H)", f"{last_month['harcama_volatilite']:.3f}")
        
        with col4:
            st.metric("Volatilite (M)", f"{last_month['mutluluk_volatilite']:.3f}")
        
        # Trend grafiği
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Harcama Trendi", "Mutluluk Trendi"),
            vertical_spacing=0.1
        )
        
        # Harcama trendi
        fig.add_trace(
            go.Scatter(x=monthly_trends.index, y=monthly_trends['toplam_harcama'],
                      mode='lines+markers', name='Gerçek Harcama',
                      line=dict(color='#00ff41')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=monthly_trends.index, y=monthly_trends['harcama_trend'],
                      mode='lines', name='Lineer Trend',
                      line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        
        # Mutluluk trendi
        fig.add_trace(
            go.Scatter(x=monthly_trends.index, y=monthly_trends['ortalama_mutluluk'],
                      mode='lines+markers', name='Gerçek Mutluluk',
                      line=dict(color='#ff6b6b')),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=monthly_trends.index, y=monthly_trends['mutluluk_trend'],
                      mode='lines', name='Lineer Trend',
                      line=dict(color='yellow', dash='dash')),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=False
        )
        
        st.plotly_chart(fig, width='stretch')
