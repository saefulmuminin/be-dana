from src.models.base_model import BaseModel
from datetime import datetime


class CampaignModel(BaseModel):
    """
    Model untuk tabel adm_campaign
    Digunakan untuk mengelola campaign/program zakat dan infak
    
    Schema columns:
    - id, kode_institusi, tipe, program_id, kategori
    - name, slug, target_donasi, start_date, end_date
    - prosen_biayaoperasional, biayaoperasional, donasi
    - url_fotoutama, informasi, status, prioritas
    """
    table_name = "adm_campaign"

    def findAll(self, limit=20, offset=0, tipe=None, kategori=None, sort='terbaru'):
        """
        Ambil semua campaign aktif dengan filter dan sorting
        
        Args:
            limit: Jumlah data per halaman
            offset: Offset untuk pagination
            tipe: Filter berdasarkan tipe (zakat/infak)
            kategori: Filter berdasarkan kategori
            sort: Sorting (terbaru/terlama/terkumpul)
        """
        with self.conn.cursor() as cursor:
            # Base query dengan join untuk menghitung total terkumpul
            sql = f"""
                SELECT 
                    c.*,
                    COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.nominal ELSE 0 END), 0) as total_terkumpul,
                    COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.biayaoperasional ELSE 0 END), 0) as operasional_terkumpul,
                    COUNT(CASE WHEN d.status = 'berhasil' THEN 1 END) as jumlah_muzaki,
                    CASE 
                        WHEN c.end_date IS NOT NULL THEN EXTRACT(DAY FROM (c.end_date - CURRENT_DATE))
                        ELSE NULL 
                    END as sisa_hari
                FROM {self.table_name} c
                LEFT JOIN adm_campaign_donasi d ON c.id = d.campaign_id AND d.is_delete = 'N'
                WHERE c.is_active = 'Y' AND c.is_delete = 'N' AND c.status = 'publish'
            """
            
            params = []
            
            # Filter berdasarkan tipe
            if tipe:
                sql += " AND c.tipe = %s"
                params.append(tipe)
            
            # Filter berdasarkan kategori
            if kategori and kategori != 'Semua':
                sql += " AND c.kategori = %s"
                params.append(kategori)
            
            # Group by campaign
            sql += " GROUP BY c.id"
            
            # Sorting
            if sort == 'terlama':
                sql += " ORDER BY c.created_date ASC"
            elif sort == 'terkumpul':
                sql += " ORDER BY total_terkumpul ASC"
            else:  # terbaru (default)
                sql += " ORDER BY CASE WHEN c.prioritas = 'Y' THEN 0 ELSE 1 END, c.created_date DESC"
            
            # Pagination
            sql += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()

    def search(self, keyword, limit=20, offset=0):
        """
        Search campaign berdasarkan keyword
        Mencari di name, informasi, dan kategori
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT 
                    c.*,
                    COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.nominal ELSE 0 END), 0) as total_terkumpul,
                    COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.biayaoperasional ELSE 0 END), 0) as operasional_terkumpul,
                    COUNT(CASE WHEN d.status = 'berhasil' THEN 1 END) as jumlah_muzaki,
                    CASE 
                        WHEN c.end_date IS NOT NULL THEN EXTRACT(DAY FROM (c.end_date - CURRENT_DATE))
                        ELSE NULL 
                    END as sisa_hari
                FROM {self.table_name} c
                LEFT JOIN adm_campaign_donasi d ON c.id = d.campaign_id AND d.is_delete = 'N'
                WHERE c.is_active = 'Y' AND c.is_delete = 'N' AND c.status = 'publish'
                AND (
                    c.name ILIKE %s OR 
                    c.informasi ILIKE %s OR 
                    c.kategori ILIKE %s OR
                    c.tipe::text ILIKE %s
                )
                GROUP BY c.id
                ORDER BY CASE WHEN c.prioritas = 'Y' THEN 0 ELSE 1 END, c.created_date DESC
                LIMIT %s OFFSET %s
            """
            
            search_pattern = f"%{keyword}%"
            cursor.execute(sql, (search_pattern, search_pattern, search_pattern, 
                                search_pattern, limit, offset))
            return cursor.fetchall()

    def findById(self, campaign_id):
        """
        Ambil detail campaign berdasarkan ID
        Termasuk list muzaki yang sudah berdonasi
        """
        with self.conn.cursor() as cursor:
            # Query campaign detail
            sql = f"""
                SELECT 
                    c.*,
                    COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.nominal ELSE 0 END), 0) as total_terkumpul,
                    COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.biayaoperasional ELSE 0 END), 0) as operasional_terkumpul,
                    COUNT(CASE WHEN d.status = 'berhasil' THEN 1 END) as jumlah_muzaki,
                    CASE 
                        WHEN c.end_date IS NOT NULL THEN EXTRACT(DAY FROM (c.end_date - CURRENT_DATE))
                        ELSE NULL 
                    END as sisa_hari
                FROM {self.table_name} c
                LEFT JOIN adm_campaign_donasi d ON c.id = d.campaign_id AND d.is_delete = 'N'
                WHERE c.id = %s AND c.is_delete = 'N'
                GROUP BY c.id
            """
            cursor.execute(sql, (campaign_id,))
            campaign = cursor.fetchone()
            
            if not campaign:
                return None
            
            # Query list muzaki
            sql_muzaki = """
                SELECT 
                    CASE 
                        WHEN hamba_allah = 'Y' THEN 'Hamba Allah'
                        ELSE nama_lengkap
                    END as nama_muzaki,
                    nominal as total_zakat,
                    created_date as tgl_donasi,
                    doa_muzaki
                FROM adm_campaign_donasi
                WHERE campaign_id = %s AND status = 'berhasil' AND is_delete = 'N'
                ORDER BY created_date DESC
                LIMIT 100
            """
            cursor.execute(sql_muzaki, (campaign_id,))
            muzaki_list = cursor.fetchall()
            
            campaign['list_muzaki'] = muzaki_list
            return campaign

    def getCategories(self):
        """
        Ambil daftar kategori unik dari campaign
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT DISTINCT kategori as category
                FROM {self.table_name}
                WHERE is_active = 'Y' AND is_delete = 'N' AND kategori IS NOT NULL
                ORDER BY kategori
            """
            cursor.execute(sql)
            return cursor.fetchall()

    def countAll(self, tipe=None):
        """
        Hitung total campaign
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT COUNT(*) as total
                FROM {self.table_name}
                WHERE is_active = 'Y' AND is_delete = 'N' AND status = 'publish'
            """
            params = []
            if tipe:
                sql += " AND tipe = %s"
                params.append(tipe)
            
            cursor.execute(sql, tuple(params) if params else None)
            result = cursor.fetchone()
            return result['total'] if result else 0
