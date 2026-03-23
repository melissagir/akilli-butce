import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Dashboard:
    def __init__(self, data, analyzer):
        self.data = data
        self.analyzer = analyzer
    
    def render_overview_metrics(self):
        """Genel bakış metrikleri"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spent = self.data['miktar'].sum()
            st.metric(
                label="💰 Toplam Harcama",
                value=f"₺{total_spent:,.0f}",
                delta=None
            )
        
        with col2:
            avg_happiness = self.data['mutluluk_skoru'].mean()
            st.metric(
                label="😊 Ortalama Mutluluk",
                value=f"{avg_happiness:.1f}/10",
                delta=None
            )
        
        with col3:
            total_transactions = len(self.data)
            st.metric(
                label="📊 İşlem Sayısı",
                value=f"{total_transactions}",
                delta=None
            )
        
        with col4:
            avg_transaction = self.data['miktar'].mean()
            st.metric(
                label="📈 Ortalama İşlem",
                value=f"₺{avg_transaction:.0f}",
                delta=None
            )
    
    def render_spending_vs_happiness_scatter(self):
        """Harcama vs Mutluluk saçılım grafiği"""
        st.subheader("💸 Harcama Miktarı vs Mutluluk Skoru")
        
        fig = px.scatter(
            self.data,
            x='miktar',
            y='mutluluk_skoru',
            color='kategori',
            size='miktar',
            hover_data=['aciklama', 'tarih'],
            title="Harcama Miktarı ve Mutluluk İlişkisi",
            labels={
                'miktar': 'Harcama Miktarı (₺)',
                'mutluluk_skoru': 'Mutluluk Skoru (1-10)',
                'kategori': 'Kategori'
            }
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def render_category_performance(self):
        """Kategori performans grafiği"""
        st.subheader("📊 Kategori Performansı")
        
        cat_stats = self.analyzer.category_performance()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Toplam harcama pasta grafiği
            fig_pie = px.pie(
                cat_stats,
                values='toplam_harcama',
                names='kategori',
                title="Kategorilere Göre Harcama Dağılımı"
            )
            
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_size=14
            )
            
            st.plotly_chart(fig_pie, width='stretch')
        
        with col2:
            # Mutluluk verimliliği bar grafiği
            fig_bar = px.bar(
                cat_stats,
                x='kategori',
                y='verimlilik_skoru',
                title="Kategori Verimlilik Skoru (Mutluluk/Harcama)",
                labels={
                    'verimlilik_skoru': 'Verimlilik Skoru',
                    'kategori': 'Kategori'
                }
            )
            
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_size=14,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_bar, width='stretch')
    
    def render_trend_analysis(self):
        """Trend analizi grafikleri"""
        st.subheader("📈 Zaman Serisi Analizi")
        
        monthly_trends = self.analyzer.monthly_trends()
        weekly_trends = self.analyzer.weekly_trends()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Aylık harcama trendi
            fig_monthly = go.Figure()
            
            fig_monthly.add_trace(go.Scatter(
                x=monthly_trends.index,
                y=monthly_trends['toplam_harcama'],
                mode='lines+markers',
                name='Aylık Harcama',
                line=dict(color='#00ff41', width=3),
                marker=dict(size=8)
            ))
            
            # Trend çizgisi
            if len(monthly_trends) >= 3:
                trend_line = np.polyfit(range(len(monthly_trends)), monthly_trends['toplam_harcama'], 1)
                trend_y = np.polyval(trend_line, range(len(monthly_trends)))
                fig_monthly.add_trace(go.Scatter(
                    x=monthly_trends.index,
                    y=trend_y,
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', width=2, dash='dash')
                ))
            
            fig_monthly.update_layout(
                title="Aylık Harcama Trendi",
                xaxis_title="Ay",
                yaxis_title="Harcama (₺)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_size=14
            )
            
            st.plotly_chart(fig_monthly, width='stretch')
        
        with col2:
            # Mutluluk trendi
            fig_happiness = go.Figure()
            
            fig_happiness.add_trace(go.Scatter(
                x=monthly_trends.index,
                y=monthly_trends['ortalama_mutluluk'],
                mode='lines+markers',
                name='Ortalama Mutluluk',
                line=dict(color='#ff6b6b', width=3),
                marker=dict(size=8)
            ))
            
            # Trend çizgisi
            if len(monthly_trends) >= 3:
                trend_line = np.polyfit(range(len(monthly_trends)), monthly_trends['ortalama_mutluluk'], 1)
                trend_y = np.polyval(trend_line, range(len(monthly_trends)))
                fig_happiness.add_trace(go.Scatter(
                    x=monthly_trends.index,
                    y=trend_y,
                    mode='lines',
                    name='Trend',
                    line=dict(color='yellow', width=2, dash='dash')
                ))
            
            fig_happiness.update_layout(
                title="Mutluluk Trendi",
                xaxis_title="Ay",
                yaxis_title="Mutluluk Skoru",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_size=14,
                yaxis=dict(range=[0, 11])
            )
            
            st.plotly_chart(fig_happiness, width='stretch')
    
    def render_correlation_heatmap(self):
        """Harcama-Mutluluk ilişkisi"""
        st.subheader("🔥 Hangi Harcamalar Seni Daha Mutlu Ediyor?")
        
        correlations = self.analyzer.calculate_correlations()
        
        # Anlamlı ilişkileri filtrele - güvenli erişim
        significant_corrs = {}
        for k, v in correlations.items():
            pearson_anlamli = v.get('pearson', {}).get('anlamli', False)
            if pearson_anlamli and k != 'genel':
                significant_corrs[k] = v
        
        if significant_corrs:
            corr_data = []
            for kategori, data in significant_corrs.items():
                pearson_corr = data.get('pearson', {}).get('korelasyon', 0)
                pearson_p = data.get('pearson', {}).get('p_degeri', 1)
                
                corr_data.append({
                    'Kategori': kategori,
                    'İlişki': pearson_corr,
                    'Güven': pearson_p
                })
            
            corr_df = pd.DataFrame(corr_data)
            
            fig = px.bar(
                corr_df,
                x='Kategori',
                y='İlişki',
                color='İlişki',
                color_continuous_scale='RdYlBu',
                title="Hangi kategoriler seni daha mutlu ediyor?"
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_size=14,
                xaxis_tickangle=-45
            )
            
            fig.add_hline(y=0, line_dash="dash", line_color="white")
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📊 Henüz anlamlı bir ilişki bulunamadı. Daha fazla harcama yaptıktan sonra sana özel ipuçları verebilirim!")
    
    def render_anomalies(self):
        """Sıra dışı harcamalar"""
        st.subheader("🚨 Dikkat Edilmesi Gereken Harcamalar")
        
        anomalies = self.analyzer.detect_anomalies()
        
        if anomalies:
            for anomaly in anomalies[:5]:  # İlk 5 anormal harcama
                with st.expander(f"🔍 {anomaly['kategori']} - ₺{anomaly['miktar']:.0f} ({anomaly['tarih'].strftime('%d.%m.%Y')})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Farklılık", f"{anomaly['z_score']:.2f}")
                    
                    with col2:
                        st.metric("Skor", f"{anomaly['modified_z_score']:.2f}")
                    
                    with col3:
                        st.metric("Durum", "⚠️" if anomaly['iqr_outlier'] else "✅")
                    
                    st.write(f"**Keyif Puanı:** {anomaly['mutluluk_skoru']}/10")
                    if anomaly['aciklama']:
                        st.write(f"**Not:** {anomaly['aciklama']}")
                    
                    if anomaly['severity'] == 'Yüksek':
                        st.warning("⚠️ Bu harcama normalinden çok farklı!")
                    else:
                        st.info("ℹ️ Bu harcama biraz dikkat gerektiriyor.")
        else:
            st.success("✅ Harcama alışkanlıkların çok düzenli!")
    
    def render_data_table(self):
        """Veri tablosu"""
        st.subheader("📋 Harcama Detayları")
        
        # Filtreleme seçenekleri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_category = st.selectbox(
                "Kategori Filtrele",
                ["Tümü"] + list(self.data['kategori'].unique())
            )
        
        with col2:
            min_happiness = st.slider(
                "Min Mutluluk Skoru",
                min_value=1,
                max_value=10,
                value=1
            )
        
        with col3:
            max_amount = st.number_input(
                "Max Harcama Miktarı",
                min_value=0.0,
                value=float(self.data['miktar'].max()),
                step=10.0
            )
        
        # Veriyi filtrele
        filtered_data = self.data.copy()
        
        if selected_category != "Tümü":
            filtered_data = filtered_data[filtered_data['kategori'] == selected_category]
        
        filtered_data = filtered_data[
            (filtered_data['mutluluk_skoru'] >= min_happiness) &
            (filtered_data['miktar'] <= max_amount)
        ]
        
        # Tabloyu göster
        st.dataframe(
            filtered_data[['tarih', 'kategori', 'miktar', 'mutluluk_skoru', 'aciklama']]
            .sort_values('tarih', ascending=False)
            .reset_index(drop=True),
            width='stretch'
        )
