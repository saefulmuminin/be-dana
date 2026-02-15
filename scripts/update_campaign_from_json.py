#!/usr/bin/env python3
"""
Script untuk update campaign data dari JSON export
Termasuk update donasi terkumpul dari sistem lama
"""
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.database import db

# Data dari JSON export
campaigns_json = [
    {"id":23,"donasi":131773521,"target_donasi":1000000000,"informasi":"Tidak ada satu subuh pun yang dialami hamba-hamba Allah kecuali turun kepada mereka dua malaikat. Salah satu di antara keduanya berdoa, 'Ya Allah, berikanlah ganti bagi orang yang berinfak', sedangkan yang satunya lagi berdoa 'Ya Allah, berilah kerusakan pada orang yang menahan hartanya.' (HR. Bukhari dan Muslim).\n\nSabda Rasulullah SAW, \"Sesungguhnya Allah SWT menerima sedekah dan mengambilnya dengan tangan kanan-Nya, lalu Dia mengembangkannya untuk salah seorang di antara kalian sebagaimana salah seorang di antara kalian mengembangkan anak kudanya, sehingga suapan (yang disedekahkan) itu menjadi seperti gunung Uhud.\" (HR. Bukhari dan Muslim).\n\nMari bersedekah di waktu subuh untuk meraih keberkahan dan pahala berlimpah dari Allah SWT."},
    {"id":26,"donasi":3194887,"target_donasi":10000000,"informasi":"\"Saya ingin bisa berobat gratis…\"\n\nItulah secercah kalimat yang seringkali tim Rumah Sehat BAZNAS dengar saat melakukan giat pelayanan kesehatan terbaik ke wilayah pemukiman warga.\n\nBagi masyarakat yang kurang mampu, seringkali berobat menjadi hal yang sangat mahal dan memberatkan. Bahkan untuk mendapatkan layanan kesehatan dasar pun, mereka harus mengeluarkan biaya yang tidak sedikit.\n\nBAZNAS RI hadir untuk mewujudkan akses layanan kesehatan gratis bagi mustahik melalui program Rumah Sehat. Dengan dukungan Anda, ribuan keluarga mustahik dapat menerima layanan kesehatan berkualitas tanpa dipungut biaya.\n\nMari bersama-sama wujudkan Indonesia Sehat dengan berdonasi untuk Rumah Sehat BAZNAS."},
    {"id":59,"donasi":644195226,"target_donasi":2000000000,"informasi":"\"Ambillah zakat dari harta mereka guna membersihkan dan mensucikan mereka dan berdoalah untuk mereka. Sesungguhnya doamu itu (menumbuhkan) ketentraman jiwa bagi mereka. Allah Maha Mendengar, Maha Mengetahui.\" (QS. At-Taubah: 103).\n\nMaal berasal dari bahasa Arab yang artinya harta atau kekayaan. Zakat maal adalah zakat yang dikenakan atas segala jenis harta yang secara zat maupun substansi tidak bertentangan dengan ketentuan agama Islam.\n\nZakat maal mencakup:\n- Uang dan surat berharga lainnya\n- Emas dan perak\n- Perdagangan dan investasi\n- Hasil pertanian, perkebunan dan perikanan\n- Hasil pertambangan\n- Hasil peternakan\n- Hasil pendapatan dan jasa\n- Rikaz (harta temuan)\n\nNisab zakat maal setara dengan 85 gram emas dan haulnya selama 1 tahun. Kadar zakat yang harus dikeluarkan adalah 2.5%."},
    {"id":63,"donasi":74730004,"target_donasi":1000000000,"informasi":"Barangsiapa yang meringankan penderitaan seorang Mukmin di dunia, niscaya Allah akan meringankan penderitaan (kesulitan)nya kelak di hari kiamat dan barangsiapa yang memudahkan urusan orang yang mengalami kesulitan, niscaya Allah akan memudahkan urusannya di dunia dan di akhirat. (HR. Muslim).\n\nKonflik yang berkepanjangan di Palestina telah menimbulkan penderitaan luar biasa bagi jutaan Muslim di sana. Mereka kehilangan rumah, kehilangan keluarga, dan kehilangan harapan untuk masa depan yang lebih baik.\n\nBAZNAS RI sebagai lembaga resmi pengelola zakat nasional terus berupaya menyalurkan bantuan kemanusiaan untuk saudara-saudara kita di Palestina melalui lembaga mitra yang terpercaya.\n\nBantu meringankan penderitaan mereka dengan berdonasi melalui BAZNAS RI. Insya Allah bantuan Anda akan tersalurkan dengan amanah dan tepat sasaran."},
    {"id":64,"donasi":14581753,"target_donasi":1000000000,"informasi":"\"Barangsiapa yang meringankan penderitaan seorang Mukmin di dunia, niscaya Allah akan meringankan penderitaan (kesulitan)nya kelak di hari kiamat dan barangsiapa yang memudahkan urusan orang yang mengalami kesulitan, niscaya Allah akan memudahkan urusannya di dunia dan di akhirat.\" (HR. Muslim).\n\nDi berbagai belahan dunia Islam, banyak saudara-saudara kita yang mengalami musibah dan kesulitan. Mulai dari konflik bersenjata, bencana alam, hingga kemiskinan ekstrem.\n\nBAZNAS RI melalui program Solidaritas Dunia Islam hadir untuk menjadi jembatan kebaikan Anda dalam membantu sesama Muslim di berbagai negara yang membutuhkan.\n\nBersama BAZNAS RI, mari bersatu dalam kebaikan dan meringankan beban saudara-saudara kita di seluruh dunia."},
    {"id":65,"donasi":49707893,"target_donasi":1000000000,"informasi":"\"Aku dan orang yang mengasuh anak yatim akan bersama-sama di surga seperti ini,\" Rasulullah SAW mengisyaratkan dengan jari telunjuk dan jari tengahnya. (HR. Bukhari).\n\n\"Barangsiapa mengusap kepala anak yatim, tidak lain hanya karena Allah, maka baginya dengan setiap rambut yang diusapnya akan mendapat kebaikan. Dan barangsiapa yang berbuat baik terhadap anak yatim, baik perempuan atau laki-laki yang ada bersamanya, maka aku akan bersamanya di surga seperti ini,\" beliau menunjukkan jari telunjuk dan jari tengahnya. (HR. Ahmad).\n\nAnak yatim adalah amanah Allah yang harus kita jaga dan kasihi. Mereka membutuhkan perhatian, kasih sayang, dan dukungan untuk tumbuh menjadi generasi yang tangguh.\n\nBAZNAS RI mengajak Anda untuk bersedekah memuliakan anak yatim melalui berbagai program pendidikan, kesehatan, dan pemberdayaan."},
    {"id":67,"donasi":607279443,"target_donasi":1000000000,"informasi":"Zakat penghasilan adalah kewajiban bagi setiap muslim yang memiliki penghasilan dari pekerjaan yang tidak melanggar syariat, baik berupa gaji, honorarium, upah, jasa, atau pendapatan lainnya.\n\nDasar hukum zakat penghasilan:\n\"Hai orang-orang yang beriman, nafkahkanlah (di jalan Allah) sebagian dari hasil usahamu yang baik-baik dan sebagian dari apa yang Kami keluarkan dari bumi untuk kamu.\" (QS. Al-Baqarah: 267)\n\nNisab zakat penghasilan adalah setara dengan 85 gram emas per tahun atau 520 kg beras per tahun. Jika penghasilan Anda dalam setahun melebihi nisab tersebut, maka wajib mengeluarkan zakat sebesar 2.5%.\n\nZakat penghasilan dapat ditunaikan setiap bulan dengan cara:\nPenghasilan bersih per bulan x 2.5%\n\nContoh: Gaji Rp 10.000.000/bulan\nZakat = Rp 10.000.000 x 2.5% = Rp 250.000\n\nTunaikan zakat penghasilan Anda melalui BAZNAS RI untuk membantu saudara-saudara yang membutuhkan."},
    {"id":78,"donasi":25141886,"target_donasi":1000000000,"informasi":"Secara geografis, Indonesia terletak di wilayah 'Ring of Fire' yang membuatnya rentan menghadapi bencana alam seperti gempa bumi, gunung meletus, banjir, longsor, tsunami, dan lainnya. Setiap bencana yang terjadi selalu meninggalkan duka dan kerugian mendalam bagi saudara-saudara kita yang terdampak.\n\n\"Tidaklah seorang Mukmin merasakan duri (atau lebih dari itu) yang menusuknya, melainkan Allah akan menghapus kesalahannya dan akan mengugurkan dosa-dosanya seperti gugurnya daun dari pohonnya.\" (HR. Bukhari dan Muslim).\n\nBAZNAS RI sebagai lembaga resmi pengelola zakat nasional senantiasa siaga dalam memberikan bantuan darurat bencana dan pemulihan pasca bencana untuk membantu para korban.\n\nProgram Solidaritas Peduli Bencana meliputi:\n- Bantuan darurat (makanan, air bersih, selimut, dll)\n- Layanan kesehatan darurat\n- Penyediaan tempat hunian sementara\n- Trauma healing dan dukungan psikososial\n- Rekonstruksi dan rehabilitasi\n\nMari bersama-sama meringankan beban saudara-saudara kita yang terdampak bencana."},
    {"id":83,"donasi":231368378,"target_donasi":1000000000,"informasi":"Bersama BAZNAS & Gopay Peduli Bencana Sumatera\n\nBencana yang melanda sebagian wilayah Sumatera membuat banyak keluarga tiba-tiba kehilangan rumah, pakaian, dan rasa aman. Anak-anak terpaksa berlindung di pengungsian dengan pakaian seadanya, orang tua mencari-cari sisa-sisa harta benda yang masih bisa diselamatkan.\n\nDi tengah kesedihan mereka, ada harapan yang datang dari kepedulian kita bersama.\n\n\"Perumpamaan orang-orang yang menafkahkan hartanya di jalan Allah adalah serupa dengan sebutir benih yang menumbuhkan tujuh bulir, pada tiap-tiap bulir seratus biji. Allah melipat gandakan (ganjaran) bagi siapa yang Dia kehendaki. Dan Allah Maha Luas (karunia-Nya) lagi Maha Mengetahui.\" (QS. Al-Baqarah: 261)\n\nBAZNAS berkolaborasi dengan Gopay untuk memberikan bantuan cepat dan tepat kepada korban bencana di Sumatera. Bantuan yang diberikan meliputi:\n- Makanan dan air bersih\n- Pakaian dan selimut\n- Obat-obatan dan layanan kesehatan\n- Hunian sementara\n- Kebutuhan dasar lainnya\n\nBersama kita bisa meringankan beban mereka. Mari salurkan donasi Anda sekarang!"},
    {"id":84,"donasi":0,"target_donasi":1000000000,"informasi":"Zakat fitrah adalah kebiasaan baik yang telah Allah SWT wajibkan kepada kaum muslimin selama di bulan Ramadhan. Zakat fitrah wajib ditunaikan oleh setiap Muslim yang mampu untuk mensucikan diri dari perbuatan sia-sia dan perkataan keji selama bulan Ramadhan, sekaligus untuk memberi makan orang-orang miskin.\n\n\"Rasulullah SAW mewajibkan zakat fitrah untuk mensucikan diri orang puasa dari perbuatan sia-sia dan perkataan keji dan kotor, sekaligus untuk memberi makan orang-orang miskin.\" (HR. Abu Daud).\n\nZakat fitrah wajib ditunaikan oleh setiap jiwa Muslim yang mampu, baik laki-laki maupun perempuan, dewasa maupun anak-anak. Waktu pembayaran zakat fitrah yang paling utama adalah sebelum shalat Idul Fitri.\n\nBesaran zakat fitrah:\n- 2.5 kg atau 3.5 liter beras per jiwa\n- Atau senilai harga beras tersebut dalam bentuk uang\n\nTunaikan zakat fitrah Anda melalui BAZNAS RI agar tersalurkan kepada yang berhak dengan amanah dan tepat waktu.\n\nJadikan Idul Fitri bermakna bagi sesama dengan berbagi kebahagiaan kepada saudara-saudara kita yang membutuhkan."}
]

def main():
    print("=" * 70)
    print("UPDATE CAMPAIGN DATA FROM JSON")
    print("=" * 70)
    print()

    conn = db.getConnection()
    cursor = conn.cursor()

    updated_count = 0

    for camp in campaigns_json:
        campaign_id = camp['id']
        donasi = camp.get('donasi', 0)
        target_donasi = camp.get('target_donasi', 0)
        informasi = camp.get('informasi', '')

        try:
            # Update campaign dengan informasi lengkap
            cursor.execute("""
                UPDATE adm_campaign
                SET
                    donasi = %s,
                    target_donasi = %s,
                    informasi = %s,
                    updated_date = NOW()
                WHERE id = %s
            """, (donasi, target_donasi, informasi, campaign_id))

            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✓ Updated Campaign ID {campaign_id}")
                print(f"  Target: Rp {target_donasi:,}")
                print(f"  Donasi (from old system): Rp {donasi:,}")
                print(f"  Informasi: {len(informasi)} characters")
                print()
            else:
                print(f"⚠ Campaign ID {campaign_id} not found")
                print()

        except Exception as e:
            print(f"✗ Error updating campaign {campaign_id}: {str(e)}")
            print()

    conn.commit()

    print("=" * 70)
    print(f"✓ Updated {updated_count} campaigns")
    print("=" * 70)
    print()

    # Verify updates
    print("Verifying updates...")
    print()

    cursor.execute("""
        SELECT id, name, target_donasi, donasi,
               LENGTH(informasi) as info_length
        FROM adm_campaign
        WHERE id IN (23, 26, 59, 63, 64, 65, 67, 78, 83, 84)
        ORDER BY id
    """)

    results = cursor.fetchall()

    print(f"{'ID':<5} {'Campaign':<40} {'Target':<15} {'Donasi':<15} {'Info':<10}")
    print("-" * 85)

    for row in results:
        print(f"{row['id']:<5} {row['name'][:38]:<40} "
              f"Rp {row['target_donasi']:>12,} "
              f"Rp {row['donasi']:>12,} "
              f"{row['info_length']:>7} ch")

    cursor.close()
    conn.close()

    print()
    print("✓ Done! You can now test the API:")
    print("  POST https://be-dana.vercel.app/api/v1/kegiatan/detail")
    print("  Body: {\"id\": \"67\"}")


if __name__ == "__main__":
    main()
