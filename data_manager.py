import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataManager:
    def __init__(self, db_path="harcamalar.db"):
        self.db_path = db_path
        self.init_database()
        self.generate_sample_data()
    
    def init_database(self):
        """SQLite veritabanını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS harcamalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            miktar REAL NOT NULL,
            kategori TEXT NOT NULL,
            tarih DATE NOT NULL,
            mutluluk_skoru INTEGER CHECK(mutluluk_skoru >= 1 AND mutluluk_skoru <= 10),
            aciklama TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_sample_data(self):
        """Örnek harcama verileri oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mevcut veri kontrolü
        cursor.execute("SELECT COUNT(*) FROM harcamalar")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        kategoriler = [
            "Kahve", "Dışarıda Yemek", "Alışveriş", "Ulaşım", 
            "Eğlence", "Eğitim", "Sağlık", "Faturalar", "Spor", "Diğer"
        ]
        
        # Son 6 ay için örnek veriler oluştur
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(500):  # 500 örnek harcama
            tarih = base_date + timedelta(days=random.randint(0, 180))
            kategori = random.choice(kategoriler)
            
            # Kategoriye göre miktar belirle
            miktar_araliklari = {
                "Kahve": (15, 80),
                "Dışarıda Yemek": (50, 300),
                "Alışveriş": (100, 1000),
                "Ulaşım": (10, 150),
                "Eğlence": (50, 500),
                "Eğitim": (100, 800),
                "Sağlık": (50, 500),
                "Faturalar": (200, 1500),
                "Spor": (50, 300),
                "Diğer": (20, 400)
            }
            
            min_miktar, max_miktar = miktar_araliklari.get(kategori, (20, 500))
            miktar = round(random.uniform(min_miktar, max_miktar), 2)
            
            # Kategori ve miktar'a göre mutluluk skoru belirle
            if kategori in ["Kahve", "Eğlence", "Spor"]:
                mutluluk_skoru = random.randint(6, 10)
            elif kategori in ["Faturalar", "Sağlık"]:
                mutluluk_skoru = random.randint(2, 6)
            else:
                mutluluk_skoru = random.randint(4, 8)
            
            aciklamalar = {
                "Kahve": ["Starbucks", "Kahveci", "Kahve molası"],
                "Dışarıda Yemek": ["Öğle yemeği", "Akşam yemeği", "Tatil"],
                "Alışveriş": ["Giyim", "Elektronik", "Market"],
                "Ulaşım": ["Taksi", "Toplu taşıma", "Benzin"],
                "Eğlence": ["Sinema", "Konser", "Tiyatro"],
                "Eğitim": ["Kitap", "Kurs", "Eğitim materyali"],
                "Sağlık": ["Doktor", "İlaç", "Vitamin"],
                "Faturalar": ["Elektrik", "Su", "İnternet"],
                "Spor": ["Salon", "Ekipman", "Turnuva"],
                "Diğer": ["Hediye", "Bağış", "Diğer"]
            }
            
            aciklama = random.choice(aciklamalar.get(kategori, ["Genel harcama"]))
            
            cursor.execute('''
            INSERT INTO harcamalar (miktar, kategori, tarih, mutluluk_skoru, aciklama)
            VALUES (?, ?, ?, ?, ?)
            ''', (miktar, kategori, tarih.strftime('%Y-%m-%d'), mutluluk_skoru, aciklama))
        
        conn.commit()
        conn.close()
    
    def get_data(self, start_date=None, end_date=None):
        """Veritabanından verileri pandas DataFrame olarak al"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM harcamalar"
        params = []
        
        if start_date and end_date:
            query += " WHERE tarih BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            df['tarih'] = pd.to_datetime(df['tarih'])
        
        return df
    
    def add_expense(self, miktar, kategori, mutluluk_skoru, aciklama=""):
        """Yeni harcama ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tarih = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
        INSERT INTO harcamalar (miktar, kategori, tarih, mutluluk_skoru, aciklama)
        VALUES (?, ?, ?, ?, ?)
        ''', (miktar, kategori, tarih, mutluluk_skoru, aciklama))
        
        conn.commit()
        conn.close()
    
    def get_category_stats(self):
        """Kategori bazında istatistikler"""
        df = self.get_data()
        if df.empty:
            return pd.DataFrame()
        
        stats = df.groupby('kategori').agg({
            'miktar': ['sum', 'mean', 'count'],
            'mutluluk_skoru': 'mean'
        }).round(2)
        
        stats.columns = ['Toplam Harcama', 'Ortalama Harcama', 'Harcama Sayısı', 'Ortalama Mutluluk']
        return stats.reset_index()
