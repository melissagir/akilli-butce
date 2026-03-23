import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class PersonalDashboard:
    def __init__(self, data, analyzer):
        self.data = data
        self.analyzer = analyzer
        
        # Kategori emojileri
        self.category_emojis = {
            "Kahve": "☕",
            "Dışarıda Yemek": "🍕",
            "Alışveriş": "🛍️",
            "Ulaşım": "🚗",
            "Eğlence": "🎮",
            "Eğitim": "📚",
            "Sağlık": "🏥",
            "Faturalar": "📄",
            "Spor": "⚽",
            "Diğer": "📦"
        }
        
        # Duygu renkleri
        self.emotion_colors = {
            "Mutlu": "#00ff41",
            "Nötr": "#ffaa00", 
            "Üzgün": "#ff4444",
            "Endişeli": "#ff6b6b"
        }
    
    def render_mood_check(self):
        """Günlük mod kontrolü"""
        st.markdown("### 😊 Bugün Nasılsın?")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            mood_options = {
                "Harika! 😄": 10,
                "İyi 😊": 8,
                "Fena Değil 😐": 6,
                "Biraz Düşük 😔": 4,
                "Kötü 😢": 2
            }
            
            selected_mood = st.selectbox(
                "Modunu seç:",
                list(mood_options.keys()),
                key="daily_mood"
            )
            
            mood_score = mood_options[selected_mood]
            
            # Motivasyonel mesaj
            mood_messages = {
                10: "Harika enerji! Bu güzel modunu koru 🌟",
                8: "Keyifli bir gün geçirmektesin 👍",
                6: "Dengeli bir gün, bu da güzel 🌈",
                4: "Her gün böyle olmaz, yarum daha iyi olacak 🌅",
                2: "Zor bir gün ama bu da geçecek 💪"
            }
            
            st.info(mood_messages[mood_score])
            
            return mood_score
    
    def render_friendly_metrics(self):
        """Dostça metrik kartları"""
        st.markdown("### 📊 Harcama Özetin")
        
        # Hesaplamalar
        total_spent = self.data['miktar'].sum()
        avg_happiness = self.data['mutluluk_skoru'].mean()
        transaction_count = len(self.data)
        avg_transaction = self.data['miktar'].mean()
        
        # En çok harcanan kategori
        top_category = self.data.groupby('kategori')['miktar'].sum().idxmax()
        top_category_emoji = self.category_emojis.get(top_category, "📦")
        
        # En mutlu edici kategori
        happiest_category = self.data.groupby('kategori')['mutluluk_skoru'].mean().idxmax()
        happiest_category_emoji = self.category_emojis.get(happiest_category, "📦")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        border-radius: 15px; padding: 20px; margin: 10px 0; 
                        border-left: 4px solid #00ff41; box-shadow: 0 4px 15px rgba(0,255,65,0.1);">
                <h4 style="color: #00ff41; margin: 0;">💰 En Çok Ne Seni Mutlu Ediyor?</h4>
                <h2 style="color: white; margin: 5px 0;">{happiest_category_emoji} {happiest_category}</h2>
                <p style="color: #aaa; margin: 0; font-size: 14px;">Bu kategoride en keyifli</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        border-radius: 15px; padding: 20px; margin: 10px 0; 
                        border-left: 4px solid #ff6b6b; box-shadow: 0 4px 15px rgba(255,107,107,0.1);">
                <h4 style="color: #ff6b6b; margin: 0;">😊 Ortalama Keyif Puanı</h4>
                <h2 style="color: white; margin: 5px 0;">{avg_happiness:.1f}/10</h2>
                <p style="color: #aaa; margin: 0; font-size: 14px;">Harcamalarından gelen</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        border-radius: 15px; padding: 20px; margin: 10px 0; 
                        border-left: 4px solid #4a90e2; box-shadow: 0 4px 15px rgba(74,144,226,0.1);">
                <h4 style="color: #4a90e2; margin: 0;">🎯 Günün Vibe Özeti</h4>
                <h2 style="color: white; margin: 5px 0;">{transaction_count} Harcama</h2>
                <p style="color: #aaa; margin: 0; font-size: 14px;">Toplamda ₺{total_spent:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        border-radius: 15px; padding: 20px; margin: 10px 0; 
                        border-left: 4px solid #f39c12; box-shadow: 0 4px 15px rgba(243,156,18,0.1);">
                <h4 style="color: #f39c12; margin: 0;">💸 Cebini En Çok Ne Yoruyor?</h4>
                <h2 style="color: white; margin: 5px 0;">{top_category_emoji} {top_category}</h2>
                <p style="color: #aaa; margin: 0; font-size: 14px;">Bu ay favorin</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_emotional_spending_chart(self):
        """Duygusal harcama grafiği"""
        st.markdown("### 💰 Hangi Harcamalar Seni Daha Mutlu Ediyor?")
        
        # Kategoriye göre emoji ekle
        data_with_emoji = self.data.copy()
        data_with_emoji['kategori_emoji'] = data_with_emoji['kategori'].map(self.category_emojis)
        
        fig = px.scatter(
            data_with_emoji,
            x='miktar',
            y='mutluluk_skoru',
            color='kategori_emoji',
            size='miktar',
            hover_data=['kategori', 'aciklama', 'tarih'],
            title="Hangi harcamalar sana daha iyi hissettiriyor?",
            labels={
                'miktar': 'Harcama Miktarı (₺)',
                'mutluluk_skoru': 'Keyif Puanı',
                'kategori_emoji': 'Kategori'
            },
            color_discrete_map={
                "☕": "#8B4513", "🍕": "#FF6B6B", "🛍️": "#4A90E2",
                "🚗": "#FFA500", "🎮": "#9B59B6", "📚": "#27AE60",
                "🏥": "#E74C3C", "📄": "#95A5A6", "⚽": "#F39C12", "📦": "#7F8C8D"
            }
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(26,26,46,0.8)',
            paper_bgcolor='rgba(22,33,62,0.9)',
            font_color='white',
            title_font_size=18,
            title_font_color='#00ff41',
            showlegend=True
        )
        
        fig.update_traces(marker=dict(line=dict(width=1, color='white')))
        
        st.plotly_chart(fig, width='stretch')
    
    def render_happy_spending_pie(self):
        """Mutluluk pasta grafiği"""
        st.markdown("### 🎉 Nereye Ne Kadar Harcıyorsun?")
        
        # Kategori bazında ortalama mutluluk
        happy_spending = self.data.groupby('kategori').agg({
            'miktar': 'sum',
            'mutluluk_skoru': 'mean'
        }).round(2)
        
        happy_spending['emoji'] = happy_spending.index.map(self.category_emojis)
        happy_spending['display_name'] = happy_spending['emoji'] + ' ' + happy_spending.index
        
        fig = px.pie(
            happy_spending,
            values='miktar',
            names='display_name',
            title="Paranı nereye harcıyorsun?",
            color_discrete_sequence=[
                '#FF6B6B', '#4A90E2', '#F39C12', '#27AE60', 
                '#9B59B6', '#E74C3C', '#95A5A6', '#FFA500',
                '#8B4513', '#7F8C8D'
            ]
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(26,26,46,0.8)',
            paper_bgcolor='rgba(22,33,62,0.9)',
            font_color='white',
            title_font_size=18,
            title_font_color='#00ff41',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Mutluluk sıralaması
        happy_ranking = happy_spending.sort_values('mutluluk_skoru', ascending=False)
        
        st.markdown("#### 🏆 Keyif Sıralaması")
        for i, (kategori, row) in enumerate(happy_ranking.iterrows(), 1):
            emoji = row['emoji']
            happiness = row['mutluluk_skoru']
            
            if happiness >= 8:
                medal = "🥇"
                color = "#00ff41"
            elif happiness >= 6:
                medal = "🥈"
                color = "#f39c12"
            else:
                medal = "🥉"
                color = "#ff6b6b"
            
            st.markdown(f"""
            <div style="background: rgba(26,26,46,0.8); border-radius: 10px; 
                        padding: 10px; margin: 5px 0; border-left: 3px solid {color};">
                <span style="font-size: 20px;">{medal}</span>
                <span style="font-size: 16px; margin-left: 10px;">{emoji} {kategori}</span>
                <span style="float: right; color: {color}; font-weight: bold;">{happiness:.1f}/10 😊</span>
            </div>
            """, unsafe_allow_html=True)
    
    def render_weekly_mood_trend(self):
        """Haftalık mod trendi"""
        st.markdown("### 📈 Son Haftalardaki Modun")
        
        # Son 4 haftanın verisi
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        recent_data = self.data[self.data['tarih'] >= four_weeks_ago].copy()
        
        if len(recent_data) == 0:
            st.warning("Son 4 haftada yeterli veri bulunmuyor.")
            return
        
        # Haftalık gruplama
        recent_data['hafta'] = recent_data['tarih'].dt.isocalendar().week
        weekly_mood = recent_data.groupby('hafta')['mutluluk_skoru'].mean().reset_index()
        
        # Hafta isimleri
        week_names = []
        for week in weekly_mood['hafta']:
            week_date = datetime.fromisocalendar(2024, week, 1)  # 2024 yılı varsayımı
            week_names.append(week_date.strftime("%d %B"))
        
        weekly_mood['hafta_adi'] = week_names
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=weekly_mood['hafta_adi'],
            y=weekly_mood['mutluluk_skoru'],
            mode='lines+markers',
            name='Keyif Trendi',
            line=dict(color='#00ff41', width=4),
            marker=dict(size=10, color='#00ff41')
        ))
        
        # Trend çizgisi
        if len(weekly_mood) >= 2:
            trend_line = np.polyfit(range(len(weekly_mood)), weekly_mood['mutluluk_skoru'], 1)
            trend_y = np.polyval(trend_line, range(len(weekly_mood)))
            
            fig.add_trace(go.Scatter(
                x=weekly_mood['hafta_adi'],
                y=trend_y,
                mode='lines',
                name='Trend',
                line=dict(color='yellow', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Son haftalardaki mod değişimin",
            xaxis_title="Hafta",
            yaxis_title="Ortalama Keyif Puanı",
            plot_bgcolor='rgba(26,26,46,0.8)',
            paper_bgcolor='rgba(22,33,62,0.9)',
            font_color='white',
            title_font_size=18,
            title_font_color='#00ff41',
            yaxis=dict(range=[0, 11])
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Trend yorumu
        if len(weekly_mood) >= 2:
            first_week = weekly_mood.iloc[0]['mutluluk_skoru']
            last_week = weekly_mood.iloc[-1]['mutluluk_skoru']
            
            if last_week > first_week + 1:
                st.success("🌟 Harika! Modun son haftalarda iyileşiyor!")
            elif last_week < first_week - 1:
                st.warning("🌙 Modunda bir düşüş var. Kendine daha fazla zaman ayırmayı deneyebilirsin.")
            else:
                st.info("⚖️ Modun stabil. Bu da güzel bir şey!")
    
    def render_personal_insights(self):
        """Kişisel içgörüler"""
        st.markdown("### 💡 Sana Özel İpuçları")
        
        insights = []
        
        # Son hafta analizi
        one_week_ago = datetime.now() - timedelta(weeks=1)
        recent_data = self.data[self.data['tarih'] >= one_week_ago]
        
        if len(recent_data) > 0:
            # En çok harcanan kategori
            top_category = recent_data.groupby('kategori')['miktar'].sum().idxmax()
            top_spending = recent_data[recent_data['kategori'] == top_category]
            top_happiness = top_spending['mutluluk_skoru'].mean()
            
            if top_happiness >= 7:
                insights.append(f"🎉 {self.category_emojis.get(top_category, '📦')} {top_category} harcamaların yüksek ve seni mutlu ediyor! Bu dengeni koru.")
            else:
                insights.append(f"🤔 {self.category_emojis.get(top_category, '📦')} {top_category} kategorisinde çok harcama yapıyorsun ama mutluluğun düşük. Belki biraz ara vermelisin?")
            
            # Düşük mutluluklu harcamalar
            low_happiness_spending = recent_data[recent_data['mutluluk_skoru'] <= 4]
            if len(low_happiness_spending) > 0:
                insights.append("💔 Bazı harcamalar seni mutlu etmemiş. Bu harcamaları tekrar düşünmek isteyebilirsin.")
        
        # Eğlence analizi
        entertainment_data = self.data[self.data['kategori'] == 'Eğlence']
        if len(entertainment_data) > 0:
            recent_entertainment = entertainment_data[entertainment_data['tarih'] >= one_week_ago]
            if len(recent_entertainment) == 0:
                insights.append("🎮 Son hafta eğlence için kendine zaman ayırmamışsın. Unutma, kendine zaman ayırmak da önemli!")
            else:
                entertainment_happiness = recent_entertainment['mutluluk_skoru'].mean()
                if entertainment_happiness >= 8:
                    insights.append("🎉 Eğlence harcamaların sana iyi gelmiş! Bu enerjiyi koru.")
        
        # Kahve analizi
        coffee_data = self.data[self.data['kategori'] == 'Kahve']
        if len(coffee_data) > 0:
            recent_coffee = coffee_data[coffee_data['tarih'] >= one_week_ago]
            if len(recent_coffee) >= 5:
                insights.append("☕ Bu hafta çok kahve içmişsin! Kahve molası vermek sana iyi geliyor gibi.")
        
        # Yemek alışkanlıkları
        food_data = self.data[self.data['kategori'] == 'Dışarıda Yemek']
        if len(food_data) > 0:
            recent_food = food_data[food_data['tarih'] >= one_week_ago]
            if len(recent_food) > 0:
                food_happiness = recent_food['mutluluk_skoru'].mean()
                if food_happiness >= 7:
                    insights.append("🍕 Dışarıda yemek yemek seni mutlu ediyor! Bu keyfi sürdür.")
                else:
                    insights.append("🍽 Belki evde yemek yapmak seni daha mutlu eder? Denemek isteyebilirsin.")
        
        # Genel bütçe tavsiyesi
        if len(recent_data) > 0:
            weekly_avg = recent_data['miktar'].sum()
            if weekly_avg > 2000:
                insights.append("💰 Bu hafta harcamaların biraz yüksek olmuş. Bir sonraki hafta daha dikkatli olabilirsin.")
            elif weekly_avg < 500:
                insights.append("🎯 Bu hafta çok tasarruflu davranmışsın! Tebrikler!")
        
        # İçgörüleri göster
        if insights:
            for insight in insights:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                            border-radius: 12px; padding: 15px; margin: 10px 0; 
                            border-left: 4px solid #00ff41; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                    <p style="color: white; margin: 0; font-size: 16px;">{insight}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 Henüz yeterli veri yok. Biraz daha harcama yaptıktan sonra sana özel ipuçları üretebilirim!")
