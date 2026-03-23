import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Local imports
from data_manager import DataManager
from analyzer import HarcamaAnalyzer
from dashboard import Dashboard
from advanced_dashboard import AdvancedDashboard
from personal_dashboard import PersonalDashboard

# Sayfa yapılandırması
st.set_page_config(
    page_title="Akıllı Bütçe ve Harcama Analizörü",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Koyu tema CSS
def load_personal_css():
    st.markdown("""
    <style>
        :root {
            --primary-color: #00ff41;
            --secondary-color: #ff6b6b;
            --accent-color: #f39c12;
            --background-color: #1a1a2e;
            --card-background: #16213e;
            --text-color: #ffffff;
            --border-color: #2c3e50;
        }
        
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: var(--text-color);
        }
        
        .stSidebar {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            border-right: 1px solid var(--border-color);
        }
        
        .metric-card {
            background: linear-gradient(135deg, var(--card-background) 0%, rgba(26,26,46,0.8) 100%);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0, 255, 65, 0.1);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 65, 0.2);
        }
        
        .vibe-check {
            background: linear-gradient(135deg, var(--card-background) 0%, rgba(26,26,46,0.9) 100%);
            border: 2px solid var(--primary-color);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0, 255, 65, 0.1);
        }
        
        .insight-card {
            background: linear-gradient(135deg, var(--card-background) 0%, rgba(44,62,80,0.9) 100%);
            border-left: 4px solid var(--primary-color);
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .stSelectbox > div > div {
            background-color: var(--card-background);
            color: var(--text-color);
        }
        
        .stSlider > div > div > div {
            background-color: var(--primary-color);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color) 0%, #00cc33 100%);
            color: var(--background-color);
            border: none;
            border-radius: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
            padding: 12px 24px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 255, 65, 0.3);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color);
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, var(--card-background) 0%, rgba(26,26,46,0.8) 100%);
            border-radius: 15px;
            border: 1px solid var(--border-color);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-color);
        }
        
        .stAlert {
            background: linear-gradient(135deg, var(--card-background) 0%, rgba(26,26,46,0.9) 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }
        
        .dataframe {
            background: var(--card-background);
            border-radius: 12px;
        }
        
        /* Soft dark theme adjustments */
        .streamlit-container {
            max-width: 1200px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_vibe_check(analyzer, data):
    """Vibe Check yorumları"""
    st.markdown('<div class="vibe-check">', unsafe_allow_html=True)
    st.markdown("### 🎯 Vibe Check - Akıllı Analiz")
    
    insights = analyzer.generate_insights()
    
    if insights:
        for insight in insights:
            st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)
    else:
        st.info("📊 Yeterli veri bulunamadı. Daha fazla harcama ekleyerek analizleri geliştirebilirsiniz.")
    
    # Özel analizler
    monthly_trends = analyzer.monthly_trends()
    if len(monthly_trends) >= 2:
        last_month = monthly_trends.iloc[-1]
        prev_month = monthly_trends.iloc[-2]
        
        # Kahve analizi
        coffee_data = data[data['kategori'] == 'Kahve']
        if len(coffee_data) >= 4:
            coffee_trend = coffee_data.tail(4)['miktar'].pct_change().mean()
            coffee_happiness = coffee_data['mutluluk_skoru'].mean()
            
            if coffee_trend > 0.1:
                if coffee_happiness < 6:
                    st.warning("☕ **Kahve Vibe Check:** Kahve harcamaların artıyor ama mutluluğun düşük. Belki biraz azaltmalısın?")
                else:
                    st.success("☕ **Kahve Vibe Check:** Kahve harcamaların artıyor ve mutluluğun yüksek. Bu dengenin tadını çıkar!")
        
        # Dışarıda yemek analizi
        dining_data = data[data['kategori'] == 'Dışarıda Yemek']
        if len(dining_data) >= 3:
            dining_avg = dining_data['miktar'].mean()
            dining_happiness = dining_data['mutluluk_skoru'].mean()
            
            if dining_avg > 200 and dining_happiness < 7:
                st.warning("🍽️ **Yemek Vibe Check:** Dışarıda yemek harcamaların yüksek ama mutluluğun beklenenin altında. Daha ekonomik ve mutluluk veren seçenekler deneyebilirsin.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_add_expense_form(data_manager):
    """Yeni harcama ekleme formu"""
    st.markdown("### ➕ Yeni Harcama Ekle")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            miktar = st.number_input("Harcama Miktarı (₺)", min_value=0.0, value=100.0, step=10.0)
            kategori = st.selectbox("Kategori", [
                "Kahve", "Dışarıda Yemek", "Alışveriş", "Ulaşım", 
                "Eğlence", "Eğitim", "Sağlık", "Faturalar", "Spor", "Diğer"
            ])
        
        with col2:
            mutluluk_skoru = st.slider("Mutluluk Skoru (1-10)", min_value=1, max_value=10, value=7)
            aciklama = st.text_input("Açıklama (opsiyonel)")
        
        submit_button = st.form_submit_button("💾 Harcamayı Kaydet")
        
        if submit_button:
            data_manager.add_expense(miktar, kategori, mutluluk_skoru, aciklama)
            st.success("✅ Harcama başarıyla eklendi!")
            st.experimental_rerun()

def main():
    # CSS yükle
    load_personal_css()
    
    # Başlık
    st.markdown("""
    # 💰 Kişisel Bütçe Koçun
    ### � Mutluluğunu Takip Et, Akıllı Harcama Yap
    """)
    
    # Veri yöneticisi ve analizör
    data_manager = DataManager()
    data = data_manager.get_data()
    
    if data.empty:
        st.error("📊 Veri bulunamadı! Lütfen veritabanını kontrol edin.")
        return
    
    analyzer = HarcamaAnalyzer(data)
    dashboard = Dashboard(data, analyzer)
    advanced_dashboard = AdvancedDashboard(data, analyzer)
    personal_dashboard = PersonalDashboard(data, analyzer)
    
    # Sidebar
    st.sidebar.markdown("## 🎛️ Kontrol Paneli")
    
    # Tarih filtreleme
    st.sidebar.markdown("### 📅 Tarih Aralığı")
    
    min_date = data['tarih'].min().date()
    max_date = data['tarih'].max().date()
    
    start_date = st.sidebar.date_input("Başlangıç Tarihi", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Bitiş Tarihi", max_date, min_value=min_date, max_value=max_date)
    
    # Veriyi filtrele
    filtered_data = data[
        (data['tarih'].dt.date >= start_date) & 
        (data['tarih'].dt.date <= end_date)
    ]
    
    if filtered_data.empty:
        st.warning("⚠️ Seçilen tarih aralığında veri bulunamadı!")
        return
    
    # Analizör ve dashboard'u güncelle
    analyzer = HarcamaAnalyzer(filtered_data)
    dashboard = Dashboard(filtered_data, analyzer)
    advanced_dashboard = AdvancedDashboard(filtered_data, analyzer)
    personal_dashboard = PersonalDashboard(filtered_data, analyzer)
    
    # Sekmeler
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "� Kişisel", "� Genel Bakış", "📈 Trend Analizi", "🎯 Vibe Check", "🧪 İstatistiksel", "➕ Harcama Ekle", "📋 Detaylar"
    ])
    
    with tab1:
        # Günlük mod kontrolü
        mood_score = personal_dashboard.render_mood_check()
        
        # Kişisel metrikler
        personal_dashboard.render_friendly_metrics()
        
        # Kişisel içgörüler
        personal_dashboard.render_personal_insights()
        
        # Duygusal harcama grafiği
        personal_dashboard.render_emotional_spending_chart()
        
        # Mutluluk pasta grafiği
        personal_dashboard.render_happy_spending_pie()
        
        # Haftalık mod trendi
        personal_dashboard.render_weekly_mood_trend()
    
    with tab2:
        # Metrikler
        dashboard.render_overview_metrics()
        
        # Ana grafikler
        col1, col2 = st.columns(2)
        
        with col1:
            dashboard.render_spending_vs_happiness_scatter()
        
        with col2:
            dashboard.render_category_performance()
    
    with tab3:
        dashboard.render_trend_analysis()
        dashboard.render_correlation_heatmap()
        dashboard.render_anomalies()
    
    with tab4:
        st.markdown("### 🎯 Detaylı Vibe Check Analizi")
        render_vibe_check(analyzer, filtered_data)
        
        # Ek analizler
        st.markdown("### 📊 Kategori Performansı")
        cat_stats = analyzer.category_performance()
        st.dataframe(cat_stats, width='stretch')
        
        st.markdown("### 🚨 Mutluluk Sürücüleri")
        happiness_drivers = analyzer.happiness_drivers()
        
        if happiness_drivers:
            drivers_df = pd.DataFrame(happiness_drivers).T
            drivers_df.columns = ['Ortalama Mutluluk', 'Toplam Harcama', 'Harcama Sayısı', 'Verimlilik']
            st.dataframe(drivers_df.sort_values('Verimlilik', ascending=False), width='stretch')
    
    with tab5:
        st.markdown("### 🧪 Gelişmiş İstatistiksel Analiz")
        
        # İstatistiksel testler
        advanced_dashboard.render_statistical_tests()
        
        # Gelişmiş korelasyon analizi
        advanced_dashboard.render_correlation_analysis()
        
        # Kümeleme analizi
        advanced_dashboard.render_clustering_analysis()
        
        # Gelişmiş anomali analizi
        advanced_dashboard.render_advanced_anomalies()
        
        # Gelişmiş trend analizi
        advanced_dashboard.render_trend_analysis()
    
    with tab6:
        render_add_expense_form(data_manager)
        
        # Son harcamalar
        st.markdown("### 📝 Son Harcamalar")
        st.dataframe(
            filtered_data[['tarih', 'kategori', 'miktar', 'mutluluk_skoru', 'aciklama']]
            .sort_values('tarih', ascending=False)
            .reset_index(drop=True),
            width='stretch'
        )
        
        # İstatistiksel özet
        st.markdown("### 📈 İstatistiksel Özet")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Harcama İstatistikleri**")
            st.write(f"- Ortalama: ₺{filtered_data['miktar'].mean():.2f}")
            st.write(f"- Medyan: ₺{filtered_data['miktar'].median():.2f}")
            st.write(f"- Standart Sapma: ₺{filtered_data['miktar'].std():.2f}")
            st.write(f"- Minimum: ₺{filtered_data['miktar'].min():.2f}")
            st.write(f"- Maksimum: ₺{filtered_data['miktar'].max():.2f}")
        
        with col2:
            st.markdown("**Mutluluk İstatistikleri**")
            st.write(f"- Ortalama: {filtered_data['mutluluk_skoru'].mean():.2f}/10")
            st.write(f"- Medyan: {filtered_data['mutluluk_skoru'].median():.2f}/10")
            st.write(f"- Standart Sapma: {filtered_data['mutluluk_skoru'].std():.2f}")
            st.write(f"- Minimum: {filtered_data['mutluluk_skoru'].min():.2f}/10")
            st.write(f"- Maksimum: {filtered_data['mutluluk_skoru'].max():.2f}/10")

    with tab7:
        dashboard.render_data_table()
        
        # İstatistiksel özet
        st.markdown("### 📈 İstatistiksel Özet")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Harcama İstatistikleri**")
            st.write(f"- Ortalama: ₺{filtered_data['miktar'].mean():.2f}")
            st.write(f"- Medyan: ₺{filtered_data['miktar'].median():.2f}")
            st.write(f"- Standart Sapma: ₺{filtered_data['miktar'].std():.2f}")
            st.write(f"- Minimum: ₺{filtered_data['miktar'].min():.2f}")
            st.write(f"- Maksimum: ₺{filtered_data['miktar'].max():.2f}")
        
        with col2:
            st.markdown("**Mutluluk İstatistikleri**")
            st.write(f"- Ortalama: {filtered_data['mutluluk_skoru'].mean():.2f}/10")
            st.write(f"- Medyan: {filtered_data['mutluluk_skoru'].median():.2f}/10")
            st.write(f"- Standart Sapma: {filtered_data['mutluluk_skoru'].std():.2f}")
            st.write(f"- Minimum: {filtered_data['mutluluk_skoru'].min():.2f}/10")
            st.write(f"- Maksimum: {filtered_data['mutluluk_skoru'].max():.2f}/10")

if __name__ == "__main__":
    main()
