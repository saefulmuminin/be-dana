-- ========================================================================
-- MIGRATION: Dana Payment Integration
-- Created: 2026-02-03
-- Description: Menambahkan kolom untuk integrasi DANA ke tabel yang sudah ada
-- ========================================================================

-- ========================================================================
-- 1. ALTER TABLE: adm_campaign_donasi
--    Kolom yang sudah ada: id, campaign_id, tipe_zakat, tipe, nama_lengkap,
--    email, npwz, doa_muzaki, nominal, tgl_donasi, metode_id, prosen_biayaoperasional,
--    biayaoperasional, donasi, biaya_admin, status, is_active, is_delete,
--    hamba_allah, no_transaksi, tanggal, waktu, bsz, no_refrensi, nama_refrensi,
--    kode_biller, url_qris, url_deeplink, tgl_expired, transaksi_id, order_id,
--    created_by, updated_by, deleted_by, created_date, updated_date, deleted_date
-- ========================================================================

ALTER TABLE `adm_campaign_donasi`
ADD COLUMN IF NOT EXISTS `uuid` VARCHAR(36) DEFAULT NULL AFTER `id`,                              -- <-- BARU: UUID unik untuk setiap transaksi
ADD COLUMN IF NOT EXISTS `checksum` VARCHAR(64) DEFAULT NULL AFTER `uuid`,                        -- <-- BARU: Checksum SHA256 untuk validasi data
ADD COLUMN IF NOT EXISTS `muzaki_id` INT DEFAULT NULL AFTER `campaign_id`,                        -- <-- BARU: FK ke tabel adm_muzaki
ADD COLUMN IF NOT EXISTS `donasi_net` DECIMAL(15,2) DEFAULT 0 AFTER `donasi`,                     -- <-- BARU: Nominal donasi bersih setelah dikurangi biaya
ADD COLUMN IF NOT EXISTS `total_bayar` DECIMAL(15,2) DEFAULT 0 AFTER `donasi_net`,                -- <-- BARU: Total yang dibayar (nominal + biaya_admin)
ADD COLUMN IF NOT EXISTS `partner_reference_no` VARCHAR(100) DEFAULT NULL AFTER `order_id`,       -- <-- BARU: Partner reference number DANA
ADD COLUMN IF NOT EXISTS `dana_reference_no` VARCHAR(100) DEFAULT NULL AFTER `partner_reference_no`, -- <-- BARU: Reference number dari DANA API
ADD COLUMN IF NOT EXISTS `dana_status` VARCHAR(50) DEFAULT NULL AFTER `dana_reference_no`,        -- <-- BARU: Status dari DANA (SUCCESS/FAILED/PENDING)
ADD COLUMN IF NOT EXISTS `dana_web_redirect_url` VARCHAR(500) DEFAULT NULL AFTER `dana_status`,   -- <-- BARU: URL redirect ke halaman pembayaran DANA
ADD COLUMN IF NOT EXISTS `dana_ott_token` VARCHAR(500) DEFAULT NULL AFTER `dana_web_redirect_url`,-- <-- BARU: One Time Token untuk pembayaran DANA
ADD COLUMN IF NOT EXISTS `dana_paid_at` DATETIME DEFAULT NULL AFTER `dana_ott_token`;             -- <-- BARU: Waktu pembayaran berhasil dari webhook

-- Index untuk kolom baru
ALTER TABLE `adm_campaign_donasi`
ADD INDEX IF NOT EXISTS `idx_uuid` (`uuid`),                            -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_muzaki_id` (`muzaki_id`),                  -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_partner_reference_no` (`partner_reference_no`), -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_dana_reference_no` (`dana_reference_no`),  -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_dana_status` (`dana_status`),              -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_order_id` (`order_id`);                    -- <-- BARU (jika belum ada)


-- ========================================================================
-- 2. ALTER TABLE: users
--    Kolom yang sudah ada: id, ip_address, username, password, email, salt,
--    activation_selector, activation_code, forgotten_password_selector,
--    forgotten_password_code, forgotten_password_time, remember_selector,
--    remember_code, created_on, last_login, active, full_name, nia, tipe,
--    gopay_id, handphone, muzaki_id
-- ========================================================================

ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `dana_access_token` VARCHAR(500) DEFAULT NULL AFTER `muzaki_id`,         -- <-- BARU: Access token dari DANA OAuth
ADD COLUMN IF NOT EXISTS `dana_refresh_token` VARCHAR(500) DEFAULT NULL AFTER `dana_access_token`,-- <-- BARU: Refresh token dari DANA OAuth
ADD COLUMN IF NOT EXISTS `dana_token_expires_at` DATETIME DEFAULT NULL AFTER `dana_refresh_token`,-- <-- BARU: Waktu expired token DANA
ADD COLUMN IF NOT EXISTS `dana_external_id` VARCHAR(100) DEFAULT NULL AFTER `dana_token_expires_at`, -- <-- BARU: External ID dari DANA OAuth flow
ADD COLUMN IF NOT EXISTS `dana_user_id` VARCHAR(100) DEFAULT NULL AFTER `dana_external_id`,       -- <-- BARU: User ID dari DANA
ADD COLUMN IF NOT EXISTS `dana_linked_at` DATETIME DEFAULT NULL AFTER `dana_user_id`;             -- <-- BARU: Waktu pertama kali terhubung dengan DANA

-- Index untuk kolom baru
ALTER TABLE `users`
ADD INDEX IF NOT EXISTS `idx_dana_external_id` (`dana_external_id`),    -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_dana_user_id` (`dana_user_id`);            -- <-- BARU


-- ========================================================================
-- 3. ALTER TABLE: log_api
--    Tambah index untuk query DANA logs (jika belum ada)
-- ========================================================================

ALTER TABLE `log_api`
ADD INDEX IF NOT EXISTS `idx_aplikasi` (`aplikasi`),                    -- <-- BARU
ADD INDEX IF NOT EXISTS `idx_created_date` (`created_date`);            -- <-- BARU


-- ========================================================================
-- 4. INSERT: Metode pembayaran DANA ke ref_metode_pembayaran
--    (hanya jika belum ada)
-- ========================================================================

INSERT INTO `ref_metode_pembayaran`
(`name`, `kelompok`, `url_gambar`, `bank`, `payment_type`, `va_number`,
 `start_amount`, `end_amount`, `order_list`, `biaya_admin`, `tahapan`,
 `is_active`, `is_delete`, `created_date`)
SELECT 'DANA', 'e money', 'dana.png', 'DANA', 'emoney', 0, 10000, 50000000, 1, 0.000,
'1. Pilih metode pembayaran DANA\n2. Anda akan diarahkan ke halaman DANA\n3. Login dengan akun DANA Anda\n4. Konfirmasi pembayaran\n5. Pembayaran berhasil',
'Y', 'N', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM `ref_metode_pembayaran`
    WHERE `payment_type` = 'emoney' AND `bank` = 'DANA'
);                                                                      -- <-- BARU: Data metode pembayaran DANA


-- ========================================================================
-- 5. VIEW: v_dana_transactions untuk melihat transaksi DANA
-- ========================================================================

CREATE OR REPLACE VIEW `v_dana_transactions` AS                         -- <-- BARU: View untuk transaksi DANA
SELECT
    d.id,
    d.uuid,
    d.order_id,
    d.partner_reference_no,
    d.dana_reference_no,
    d.dana_status,
    d.email,
    d.nama_lengkap,
    d.npwz,
    d.nominal,
    d.biaya_admin,
    d.biayaoperasional AS biaya_operasional,
    d.donasi_net,
    d.total_bayar,
    d.status,
    d.tgl_donasi,
    d.dana_paid_at,
    d.hamba_allah,
    d.doa_muzaki,
    c.name AS campaign_name,
    c.tipe AS campaign_tipe,
    m.name AS metode_name,
    mz.nama AS muzaki_nama,
    mz.handphone AS muzaki_phone
FROM adm_campaign_donasi d
LEFT JOIN adm_campaign c ON d.campaign_id = c.id
LEFT JOIN ref_metode_pembayaran m ON d.metode_id = m.id
LEFT JOIN adm_muzaki mz ON d.muzaki_id = mz.id
WHERE d.is_delete = 'N';


-- ========================================================================
-- RINGKASAN KOLOM BARU
-- ========================================================================
/*
TABEL: adm_campaign_donasi
+---------------------------+---------------+----------------------------------------+
| Kolom                     | Tipe          | Keterangan                             |
+---------------------------+---------------+----------------------------------------+
| uuid                      | VARCHAR(36)   | <-- BARU: ID unik transaksi            |
| checksum                  | VARCHAR(64)   | <-- BARU: SHA256 untuk validasi        |
| muzaki_id                 | INT           | <-- BARU: FK ke adm_muzaki             |
| donasi_net                | DECIMAL(15,2) | <-- BARU: Nominal setelah potongan     |
| total_bayar               | DECIMAL(15,2) | <-- BARU: Total pembayaran             |
| partner_reference_no      | VARCHAR(100)  | <-- BARU: Reference dari merchant      |
| dana_reference_no         | VARCHAR(100)  | <-- BARU: Reference dari DANA          |
| dana_status               | VARCHAR(50)   | <-- BARU: Status DANA                  |
| dana_web_redirect_url     | VARCHAR(500)  | <-- BARU: URL redirect pembayaran      |
| dana_ott_token            | VARCHAR(500)  | <-- BARU: One Time Token               |
| dana_paid_at              | DATETIME      | <-- BARU: Waktu bayar berhasil         |
+---------------------------+---------------+----------------------------------------+

TABEL: users
+---------------------------+---------------+----------------------------------------+
| Kolom                     | Tipe          | Keterangan                             |
+---------------------------+---------------+----------------------------------------+
| dana_access_token         | VARCHAR(500)  | <-- BARU: Access token DANA            |
| dana_refresh_token        | VARCHAR(500)  | <-- BARU: Refresh token DANA           |
| dana_token_expires_at     | DATETIME      | <-- BARU: Waktu expired token          |
| dana_external_id          | VARCHAR(100)  | <-- BARU: External ID OAuth            |
| dana_user_id              | VARCHAR(100)  | <-- BARU: User ID DANA                 |
| dana_linked_at            | DATETIME      | <-- BARU: Waktu pertama link DANA      |
+---------------------------+---------------+----------------------------------------+

STATUS MAPPING adm_campaign_donasi.status:
- 'belum'      = pending (belum bayar)
- 'menunggu'   = processing (sedang diproses)
- 'berhasil'   = success (pembayaran berhasil)
- 'dibatalkan' = cancelled/failed (dibatalkan atau gagal)
*/
