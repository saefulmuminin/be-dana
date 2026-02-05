-- --------------------------------------------------------
-- PostgreSQL Schema for Cinta Zakat Database
-- Converted from MySQL schema.sql
-- Created: 2026-02-04
-- --------------------------------------------------------

-- Create database (run separately if needed)
-- CREATE DATABASE cintazak_dbcintazakat;

-- Set timezone
SET timezone = 'UTC';

-- ========================================================================
-- ENUM TYPES
-- ========================================================================

CREATE TYPE enum_zakat_infak AS ENUM ('zakat', 'infak');
CREATE TYPE enum_perorangan_lembaga AS ENUM ('perorangan', 'lembaga');
CREATE TYPE enum_perorangan_kelompok AS ENUM ('perorangan', 'kelompok');
CREATE TYPE enum_yes_no AS ENUM ('Y', 'N');
CREATE TYPE enum_status_donasi AS ENUM ('belum', 'berhasil', 'menunggu', 'dibatalkan');
CREATE TYPE enum_status_campaign AS ENUM ('draft', 'publish', 'closed');
CREATE TYPE enum_status_histori AS ENUM ('draft', 'simpan', 'edit', 'perpanjangan');
CREATE TYPE enum_status_pembayaran AS ENUM ('draft', 'belum', 'sudah', 'kembali');
CREATE TYPE enum_kelompok_institusi AS ENUM ('BAZNAS_prov', 'BAZNAS_kab', 'LAZ_prov', 'LAZ_kab', 'UPZ', 'LAZNAS', 'Pusat');
CREATE TYPE enum_kelompok_metode AS ENUM ('pembayaran instan', 'virtual account', 'transfer bank', 'internet banking', 'counter store', 'e money', 'credit card');
CREATE TYPE enum_menu_location AS ENUM ('Backend', 'Frontend');
CREATE TYPE enum_menu_type AS ENUM ('module', 'page', 'uri', 'url');
CREATE TYPE enum_target AS ENUM ('_blank', '_self');
CREATE TYPE enum_nav_type AS ENUM ('label', 'link');
CREATE TYPE enum_nav_position AS ENUM ('Main', 'Top', 'Bottom');
CREATE TYPE enum_page_status AS ENUM ('draft', 'live');
CREATE TYPE enum_gender AS ENUM ('pria', 'wanita', '');
CREATE TYPE enum_gender_mf AS ENUM ('m', 'f', '');
CREATE TYPE enum_tipe_laporan AS ENUM ('bulanan', 'tahunan');
CREATE TYPE enum_banner_view AS ENUM ('random', 'slide');
CREATE TYPE enum_dana_environment AS ENUM ('sandbox', 'production');
CREATE TYPE enum_biaya_admin_type AS ENUM ('percentage', 'fixed');
CREATE TYPE enum_dana_payment_status AS ENUM ('pending', 'processing', 'success', 'failed', 'expired', 'cancelled');
CREATE TYPE enum_signature_valid AS ENUM ('Y', 'N', 'UNCHECKED');


-- ========================================================================
-- TABLE: adm_campaign
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign (
  id SERIAL PRIMARY KEY,
  kode_institusi INTEGER DEFAULT NULL,
  tipe enum_zakat_infak NOT NULL,
  program_id INTEGER NOT NULL,
  kategori VARCHAR(150) NOT NULL,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(255) NOT NULL,
  target_donasi BIGINT DEFAULT NULL,
  start_date DATE DEFAULT NULL,
  end_date DATE DEFAULT NULL,
  bataswaktu_id INTEGER DEFAULT NULL,
  link_campaign VARCHAR(100) DEFAULT NULL,
  prosen_biayaoperasional DECIMAL(10,2) DEFAULT NULL,
  biayaoperasional BIGINT DEFAULT 0,
  donasi BIGINT DEFAULT NULL,
  url_fotoutama VARCHAR(100) DEFAULT NULL,
  no_rekening VARCHAR(30) DEFAULT NULL,
  nama_bank VARCHAR(100) DEFAULT NULL,
  atas_nama VARCHAR(100) DEFAULT NULL,
  coa_infak VARCHAR(20) DEFAULT NULL,
  coaid_infak INTEGER DEFAULT NULL,
  coa_zakat VARCHAR(20) DEFAULT NULL,
  coaid_zakat INTEGER DEFAULT NULL,
  informasi TEXT,
  mustahik_nama VARCHAR(150) DEFAULT NULL,
  tipe_mustahik enum_perorangan_kelompok DEFAULT NULL,
  nik_mustahik VARCHAR(25) DEFAULT NULL,
  hp_mustahik VARCHAR(25) DEFAULT NULL,
  email_mustahik VARCHAR(100) DEFAULT NULL,
  alamat_mustahik TEXT,
  campaign_latitude VARCHAR(50) NOT NULL,
  campaign_longitude VARCHAR(50) NOT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL,
  status enum_status_campaign DEFAULT NULL,
  program_pilihan enum_yes_no NOT NULL,
  prioritas enum_yes_no NOT NULL,
  closed_date TIMESTAMP DEFAULT NULL,
  closed_by VARCHAR(50) DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_campaign_donasi
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_donasi (
  id SERIAL PRIMARY KEY,
  uuid VARCHAR(36) DEFAULT NULL,
  checksum VARCHAR(64) DEFAULT NULL,
  campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  muzaki_id INTEGER DEFAULT NULL,
  tipe_zakat enum_zakat_infak NOT NULL,
  tipe enum_perorangan_lembaga NOT NULL,
  nama_lengkap VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  npwz VARCHAR(100) DEFAULT NULL,
  doa_muzaki VARCHAR(200) DEFAULT NULL,
  nominal BIGINT DEFAULT NULL,
  tgl_donasi DATE DEFAULT NULL,
  metode_id INTEGER DEFAULT NULL,
  prosen_biayaoperasional DECIMAL(10,2) DEFAULT NULL,
  biayaoperasional BIGINT DEFAULT NULL,
  donasi BIGINT DEFAULT NULL,
  donasi_net DECIMAL(15,2) DEFAULT 0,
  total_bayar DECIMAL(15,2) DEFAULT 0,
  biaya_admin BIGINT DEFAULT NULL,
  status enum_status_donasi DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  hamba_allah enum_yes_no DEFAULT 'N',
  no_transaksi VARCHAR(50) DEFAULT NULL,
  tanggal VARCHAR(20) DEFAULT NULL,
  waktu VARCHAR(20) DEFAULT NULL,
  bsz VARCHAR(200) DEFAULT NULL,
  no_refrensi VARCHAR(200) DEFAULT NULL,
  nama_refrensi VARCHAR(200) DEFAULT NULL,
  kode_biller VARCHAR(200) DEFAULT NULL,
  url_qris VARCHAR(200) DEFAULT NULL,
  url_deeplink VARCHAR(255) DEFAULT NULL,
  tgl_expired TIMESTAMP DEFAULT NULL,
  transaksi_id VARCHAR(50) DEFAULT NULL,
  order_id VARCHAR(50) DEFAULT NULL,
  partner_reference_no VARCHAR(100) DEFAULT NULL,
  dana_reference_no VARCHAR(100) DEFAULT NULL,
  dana_status VARCHAR(50) DEFAULT NULL,
  dana_web_redirect_url VARCHAR(500) DEFAULT NULL,
  dana_ott_token VARCHAR(500) DEFAULT NULL,
  dana_paid_at TIMESTAMP DEFAULT NULL,
  dana_payment_id INTEGER DEFAULT NULL,
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_donasi_campaign_id ON adm_campaign_donasi(campaign_id);
CREATE INDEX idx_donasi_uuid ON adm_campaign_donasi(uuid);
CREATE INDEX idx_donasi_muzaki_id ON adm_campaign_donasi(muzaki_id);
CREATE INDEX idx_donasi_partner_reference_no ON adm_campaign_donasi(partner_reference_no);
CREATE INDEX idx_donasi_dana_reference_no ON adm_campaign_donasi(dana_reference_no);
CREATE INDEX idx_donasi_dana_status ON adm_campaign_donasi(dana_status);
CREATE INDEX idx_donasi_order_id ON adm_campaign_donasi(order_id);
CREATE INDEX idx_donasi_dana_payment_id ON adm_campaign_donasi(dana_payment_id);


-- ========================================================================
-- TABLE: adm_campaign_histori
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_histori (
  id SERIAL PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  tipe enum_zakat_infak NOT NULL,
  program_id INTEGER NOT NULL,
  kategori VARCHAR(150) NOT NULL,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(255) DEFAULT NULL,
  target_donasi BIGINT DEFAULT NULL,
  start_date DATE DEFAULT NULL,
  end_date DATE DEFAULT NULL,
  bataswaktu_id INTEGER DEFAULT NULL,
  link_campaign VARCHAR(100) DEFAULT NULL,
  prosen_biayaoperasional DECIMAL(10,2) DEFAULT NULL,
  biayaoperasional BIGINT DEFAULT NULL,
  donasi BIGINT DEFAULT NULL,
  donasi_infak BIGINT DEFAULT NULL,
  donasi_zakat BIGINT DEFAULT NULL,
  url_fotoutama VARCHAR(100) DEFAULT NULL,
  no_rekening VARCHAR(30) DEFAULT NULL,
  nama_bank VARCHAR(100) DEFAULT NULL,
  atas_nama VARCHAR(100) DEFAULT NULL,
  coa_infak VARCHAR(20) DEFAULT NULL,
  coaid_infak INTEGER DEFAULT NULL,
  coa_zakat VARCHAR(20) DEFAULT NULL,
  coaid_zakat INTEGER DEFAULT NULL,
  informasi TEXT,
  mustahik_nama VARCHAR(150) DEFAULT NULL,
  tipe_mustahik enum_perorangan_kelompok DEFAULT NULL,
  nik_mustahik VARCHAR(25) DEFAULT NULL,
  hp_mustahik VARCHAR(25) DEFAULT NULL,
  email_mustahik VARCHAR(100) DEFAULT NULL,
  alamat_mustahik TEXT,
  campaign_latitude VARCHAR(50) NOT NULL,
  campaign_longitude VARCHAR(50) NOT NULL,
  status_histori VARCHAR(100) DEFAULT NULL,
  log_histori TEXT,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL,
  status enum_status_histori DEFAULT NULL,
  program_pilihan enum_yes_no NOT NULL,
  prioritas enum_yes_no NOT NULL,
  closed_date TIMESTAMP DEFAULT NULL,
  closed_by INTEGER DEFAULT NULL
);

CREATE INDEX idx_histori_campaign_id ON adm_campaign_histori(campaign_id);


-- ========================================================================
-- TABLE: adm_campaign_info
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_info (
  id SERIAL PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(255) NOT NULL,
  tgl_berita DATE NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_info_campaign_id ON adm_campaign_info(campaign_id);


-- ========================================================================
-- TABLE: adm_campaign_notifikasi
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_notifikasi (
  id SERIAL PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  donasi_id INTEGER NOT NULL REFERENCES adm_campaign_donasi(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  nama_lengkap VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  handphone VARCHAR(100) NOT NULL,
  alamat VARCHAR(200) DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_campaign_permohonan
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_permohonan (
  id SERIAL PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  kode_permohonan VARCHAR(20) DEFAULT NULL,
  tipe_permohonan VARCHAR(50) DEFAULT NULL,
  tgl_permohonan DATE DEFAULT NULL,
  permohonan_pencairan BIGINT DEFAULT NULL,
  permohonan_biayaoperasional BIGINT DEFAULT NULL,
  catatan TEXT,
  status enum_status_pembayaran DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_campaign_pembayaran
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_pembayaran (
  id SERIAL PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  permohonan_id INTEGER NOT NULL,
  tgl_pembayaran DATE NOT NULL,
  nominal_distribusi BIGINT DEFAULT NULL,
  no_rekening VARCHAR(50) DEFAULT NULL,
  nama_bank VARCHAR(50) NOT NULL,
  atas_nama VARCHAR(50) NOT NULL,
  permbayaran_biayaoperasional BIGINT DEFAULT NULL,
  bukti_transfer VARCHAR(50) DEFAULT NULL,
  catatan TEXT,
  status enum_status_pembayaran DEFAULT NULL,
  tindak_lanjut enum_yes_no NOT NULL,
  alasan_kembali TEXT,
  tgl_dikembalikan TIMESTAMP DEFAULT NULL,
  userid_pengembali VARCHAR(50) DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_campaign_pembayaran_bukti
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_campaign_pembayaran_bukti (
  id BIGSERIAL PRIMARY KEY,
  permohonan_id BIGINT DEFAULT NULL,
  pembayaran_id BIGINT DEFAULT NULL,
  file_name VARCHAR(255) DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_manual
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_manual (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  manual_file VARCHAR(255) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_mustahik
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_mustahik (
  id SERIAL PRIMARY KEY,
  tipe enum_perorangan_kelompok NOT NULL,
  nama VARCHAR(100) NOT NULL,
  foto VARCHAR(100) DEFAULT NULL,
  nik VARCHAR(25) DEFAULT NULL,
  nim VARCHAR(50) DEFAULT NULL,
  npwp VARCHAR(25) DEFAULT NULL,
  npwz VARCHAR(25) DEFAULT NULL,
  handphone VARCHAR(25) DEFAULT NULL,
  no_rekening VARCHAR(25) DEFAULT NULL,
  nama_bank VARCHAR(100) DEFAULT NULL,
  email VARCHAR(100) DEFAULT NULL,
  alamat TEXT,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_muzaki
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_muzaki (
  id SERIAL PRIMARY KEY,
  tipe enum_perorangan_lembaga NOT NULL,
  kelompok enum_kelompok_institusi DEFAULT NULL,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  nama VARCHAR(200) DEFAULT NULL,
  foto VARCHAR(100) DEFAULT NULL,
  nik VARCHAR(25) DEFAULT NULL,
  npwp VARCHAR(25) DEFAULT NULL,
  npwz VARCHAR(25) DEFAULT NULL,
  npwz_bg VARCHAR(255) NOT NULL,
  tgl_daftar VARCHAR(16) NOT NULL,
  handphone VARCHAR(25) DEFAULT NULL,
  email VARCHAR(100) DEFAULT NULL,
  alamat TEXT,
  email_cp VARCHAR(100) DEFAULT NULL,
  latitude VARCHAR(30) DEFAULT NULL,
  longitude VARCHAR(30) DEFAULT NULL,
  phone_cp VARCHAR(100) DEFAULT NULL,
  name_cp VARCHAR(100) DEFAULT NULL,
  tgl_lahir DATE DEFAULT NULL,
  jenis_kelamin enum_gender DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_muzaki_npwz
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_muzaki_npwz (
  id SERIAL PRIMARY KEY,
  muzaki_id INTEGER DEFAULT NULL,
  tipe enum_perorangan_lembaga NOT NULL,
  kelompok enum_kelompok_institusi DEFAULT NULL,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  npwz VARCHAR(25) DEFAULT NULL,
  nama_npwz VARCHAR(100) DEFAULT NULL,
  npwz_bg VARCHAR(255) NOT NULL,
  apikey VARCHAR(255) DEFAULT NULL,
  tgl_daftar DATE DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL,
  is_primary enum_yes_no NOT NULL DEFAULT 'N'
);


-- ========================================================================
-- TABLE: adm_pegawai
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_pegawai (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  nia VARCHAR(50) DEFAULT NULL,
  nama VARCHAR(100) NOT NULL,
  foto VARCHAR(100) DEFAULT NULL,
  nik VARCHAR(25) DEFAULT NULL,
  npwp VARCHAR(25) DEFAULT NULL,
  handphone VARCHAR(25) DEFAULT NULL,
  email VARCHAR(100) DEFAULT NULL,
  alamat TEXT,
  is_cp enum_yes_no DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: adm_program
-- ========================================================================

CREATE TABLE IF NOT EXISTS adm_program (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) DEFAULT NULL
);


-- ========================================================================
-- TABLE: groups
-- ========================================================================

CREATE TABLE IF NOT EXISTS groups (
  id SERIAL PRIMARY KEY,
  name VARCHAR(20) NOT NULL,
  description VARCHAR(100) NOT NULL,
  created_by INTEGER DEFAULT NULL,
  created_on INTEGER DEFAULT NULL,
  is_active SMALLINT DEFAULT 1,
  is_visible SMALLINT NOT NULL DEFAULT 1,
  has_admin_access SMALLINT NOT NULL DEFAULT 1
);


-- ========================================================================
-- TABLE: users
-- ========================================================================

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  ip_address VARCHAR(45) NOT NULL,
  username VARCHAR(100) DEFAULT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(254) NOT NULL,
  salt VARCHAR(6) DEFAULT NULL,
  activation_selector VARCHAR(255) DEFAULT NULL,
  activation_code VARCHAR(255) DEFAULT NULL,
  forgotten_password_selector VARCHAR(255) DEFAULT NULL,
  forgotten_password_code VARCHAR(255) DEFAULT NULL,
  forgotten_password_time INTEGER DEFAULT NULL,
  remember_selector VARCHAR(255) DEFAULT NULL,
  remember_code VARCHAR(255) DEFAULT NULL,
  created_on INTEGER NOT NULL,
  last_login INTEGER DEFAULT NULL,
  active SMALLINT DEFAULT NULL,
  full_name VARCHAR(50) DEFAULT NULL,
  nia VARCHAR(50) DEFAULT NULL,
  tipe VARCHAR(15) DEFAULT NULL,
  gopay_id VARCHAR(50) DEFAULT NULL,
  handphone VARCHAR(15) NOT NULL DEFAULT '',
  muzaki_id INTEGER DEFAULT NULL,
  dana_access_token VARCHAR(500) DEFAULT NULL,
  dana_refresh_token VARCHAR(500) DEFAULT NULL,
  dana_token_expires_at TIMESTAMP DEFAULT NULL,
  dana_external_id VARCHAR(100) DEFAULT NULL,
  dana_user_id VARCHAR(100) DEFAULT NULL,
  dana_linked_at TIMESTAMP DEFAULT NULL,
  CONSTRAINT uc_activation_selector UNIQUE (activation_selector),
  CONSTRAINT uc_forgotten_password_selector UNIQUE (forgotten_password_selector),
  CONSTRAINT uc_remember_selector UNIQUE (remember_selector)
);

CREATE INDEX idx_users_dana_external_id ON users(dana_external_id);
CREATE INDEX idx_users_dana_user_id ON users(dana_user_id);


-- ========================================================================
-- TABLE: users_groups
-- ========================================================================

CREATE TABLE IF NOT EXISTS users_groups (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
  assign SMALLINT DEFAULT 0,
  CONSTRAINT uc_users_groups UNIQUE (user_id, group_id)
);

CREATE INDEX idx_users_groups_user_id ON users_groups(user_id);
CREATE INDEX idx_users_groups_group_id ON users_groups(group_id);


-- ========================================================================
-- TABLE: users_google
-- ========================================================================

CREATE TABLE IF NOT EXISTS users_google (
  email VARCHAR(150) DEFAULT NULL,
  family_name VARCHAR(150) DEFAULT NULL,
  gender VARCHAR(32) DEFAULT NULL,
  given_name VARCHAR(150) DEFAULT NULL,
  hd VARCHAR(255) DEFAULT NULL,
  id BIGINT DEFAULT NULL,
  link VARCHAR(255) DEFAULT NULL,
  locale VARCHAR(5) DEFAULT NULL,
  name VARCHAR(150) DEFAULT NULL,
  picture TEXT,
  verified_email SMALLINT DEFAULT 0,
  signin_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_users_google_email ON users_google(email);
CREATE INDEX idx_users_google_id ON users_google(id);


-- ========================================================================
-- TABLE: users_otp
-- ========================================================================

CREATE TABLE IF NOT EXISTS users_otp (
  id SERIAL PRIMARY KEY,
  ip_address VARCHAR(45) NOT NULL,
  email VARCHAR(254) NOT NULL,
  tipe VARCHAR(254) NOT NULL,
  code_otp VARCHAR(255) DEFAULT NULL,
  created_on TIMESTAMP DEFAULT NULL,
  active SMALLINT DEFAULT NULL
);


-- ========================================================================
-- TABLE: users_otp_expsec
-- ========================================================================

CREATE TABLE IF NOT EXISTS users_otp_expsec (
  id SERIAL PRIMARY KEY,
  second INTEGER DEFAULT NULL,
  appl_type VARCHAR(10) DEFAULT NULL,
  active INTEGER DEFAULT NULL,
  created_by VARCHAR(155) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: users_profiles
-- ========================================================================

CREATE TABLE IF NOT EXISTS users_profiles (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP DEFAULT NULL,
  updated TIMESTAMP DEFAULT NULL,
  created_by INTEGER DEFAULT NULL,
  ordering_count INTEGER DEFAULT NULL,
  user_id INTEGER NOT NULL,
  display_name VARCHAR(50) NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  company VARCHAR(100) DEFAULT NULL,
  lang VARCHAR(2) NOT NULL DEFAULT 'en',
  bio TEXT,
  dob INTEGER DEFAULT NULL,
  gender enum_gender_mf DEFAULT NULL,
  phone VARCHAR(20) DEFAULT NULL,
  mobile VARCHAR(20) DEFAULT NULL,
  address_line1 VARCHAR(255) DEFAULT NULL,
  address_line2 VARCHAR(255) DEFAULT NULL,
  address_line3 VARCHAR(255) DEFAULT NULL,
  postcode VARCHAR(20) DEFAULT NULL,
  website VARCHAR(255) DEFAULT NULL,
  updated_on INTEGER DEFAULT NULL
);

CREATE INDEX idx_profiles_user_id ON users_profiles(user_id);


-- ========================================================================
-- TABLE: roles
-- ========================================================================

CREATE TABLE IF NOT EXISTS roles (
  id SERIAL PRIMARY KEY,
  role_name VARCHAR(100) DEFAULT NULL,
  is_active SMALLINT NOT NULL DEFAULT 1,
  created_by INTEGER DEFAULT NULL,
  created_on INTEGER DEFAULT NULL,
  is_visible SMALLINT NOT NULL DEFAULT 1
);


-- ========================================================================
-- TABLE: roles_menu
-- ========================================================================

CREATE TABLE IF NOT EXISTS roles_menu (
  id SERIAL PRIMARY KEY,
  role_id INTEGER DEFAULT NULL,
  menu_id INTEGER DEFAULT NULL,
  all_access SMALLINT NOT NULL DEFAULT 0,
  "insert" SMALLINT NOT NULL DEFAULT 0,
  read SMALLINT NOT NULL DEFAULT 0,
  edit SMALLINT NOT NULL DEFAULT 0,
  delete SMALLINT NOT NULL DEFAULT 0
);


-- ========================================================================
-- TABLE: groups_roles
-- ========================================================================

CREATE TABLE IF NOT EXISTS groups_roles (
  id SERIAL PRIMARY KEY,
  group_id INTEGER DEFAULT NULL,
  role_id INTEGER DEFAULT NULL,
  assign SMALLINT NOT NULL DEFAULT 0
);


-- ========================================================================
-- TABLE: login_attempts
-- ========================================================================

CREATE TABLE IF NOT EXISTS login_attempts (
  id SERIAL PRIMARY KEY,
  ip_address VARCHAR(45) NOT NULL,
  login VARCHAR(100) NOT NULL,
  time INTEGER DEFAULT NULL
);


-- ========================================================================
-- TABLE: log_api
-- ========================================================================

CREATE TABLE IF NOT EXISTS log_api (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) DEFAULT NULL,
  aplikasi VARCHAR(100) DEFAULT NULL,
  url_api VARCHAR(200) DEFAULT NULL,
  parameter TEXT,
  response TEXT,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_log_api_aplikasi ON log_api(aplikasi);
CREATE INDEX idx_log_api_created_date ON log_api(created_date);


-- ========================================================================
-- TABLE: log_api_midtrans
-- ========================================================================

CREATE TABLE IF NOT EXISTS log_api_midtrans (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) DEFAULT NULL,
  aplikasi VARCHAR(100) DEFAULT NULL,
  url_api VARCHAR(200) DEFAULT NULL,
  parameter TEXT,
  response TEXT,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_provinsi
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_provinsi (
  id CHAR(2) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  update_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_kabupaten
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_kabupaten (
  id CHAR(4) PRIMARY KEY,
  province_id CHAR(2) NOT NULL REFERENCES ref_provinsi(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  name VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_kabupaten_province_id ON ref_kabupaten(province_id);


-- ========================================================================
-- TABLE: ref_kecamatan
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_kecamatan (
  id CHAR(7) PRIMARY KEY,
  regency_id CHAR(4) NOT NULL REFERENCES ref_kabupaten(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  name VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_kecamatan_regency_id ON ref_kecamatan(regency_id);


-- ========================================================================
-- TABLE: ref_kelurahan
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_kelurahan (
  id CHAR(10) PRIMARY KEY,
  district_id CHAR(7) NOT NULL REFERENCES ref_kecamatan(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  name VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_kelurahan_district_id ON ref_kelurahan(district_id);


-- ========================================================================
-- TABLE: ref_kantor
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_kantor (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  tipe enum_kelompok_institusi NOT NULL,
  province_id CHAR(2) DEFAULT NULL,
  regency_id CHAR(4) DEFAULT NULL,
  name VARCHAR(100) DEFAULT NULL,
  alamat TEXT,
  telepon VARCHAR(20) DEFAULT NULL,
  email VARCHAR(100) DEFAULT NULL,
  cp VARCHAR(50) DEFAULT NULL,
  apikey VARCHAR(255) DEFAULT NULL,
  latitude VARCHAR(50) DEFAULT NULL,
  longitude VARCHAR(50) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_kantor_logo
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_kantor_logo (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  logo VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_metode_pembayaran
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_metode_pembayaran (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  kelompok enum_kelompok_metode NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  bank VARCHAR(20) NOT NULL,
  payment_type VARCHAR(50) NOT NULL,
  va_number INTEGER NOT NULL,
  start_amount BIGINT NOT NULL,
  end_amount BIGINT NOT NULL,
  order_list INTEGER NOT NULL,
  biaya_admin DECIMAL(12,3) DEFAULT NULL,
  tahapan TEXT,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_bank
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_bank (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  url_file VARCHAR(100) DEFAULT NULL,
  total_view INTEGER DEFAULT NULL,
  total_download INTEGER DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_batas_waktu
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_batas_waktu (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  nilai INTEGER NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_campaign_kategori
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_campaign_kategori (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_coa
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_coa (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) NOT NULL,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  title VARCHAR(100) DEFAULT NULL,
  description TEXT,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_coa_via
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_coa_via (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) NOT NULL,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  simbakey VARCHAR(255) DEFAULT NULL,
  title VARCHAR(100) DEFAULT NULL,
  description TEXT,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_dana_sosial
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_dana_sosial (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(50) DEFAULT NULL,
  code CHAR(15) DEFAULT NULL,
  name VARCHAR(100) DEFAULT NULL,
  year_activity INTEGER DEFAULT NULL,
  is_active enum_yes_no DEFAULT 'Y',
  is_delete enum_yes_no DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_news_kategori
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_news_kategori (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) DEFAULT NULL
);


-- ========================================================================
-- TABLE: ref_nominal_donasi
-- ========================================================================

CREATE TABLE IF NOT EXISTS ref_nominal_donasi (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  nilai INTEGER NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: geo_provinces
-- ========================================================================

CREATE TABLE IF NOT EXISTS geo_provinces (
  id BIGINT PRIMARY KEY,
  name VARCHAR(100) DEFAULT NULL,
  alt_name VARCHAR(100) DEFAULT NULL,
  latitude VARCHAR(50) DEFAULT NULL,
  longitude VARCHAR(50) DEFAULT NULL
);

CREATE INDEX idx_geo_provinces_id ON geo_provinces(id);


-- ========================================================================
-- TABLE: geo_regencies
-- ========================================================================

CREATE TABLE IF NOT EXISTS geo_regencies (
  id BIGINT PRIMARY KEY,
  province_id BIGINT DEFAULT NULL,
  name VARCHAR(100) DEFAULT NULL,
  alt_name VARCHAR(100) DEFAULT NULL,
  latitude VARCHAR(50) DEFAULT NULL,
  longitude VARCHAR(50) DEFAULT NULL
);

CREATE INDEX idx_geo_regencies_id ON geo_regencies(id);
CREATE INDEX idx_geo_regencies_province_id ON geo_regencies(province_id);


-- ========================================================================
-- TABLE: pub_banner
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_banner (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar VARCHAR(255) NOT NULL,
  link BYTEA NOT NULL,
  start_date DATE DEFAULT NULL,
  end_date DATE DEFAULT NULL,
  width VARCHAR(50) DEFAULT NULL,
  height VARCHAR(50) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_banner_log
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_banner_log (
  id SERIAL PRIMARY KEY,
  ip_address VARCHAR(100) NOT NULL,
  tanggal DATE NOT NULL,
  browser VARCHAR(200) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_banner_settings
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_banner_settings (
  view enum_banner_view DEFAULT NULL,
  width VARCHAR(16) DEFAULT NULL,
  height VARCHAR(16) DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_berita
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_berita (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(255) NOT NULL,
  tgl_berita DATE NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL,
  kategori INTEGER NOT NULL DEFAULT 1
);


-- ========================================================================
-- TABLE: pub_download_app
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_download_app (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar_playstore VARCHAR(100) NOT NULL,
  url_playstore VARCHAR(255) NOT NULL,
  url_gambar_appstore VARCHAR(100) NOT NULL,
  url_appstore VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_faq
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_faq (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_hubungi
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_hubungi (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar VARCHAR(255) NOT NULL,
  alamat TEXT NOT NULL,
  telepon VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL,
  latitude VARCHAR(50) NOT NULL,
  longitude VARCHAR(50) NOT NULL,
  url_map VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_kirimpesan
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_kirimpesan (
  id SERIAL PRIMARY KEY,
  nama_lengkap VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  handphone VARCHAR(100) DEFAULT NULL,
  pesan TEXT NOT NULL,
  ipaddress VARCHAR(200) NOT NULL,
  browser_aplikasi VARCHAR(200) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_legal
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_legal (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  url_link VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_legal_img
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_legal_img (
  id SERIAL PRIMARY KEY,
  legal_id INTEGER NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  url_link VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_penghargaan
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_penghargaan (
  id SERIAL PRIMARY KEY,
  url_gambar VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  url_link VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_slider
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_slider (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  url_link VARCHAR(255) NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL,
  is_deleted VARCHAR(1) DEFAULT '0'
);


-- ========================================================================
-- TABLE: pub_syarat_ketentuan
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_syarat_ketentuan (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(255) NOT NULL,
  tgl_berita DATE NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: pub_tentang
-- ========================================================================

CREATE TABLE IF NOT EXISTS pub_tentang (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  url_gambar VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: om_annual_work_plan_budget
-- ========================================================================

CREATE TABLE IF NOT EXISTS om_annual_work_plan_budget (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(20) DEFAULT NULL,
  annual_work_plan_budget VARCHAR(200) DEFAULT NULL,
  tipe_laporan enum_tipe_laporan DEFAULT NULL,
  bulan VARCHAR(16) DEFAULT NULL,
  tahun INTEGER DEFAULT NULL,
  nama_file VARCHAR(200) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: om_budget_realization
-- ========================================================================

CREATE TABLE IF NOT EXISTS om_budget_realization (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(20) DEFAULT NULL,
  budget_realization VARCHAR(200) DEFAULT NULL,
  tipe_laporan enum_tipe_laporan DEFAULT NULL,
  bulan VARCHAR(16) DEFAULT NULL,
  tahun INTEGER DEFAULT NULL,
  nama_file VARCHAR(200) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: om_financial_reports
-- ========================================================================

CREATE TABLE IF NOT EXISTS om_financial_reports (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(20) DEFAULT NULL,
  financial_reports VARCHAR(200) DEFAULT NULL,
  tipe_laporan enum_tipe_laporan DEFAULT NULL,
  bulan VARCHAR(16) DEFAULT NULL,
  tahun INTEGER DEFAULT NULL,
  nama_file VARCHAR(200) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: om_program_activities
-- ========================================================================

CREATE TABLE IF NOT EXISTS om_program_activities (
  id SERIAL PRIMARY KEY,
  kode_institusi VARCHAR(20) DEFAULT NULL,
  program_activities VARCHAR(200) DEFAULT NULL,
  tipe_laporan enum_tipe_laporan DEFAULT NULL,
  bulan VARCHAR(16) DEFAULT NULL,
  tahun INTEGER DEFAULT NULL,
  nama_file VARCHAR(200) DEFAULT NULL,
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);


-- ========================================================================
-- TABLE: app_menu
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_menu (
  id SERIAL PRIMARY KEY,
  menu_name VARCHAR(255) DEFAULT NULL,
  menu_location enum_menu_location DEFAULT NULL,
  menu_type enum_menu_type DEFAULT NULL,
  module_name VARCHAR(100) DEFAULT NULL,
  folder VARCHAR(100) DEFAULT NULL,
  controller VARCHAR(100) DEFAULT NULL,
  method VARCHAR(100) DEFAULT NULL,
  params VARCHAR(100) DEFAULT NULL,
  page_id INTEGER DEFAULT NULL,
  site_uri VARCHAR(255) DEFAULT NULL,
  url_link VARCHAR(255) DEFAULT NULL,
  target enum_target DEFAULT NULL,
  icon VARCHAR(100) DEFAULT NULL,
  class VARCHAR(100) DEFAULT NULL,
  created_by INTEGER DEFAULT NULL,
  created_on INTEGER DEFAULT NULL
);


-- ========================================================================
-- TABLE: app_menu_nav
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_menu_nav (
  id SERIAL PRIMARY KEY,
  parent_id INTEGER DEFAULT NULL,
  nav_type enum_nav_type DEFAULT NULL,
  nav_title VARCHAR(255) DEFAULT NULL,
  nav_location enum_menu_location DEFAULT NULL,
  menu_id INTEGER DEFAULT NULL,
  nav_position enum_nav_position DEFAULT NULL,
  nav_order INTEGER DEFAULT NULL,
  created_by INTEGER DEFAULT NULL,
  created_on INTEGER DEFAULT NULL
);


-- ========================================================================
-- TABLE: app_modules
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_modules (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  slug VARCHAR(50) NOT NULL UNIQUE,
  version VARCHAR(20) NOT NULL,
  type VARCHAR(20) DEFAULT NULL,
  description TEXT,
  skip_xss SMALLINT NOT NULL,
  is_frontend SMALLINT NOT NULL,
  is_backend SMALLINT NOT NULL,
  menu VARCHAR(20) NOT NULL,
  enabled SMALLINT NOT NULL,
  installed SMALLINT NOT NULL,
  is_core SMALLINT NOT NULL,
  updated_on INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_modules_enabled ON app_modules(enabled);


-- ========================================================================
-- TABLE: app_navigation_groups
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_navigation_groups (
  id SERIAL PRIMARY KEY,
  title VARCHAR(50) NOT NULL,
  abbrev VARCHAR(50) NOT NULL
);

CREATE INDEX idx_nav_groups_abbrev ON app_navigation_groups(abbrev);


-- ========================================================================
-- TABLE: app_navigation_links
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_navigation_links (
  id SERIAL PRIMARY KEY,
  title VARCHAR(100) NOT NULL DEFAULT '',
  parent INTEGER DEFAULT NULL,
  link_type VARCHAR(20) NOT NULL DEFAULT 'uri',
  page_id INTEGER DEFAULT NULL,
  module_name VARCHAR(50) NOT NULL DEFAULT '',
  url VARCHAR(255) NOT NULL DEFAULT '',
  uri VARCHAR(255) NOT NULL DEFAULT '',
  navigation_group_id INTEGER NOT NULL DEFAULT 0,
  position INTEGER NOT NULL DEFAULT 0,
  target VARCHAR(10) DEFAULT NULL,
  restricted_to VARCHAR(255) DEFAULT NULL,
  class VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE INDEX idx_nav_links_group_id ON app_navigation_links(navigation_group_id);


-- ========================================================================
-- TABLE: app_pages
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_pages (
  id SERIAL PRIMARY KEY,
  slug VARCHAR(255) NOT NULL DEFAULT '',
  class VARCHAR(255) NOT NULL DEFAULT '',
  title VARCHAR(255) NOT NULL DEFAULT '',
  uri TEXT,
  parent_id INTEGER NOT NULL DEFAULT 0,
  type_id VARCHAR(255) NOT NULL,
  entry_id VARCHAR(255) DEFAULT NULL,
  css TEXT,
  js TEXT,
  meta_title VARCHAR(255) DEFAULT NULL,
  meta_keywords CHAR(32) DEFAULT NULL,
  meta_robots_no_index SMALLINT DEFAULT NULL,
  meta_robots_no_follow SMALLINT DEFAULT NULL,
  meta_description TEXT,
  rss_enabled INTEGER NOT NULL DEFAULT 0,
  comments_enabled INTEGER NOT NULL DEFAULT 0,
  status enum_page_status NOT NULL DEFAULT 'draft',
  created_on INTEGER NOT NULL DEFAULT 0,
  updated_on INTEGER NOT NULL DEFAULT 0,
  restricted_to VARCHAR(255) DEFAULT NULL,
  is_home INTEGER NOT NULL DEFAULT 0,
  strict_uri SMALLINT NOT NULL DEFAULT 1,
  "order" INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_pages_slug ON app_pages(slug);
CREATE INDEX idx_pages_parent_id ON app_pages(parent_id);


-- ========================================================================
-- TABLE: app_page_types
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_page_types (
  id SERIAL PRIMARY KEY,
  slug VARCHAR(255) NOT NULL DEFAULT '',
  title VARCHAR(60) NOT NULL,
  description TEXT,
  stream_id INTEGER NOT NULL,
  meta_title VARCHAR(255) DEFAULT NULL,
  meta_keywords CHAR(32) DEFAULT NULL,
  meta_description TEXT,
  body TEXT NOT NULL,
  css TEXT,
  js TEXT,
  theme_layout VARCHAR(100) NOT NULL DEFAULT 'default',
  updated_on INTEGER NOT NULL,
  save_as_files CHAR(1) NOT NULL DEFAULT 'n',
  content_label VARCHAR(60) DEFAULT NULL,
  title_label VARCHAR(100) DEFAULT NULL
);


-- ========================================================================
-- TABLE: app_permissions
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_permissions (
  id SERIAL PRIMARY KEY,
  group_id INTEGER NOT NULL,
  module VARCHAR(50) NOT NULL,
  roles TEXT
);

CREATE INDEX idx_permissions_group_id ON app_permissions(group_id);


-- ========================================================================
-- TABLE: app_settings
-- ========================================================================

CREATE TABLE IF NOT EXISTS app_settings (
  slug VARCHAR(30) PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  type VARCHAR(50) NOT NULL,
  "default" TEXT NOT NULL,
  value TEXT NOT NULL,
  options TEXT NOT NULL,
  is_required INTEGER NOT NULL,
  is_gui INTEGER NOT NULL,
  module VARCHAR(50) NOT NULL,
  "order" INTEGER NOT NULL DEFAULT 0
);


-- ========================================================================
-- DANA MERCHANT TABLES
-- ========================================================================

-- TABLE: ref_dana_merchant_config
CREATE TABLE IF NOT EXISTS ref_dana_merchant_config (
  id SERIAL PRIMARY KEY,
  merchant_id VARCHAR(50) NOT NULL UNIQUE,
  merchant_name VARCHAR(100) NOT NULL,
  client_id VARCHAR(100) NOT NULL,
  client_secret VARCHAR(255) DEFAULT NULL,
  private_key TEXT DEFAULT NULL,
  public_key TEXT DEFAULT NULL,
  environment enum_dana_environment NOT NULL DEFAULT 'sandbox',
  api_base_url VARCHAR(255) DEFAULT NULL,
  callback_url VARCHAR(255) DEFAULT NULL,
  redirect_url VARCHAR(255) DEFAULT NULL,
  min_amount BIGINT NOT NULL DEFAULT 10000,
  max_amount BIGINT NOT NULL DEFAULT 50000000,
  biaya_admin DECIMAL(12,3) DEFAULT 0.000,
  biaya_admin_type enum_biaya_admin_type DEFAULT 'percentage',
  is_active enum_yes_no NOT NULL DEFAULT 'Y',
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_by VARCHAR(50) DEFAULT NULL,
  updated_by VARCHAR(50) DEFAULT NULL,
  deleted_by VARCHAR(50) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT NULL,
  updated_date TIMESTAMP DEFAULT NULL,
  deleted_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_merchant_client_id ON ref_dana_merchant_config(client_id);
CREATE INDEX idx_merchant_environment ON ref_dana_merchant_config(environment);
CREATE INDEX idx_merchant_is_active ON ref_dana_merchant_config(is_active);


-- TABLE: trx_dana_payment
CREATE TABLE IF NOT EXISTS trx_dana_payment (
  id SERIAL PRIMARY KEY,
  uuid VARCHAR(36) NOT NULL UNIQUE,
  checksum VARCHAR(64) DEFAULT NULL,
  merchant_config_id INTEGER NOT NULL REFERENCES ref_dana_merchant_config(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  order_id VARCHAR(100) NOT NULL UNIQUE,
  partner_reference_no VARCHAR(100) NOT NULL UNIQUE,
  dana_reference_no VARCHAR(100) DEFAULT NULL,
  amount DECIMAL(15,2) NOT NULL,
  biaya_admin DECIMAL(15,2) DEFAULT 0,
  total_amount DECIMAL(15,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'IDR',
  description VARCHAR(255) DEFAULT NULL,
  payer_name VARCHAR(100) DEFAULT NULL,
  payer_email VARCHAR(100) DEFAULT NULL,
  payer_phone VARCHAR(20) DEFAULT NULL,
  payer_dana_id VARCHAR(100) DEFAULT NULL,
  status enum_dana_payment_status NOT NULL DEFAULT 'pending',
  dana_status VARCHAR(50) DEFAULT NULL,
  dana_response_code VARCHAR(20) DEFAULT NULL,
  dana_response_message VARCHAR(255) DEFAULT NULL,
  dana_web_redirect_url VARCHAR(500) DEFAULT NULL,
  dana_ott_token VARCHAR(500) DEFAULT NULL,
  expired_at TIMESTAMP DEFAULT NULL,
  paid_at TIMESTAMP DEFAULT NULL,
  callback_at TIMESTAMP DEFAULT NULL,
  request_payload JSONB DEFAULT NULL,
  response_payload JSONB DEFAULT NULL,
  callback_payload JSONB DEFAULT NULL,
  donasi_id INTEGER DEFAULT NULL,
  user_id INTEGER DEFAULT NULL,
  ip_address VARCHAR(45) DEFAULT NULL,
  user_agent VARCHAR(255) DEFAULT NULL,
  is_delete enum_yes_no NOT NULL DEFAULT 'N',
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_trx_merchant_config_id ON trx_dana_payment(merchant_config_id);
CREATE INDEX idx_trx_dana_reference_no ON trx_dana_payment(dana_reference_no);
CREATE INDEX idx_trx_status ON trx_dana_payment(status);
CREATE INDEX idx_trx_dana_status ON trx_dana_payment(dana_status);
CREATE INDEX idx_trx_donasi_id ON trx_dana_payment(donasi_id);
CREATE INDEX idx_trx_user_id ON trx_dana_payment(user_id);
CREATE INDEX idx_trx_created_date ON trx_dana_payment(created_date);
CREATE INDEX idx_trx_paid_at ON trx_dana_payment(paid_at);


-- TABLE: log_dana_webhook
CREATE TABLE IF NOT EXISTS log_dana_webhook (
  id SERIAL PRIMARY KEY,
  merchant_config_id INTEGER DEFAULT NULL,
  webhook_type VARCHAR(50) NOT NULL,
  order_id VARCHAR(100) DEFAULT NULL,
  dana_reference_no VARCHAR(100) DEFAULT NULL,
  payload JSONB NOT NULL,
  signature VARCHAR(500) DEFAULT NULL,
  signature_valid enum_signature_valid DEFAULT 'UNCHECKED',
  processed enum_yes_no DEFAULT 'N',
  process_result VARCHAR(255) DEFAULT NULL,
  ip_address VARCHAR(45) DEFAULT NULL,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_date TIMESTAMP DEFAULT NULL
);

CREATE INDEX idx_webhook_merchant_config_id ON log_dana_webhook(merchant_config_id);
CREATE INDEX idx_webhook_type ON log_dana_webhook(webhook_type);
CREATE INDEX idx_webhook_order_id ON log_dana_webhook(order_id);
CREATE INDEX idx_webhook_dana_reference_no ON log_dana_webhook(dana_reference_no);
CREATE INDEX idx_webhook_processed ON log_dana_webhook(processed);
CREATE INDEX idx_webhook_created_date ON log_dana_webhook(created_date);


-- ========================================================================
-- VIEWS
-- ========================================================================

-- VIEW: v_dana_transactions
CREATE OR REPLACE VIEW v_dana_transactions AS
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


-- VIEW: v_dana_merchant_transactions
CREATE OR REPLACE VIEW v_dana_merchant_transactions AS
SELECT
    t.id,
    t.uuid,
    t.order_id,
    t.partner_reference_no,
    t.dana_reference_no,
    t.amount,
    t.biaya_admin,
    t.total_amount,
    t.currency,
    t.description,
    t.payer_name,
    t.payer_email,
    t.payer_phone,
    t.payer_dana_id,
    t.status,
    t.dana_status,
    t.dana_response_code,
    t.dana_response_message,
    t.dana_web_redirect_url,
    t.expired_at,
    t.paid_at,
    t.created_date,
    m.merchant_id,
    m.merchant_name,
    m.environment,
    d.campaign_id,
    d.nama_lengkap AS donasi_nama,
    d.email AS donasi_email,
    c.name AS campaign_name
FROM trx_dana_payment t
LEFT JOIN ref_dana_merchant_config m ON t.merchant_config_id = m.id
LEFT JOIN adm_campaign_donasi d ON t.donasi_id = d.id
LEFT JOIN adm_campaign c ON d.campaign_id = c.id
WHERE t.is_delete = 'N';


-- VIEW: v_dana_donasi_transactions
CREATE OR REPLACE VIEW v_dana_donasi_transactions AS
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
    mz.nama AS muzaki_nama,
    mz.handphone AS muzaki_phone
FROM adm_campaign_donasi d
LEFT JOIN adm_campaign c ON d.campaign_id = c.id
LEFT JOIN adm_muzaki mz ON d.muzaki_id = mz.id
WHERE d.is_delete = 'N'
  AND d.dana_reference_no IS NOT NULL;


-- ========================================================================
-- INSERT DEFAULT DATA
-- ========================================================================

-- Insert DANA payment method (if not exists)
INSERT INTO ref_metode_pembayaran
(name, kelompok, url_gambar, bank, payment_type, va_number,
 start_amount, end_amount, order_list, biaya_admin, tahapan,
 is_active, is_delete, created_date)
SELECT 'DANA', 'e money', 'dana.png', 'DANA', 'emoney', 0, 10000, 50000000, 1, 0.000,
'1. Pilih metode pembayaran DANA
2. Anda akan diarahkan ke halaman DANA
3. Login dengan akun DANA Anda
4. Konfirmasi pembayaran
5. Pembayaran berhasil',
'Y', 'N', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM ref_metode_pembayaran
    WHERE payment_type = 'emoney' AND bank = 'DANA'
);


-- ========================================================================
-- COMMENTS
-- ========================================================================

COMMENT ON TABLE ref_dana_merchant_config IS 'Konfigurasi merchant DANA untuk pembayaran langsung';
COMMENT ON TABLE trx_dana_payment IS 'Transaksi pembayaran DANA khusus merchant';
COMMENT ON TABLE log_dana_webhook IS 'Log webhook/callback dari DANA';

COMMENT ON COLUMN ref_dana_merchant_config.merchant_id IS 'ID merchant dari DANA';
COMMENT ON COLUMN ref_dana_merchant_config.client_secret IS 'Client Secret (encrypted)';
COMMENT ON COLUMN ref_dana_merchant_config.private_key IS 'Private key untuk signing (encrypted)';
COMMENT ON COLUMN trx_dana_payment.uuid IS 'UUID unik untuk setiap transaksi';
COMMENT ON COLUMN trx_dana_payment.request_payload IS 'Request payload ke DANA (untuk debugging)';
COMMENT ON COLUMN trx_dana_payment.response_payload IS 'Response payload dari DANA (untuk debugging)';
