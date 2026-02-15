#!/usr/bin/env python3
"""
Script untuk membuat sample donations di berbagai campaign
Untuk testing tampilan total_terkumpul di mini app
"""
import os
import sys
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.database import db

# Sample donations for different campaigns
sample_donations = [
    # Zakat Fitrah (ID 84)
    {"campaign_id": 84, "nama": "Ahmad Yusuf", "email": "ahmad@example.com", "nominal": 50000, "doa": "Semoga berkah"},
    {"campaign_id": 84, "nama": "Hamba Allah", "email": "hamba1@example.com", "nominal": 50000, "doa": "", "hamba_allah": "Y"},
    {"campaign_id": 84, "nama": "Siti Nurhaliza", "email": "siti@example.com", "nominal": 100000, "doa": "Untuk keluarga"},

    # Zakat Maal (ID 59)
    {"campaign_id": 59, "nama": "Budi Santoso", "email": "budi@example.com", "nominal": 500000, "doa": "Zakat harta"},
    {"campaign_id": 59, "nama": "Hamba Allah", "email": "hamba2@example.com", "nominal": 250000, "doa": "", "hamba_allah": "Y"},
    {"campaign_id": 59, "nama": "Dewi Lestari", "email": "dewi@example.com", "nominal": 1000000, "doa": "Semoga bermanfaat"},

    # Bantu Palestina (ID 63)
    {"campaign_id": 63, "nama": "Hamba Allah", "email": "hamba3@example.com", "nominal": 100000, "doa": "", "hamba_allah": "Y"},
    {"campaign_id": 63, "nama": "Muhammad Rizki", "email": "rizki@example.com", "nominal": 200000, "doa": "Untuk Palestina"},
    {"campaign_id": 63, "nama": "Hamba Allah", "email": "hamba4@example.com", "nominal": 150000, "doa": "", "hamba_allah": "Y"},

    # Sedekah Subuh (ID 23)
    {"campaign_id": 23, "nama": "Fatimah Az-Zahra", "email": "fatimah@example.com", "nominal": 25000, "doa": "Sedekah pagi"},
    {"campaign_id": 23, "nama": "Hamba Allah", "email": "hamba5@example.com", "nominal": 50000, "doa": "", "hamba_allah": "Y"},
    {"campaign_id": 23, "nama": "Abdullah Malik", "email": "abdullah@example.com", "nominal": 75000, "doa": "Barakallah"},

    # Sedekah Yatim (ID 65)
    {"campaign_id": 65, "nama": "Hamba Allah", "email": "hamba6@example.com", "nominal": 100000, "doa": "", "hamba_allah": "Y"},
    {"campaign_id": 65, "nama": "Aisyah Ramadhani", "email": "aisyah@example.com", "nominal": 200000, "doa": "Untuk anak yatim"},
    {"campaign_id": 65, "nama": "Umar Faruq", "email": "umar@example.com", "nominal": 150000, "doa": "Semoga berkah"},

    # Bantu Sumatera (ID 83)
    {"campaign_id": 83, "nama": "Hamba Allah", "email": "hamba7@example.com", "nominal": 300000, "doa": "", "hamba_allah": "Y"},
    {"campaign_id": 83, "nama": "Khadijah", "email": "khadijah@example.com", "nominal": 500000, "doa": "Untuk korban bencana"},

    # Solidaritas Peduli Bencana (ID 78)
    {"campaign_id": 78, "nama": "Ali Imran", "email": "ali@example.com", "nominal": 250000, "doa": "Semoga cepat pulih"},
    {"campaign_id": 78, "nama": "Hamba Allah", "email": "hamba8@example.com", "nominal": 100000, "doa": "", "hamba_allah": "Y"},
]

def generate_order_id():
    """Generate order ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices('ABCDEF0123456789', k=8))
    return f"SAMPLE-{timestamp}-{random_str}"

def create_donations():
    """Create sample donations"""
    print("=" * 70)
    print("CREATE SAMPLE DONATIONS FOR TESTING")
    print("=" * 70)
    print()

    conn = db.getConnection()
    cursor = conn.cursor()

    created_count = 0

    for i, don in enumerate(sample_donations, 1):
        # Generate random date in the past 7 days
        days_ago = random.randint(1, 7)
        hours_ago = random.randint(0, 23)
        paid_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

        order_id = generate_order_id()

        try:
            cursor.execute("""
                INSERT INTO adm_campaign_donasi (
                    campaign_id, order_id, partner_reference_no,
                    nama_lengkap, email, nominal,
                    status, dana_status, dana_paid_at, tgl_donasi,
                    doa_muzaki, hamba_allah, tipe_zakat, tipe,
                    metode_id, biaya_admin, total_bayar,
                    is_active, is_delete, created_date, created_by
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    'berhasil', 'SUCCESS', %s, %s,
                    %s, %s, 'infak', 'perorangan',
                    1, 0, %s,
                    'Y', 'N', %s, 'system'
                )
            """, (
                don['campaign_id'],
                order_id,
                order_id,
                don['nama'],
                don['email'],
                don['nominal'],
                paid_at,
                paid_at.date(),
                don.get('doa', ''),
                don.get('hamba_allah', 'N'),
                don['nominal'],
                paid_at
            ))

            created_count += 1

            print(f"✓ [{i}/{len(sample_donations)}] Created donation")
            print(f"  Campaign ID: {don['campaign_id']}")
            print(f"  Nama: {don['nama']}")
            print(f"  Nominal: Rp {don['nominal']:,}")
            print(f"  Order ID: {order_id}")
            print()

        except Exception as e:
            print(f"✗ Error creating donation: {str(e)}")
            print()

    conn.commit()

    print("=" * 70)
    print(f"✓ Created {created_count} sample donations")
    print("=" * 70)
    print()

    # Show summary per campaign
    print("Summary per Campaign:")
    print()

    cursor.execute("""
        SELECT
            c.id,
            c.name,
            COUNT(d.id) as total_donations,
            COALESCE(SUM(d.nominal), 0) as total_amount
        FROM adm_campaign c
        LEFT JOIN adm_campaign_donasi d
            ON c.id = d.campaign_id
            AND d.status = 'berhasil'
            AND d.is_delete = 'N'
        WHERE c.id IN (23, 59, 63, 65, 67, 78, 83, 84)
        GROUP BY c.id, c.name
        ORDER BY c.id
    """)

    results = cursor.fetchall()

    print(f"{'ID':<5} {'Campaign':<40} {'Donations':<12} {'Total':<15}")
    print("-" * 72)

    for row in results:
        print(f"{row['id']:<5} {row['name'][:38]:<40} "
              f"{row['total_donations']:>10} "
              f"Rp {row['total_amount']:>12,}")

    cursor.close()
    conn.close()

    print()
    print("✓ Test API now:")
    print("  curl -X POST https://be-dana.vercel.app/api/v1/kegiatan/index \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"limit\": 10, \"offset\": 0}'")

if __name__ == "__main__":
    create_donations()
