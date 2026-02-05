#!/usr/bin/env python3
"""
Script untuk memasukkan data campaign dari API ke database Neon PostgreSQL
"""
import os
import sys
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Campaign data from API
campaigns = [
    {
        "id": "84",
        "judul": "Zakat Fitrah",
        "tipe_zakat": "zakat",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Zakat_Fitrah1.jpg",
        "total_terkumpul": None,
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2026-02-04 11:34:55",
        "start_date": "2026-02-04",
        "end_date": "9999-12-31",
        "abstract": "Zakat fitrah adalah kebiasaan baik yang telah Allah SWT wajibkan kepada kaum muslimin selama di bulan Ramadhan.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "67",
        "judul": "Zakat Penghasilan",
        "tipe_zakat": "zakat",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/paybill-program-banner-1-NOALGD-1732603502437.jpg",
        "total_terkumpul": "607279443",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-12-22 14:40:43",
        "start_date": "2024-12-06",
        "end_date": "9999-12-31",
        "abstract": "Zakat penghasilan adalah kewajiban bagi setiap muslim yang memiliki penghasilan dari pekerjaan yang tidak melanggar syariat.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "59",
        "judul": "Zakat Maal",
        "tipe_zakat": "zakat",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Zakat_Maal_564_x_317_pxl.jpg",
        "total_terkumpul": "644195226",
        "total_kebutuhan": "2000000000",
        "batas_waktu": "18250",
        "created_date": "2025-12-22 14:40:08",
        "start_date": "2022-04-21",
        "end_date": "9999-12-31",
        "abstract": "Ambillah zakat dari harta mereka guna membersihkan dan mensucikan mereka.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "83",
        "judul": "BANTU KORBAN BENCANA SUMATERA",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Cinta_Zakat_Bantu_Korban_Bencana_x_gopay_low_(1).jpg",
        "total_terkumpul": "231368378",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-12-02 13:08:32",
        "start_date": "2025-12-02",
        "end_date": "9999-12-31",
        "abstract": "Bersama BAZNAS & Gopay Peduli Bencana Sumatera. Bencana yang melanda sebagian wilayah Sumatera membuat banyak keluarga kehilangan rumah.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "78",
        "judul": "Solidaritas Peduli Bencana",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Cinta_Zakat_Solidaritas_Peduli_Bencana.jpg",
        "total_terkumpul": "25141886",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-11-28 09:54:34",
        "start_date": "2025-03-12",
        "end_date": "9999-12-31",
        "abstract": "Secara geografis, Indonesia terletak di wilayah Ring of Fire yang membuatnya rentan menghadapi bencana alam.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "26",
        "judul": "Wujudkan Layanan Kesehatan Gratis Bagi Mustahik",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/bantu-mustahik-sehat.jpg",
        "total_terkumpul": "3194887",
        "total_kebutuhan": "10000000",
        "batas_waktu": "18250",
        "created_date": "2025-11-25 12:18:12",
        "start_date": "2022-03-26",
        "end_date": "2072-12-08",
        "abstract": "Saya ingin bisa berobat gratis. Bagi masyarakat yang kurang mampu, seringkali berobat menjadi hal yang sulit.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "63",
        "judul": "Bantu Jutaan Muslim Palestina",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Cinta_Zakat_Membasuh_Luka_Palestina_Update_low_(1)2.jpg",
        "total_terkumpul": "74730004",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-11-20 11:27:44",
        "start_date": "2024-08-08",
        "end_date": "2178-05-30",
        "abstract": "Barangsiapa yang meringankan penderitaan seorang Mukmin di dunia, niscaya Allah akan meringankan penderitaannya.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "64",
        "judul": "Solidaritas Dunia Islam",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Cinta_Zakat_-_SDI.jpg",
        "total_terkumpul": "14581753",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-10-01 10:20:18",
        "start_date": "2024-10-17",
        "end_date": "9999-12-31",
        "abstract": "Barangsiapa yang meringankan penderitaan seorang Mukmin di dunia, niscaya Allah akan meringankan penderitaannya.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "23",
        "judul": "Sedekah Subuh",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Cinta_Zakat_Sedekah_Subuh_(1).jpg",
        "total_terkumpul": "131773521",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-03-25 10:39:56",
        "start_date": "2022-03-12",
        "end_date": "9999-12-31",
        "abstract": "Tidak ada satu subuh pun yang dialami hamba-hamba Allah kecuali turun kepada mereka dua malaikat.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    },
    {
        "id": "65",
        "judul": "Sedekah Muliakan Yatim",
        "tipe_zakat": "infak",
        "kategori": "Lainnya",
        "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Banner_Sedekah_Yatim.jpg",
        "total_terkumpul": "49707893",
        "total_kebutuhan": "1000000000",
        "batas_waktu": "18250",
        "created_date": "2025-03-21 15:33:36",
        "start_date": "2024-10-21",
        "end_date": "9999-12-31",
        "abstract": "Memperbaiki keadaan anak yatim adalah baik. Aku dan orang yang mengasuh anak yatim akan bersama di surga.",
        "nama_lembaga": "BAZNAS RI (Pusat)",
        "kode_institusi": "3171100"
    }
]

def slugify(text):
    """Convert text to slug format"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def parse_date(date_str):
    """Parse date string to date object"""
    if not date_str:
        return None
    try:
        # Handle "9999-12-31" as max date
        if date_str.startswith("9999"):
            return datetime(9999, 12, 31).date()
        return datetime.strptime(date_str.split()[0], "%Y-%m-%d").date()
    except:
        return None

def parse_datetime(dt_str):
    """Parse datetime string"""
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except:
        return None

def main():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in .env")
        return

    print(f"Connecting to database...")

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # First, check existing campaigns
        cursor.execute("SELECT id, name FROM adm_campaign ORDER BY id")
        existing = cursor.fetchall()
        print(f"\nExisting campaigns: {len(existing)}")
        for row in existing:
            print(f"  ID: {row[0]}, Name: {row[1]}")

        # Insert/Update campaigns using UPSERT
        print(f"\nInserting {len(campaigns)} campaigns...")

        for camp in campaigns:
            campaign_id = int(camp['id'])
            slug = slugify(camp['judul'])
            donasi = int(camp['total_terkumpul']) if camp['total_terkumpul'] else 0
            target = int(camp['total_kebutuhan']) if camp['total_kebutuhan'] else 0
            kode_institusi = int(camp['kode_institusi']) if camp['kode_institusi'] else None

            # Check if exists
            cursor.execute("SELECT id FROM adm_campaign WHERE id = %s", (campaign_id,))
            exists = cursor.fetchone()

            if exists:
                # Update
                cursor.execute("""
                    UPDATE adm_campaign SET
                        kode_institusi = %s,
                        tipe = %s,
                        kategori = %s,
                        name = %s,
                        slug = %s,
                        target_donasi = %s,
                        start_date = %s,
                        end_date = %s,
                        donasi = %s,
                        url_fotoutama = %s,
                        informasi = %s,
                        is_active = 'Y',
                        is_delete = 'N',
                        updated_date = NOW()
                    WHERE id = %s
                """, (
                    kode_institusi,
                    camp['tipe_zakat'],
                    camp['kategori'],
                    camp['judul'],
                    slug,
                    target,
                    parse_date(camp['start_date']),
                    parse_date(camp['end_date']),
                    donasi,
                    camp['url_gambar'],
                    camp['abstract'],
                    campaign_id
                ))
                print(f"  Updated ID {campaign_id}: {camp['judul']}")
            else:
                # Insert with specific ID
                cursor.execute("""
                    INSERT INTO adm_campaign (
                        id, kode_institusi, tipe, program_id, kategori, name, slug,
                        target_donasi, start_date, end_date, donasi, url_fotoutama,
                        informasi, campaign_latitude, campaign_longitude,
                        is_active, is_delete, program_pilihan, prioritas, created_date
                    ) VALUES (
                        %s, %s, %s, 1, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, '0', '0',
                        'Y', 'N', 'N', 'N', %s
                    )
                """, (
                    campaign_id,
                    kode_institusi,
                    camp['tipe_zakat'],
                    camp['kategori'],
                    camp['judul'],
                    slug,
                    target,
                    parse_date(camp['start_date']),
                    parse_date(camp['end_date']),
                    donasi,
                    camp['url_gambar'],
                    camp['abstract'],
                    parse_datetime(camp['created_date'])
                ))
                print(f"  Inserted ID {campaign_id}: {camp['judul']}")

        # Update sequence to max id
        cursor.execute("SELECT MAX(id) FROM adm_campaign")
        max_id = cursor.fetchone()[0]
        if max_id:
            cursor.execute(f"SELECT setval('adm_campaign_id_seq', {max_id}, true)")
            print(f"\nSequence updated to {max_id}")

        conn.commit()
        print("\n✓ All campaigns inserted/updated successfully!")

        # Verify
        cursor.execute("SELECT id, name, tipe, donasi FROM adm_campaign ORDER BY id")
        all_campaigns = cursor.fetchall()
        print(f"\nTotal campaigns in database: {len(all_campaigns)}")
        for row in all_campaigns:
            print(f"  ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, Donasi: {row[3]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
