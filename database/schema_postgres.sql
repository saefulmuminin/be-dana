-- ============================================================================
-- PostgreSQL Schema for Cinta Zakat Database
-- Converted from MySQL schema.sql
-- Compatible with Neon PostgreSQL / Vercel Postgres
-- ============================================================================

-- Drop existing types if they exist (for clean migration)
DROP TYPE IF EXISTS enum_tipe_zakat CASCADE;
DROP TYPE IF EXISTS enum_tipe_muzaki CASCADE;
DROP TYPE IF EXISTS enum_status_donasi CASCADE;
DROP TYPE IF EXISTS enum_yes_no CASCADE;
DROP TYPE IF EXISTS enum_status_campaign CASCADE;
DROP TYPE IF EXISTS enum_kelompok CASCADE;
DROP TYPE IF EXISTS enum_gender CASCADE;
DROP TYPE IF EXISTS enum_tipe_permohonan CASCADE;
DROP TYPE IF EXISTS enum_tipe_laporan CASCADE;
DROP TYPE IF EXISTS enum_kelompok_pembayaran CASCADE;
DROP TYPE IF EXISTS enum_nav_type CASCADE;
DROP TYPE IF EXISTS enum_nav_position CASCADE;
DROP TYPE IF EXISTS enum_menu_location CASCADE;
DROP TYPE IF EXISTS enum_menu_type CASCADE;
DROP TYPE IF EXISTS enum_target CASCADE;
DROP TYPE IF EXISTS enum_page_status CASCADE;

-- ============================================================================
-- CREATE ENUM TYPES
-- ============================================================================

CREATE TYPE enum_tipe_zakat AS ENUM ('zakat', 'infak');
CREATE TYPE enum_tipe_muzaki AS ENUM ('perorangan', 'lembaga');
CREATE TYPE enum_tipe_mustahik AS ENUM ('perorangan', 'kelompok');
CREATE TYPE enum_status_donasi AS ENUM ('belum', 'berhasil', 'menunggu', 'dibatalkan');
CREATE TYPE enum_yes_no AS ENUM ('Y', 'N');
CREATE TYPE enum_status_campaign AS ENUM ('draft', 'publish', 'closed');
CREATE TYPE enum_kelompok AS ENUM ('BAZNAS_prov', 'BAZNAS_kab', 'LAZ_prov', 'LAZ_kab', 'UPZ', 'LAZNAS', 'Pusat');
CREATE TYPE enum_gender AS ENUM ('pria', 'wanita', '');
CREATE TYPE enum_tipe_permohonan AS ENUM ('draft', 'belum', 'sudah', 'kembali');
CREATE TYPE enum_tipe_laporan AS ENUM ('bulanan', 'tahunan');
CREATE TYPE enum_kelompok_pembayaran AS ENUM ('pembayaran instan', 'virtual account', 'transfer bank', 'internet banking', 'counter store', 'e money', 'credit card');
CREATE TYPE enum_nav_type AS ENUM ('label', 'link');
CREATE TYPE enum_nav_position AS ENUM ('Main', 'Top', 'Bottom');
CREATE TYPE enum_menu_location AS ENUM ('Backend', 'Frontend');
CREATE TYPE enum_menu_type AS ENUM ('module', 'page', 'uri', 'url');
CREATE TYPE enum_target AS ENUM ('_blank', '_self');
CREATE TYPE enum_page_status AS ENUM ('draft', 'live');
CREATE TYPE enum_histori_status AS ENUM ('draft', 'simpan', 'edit', 'perpanjangan');

-- ============================================================================
-- TABLE: adm_campaign
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign (
    id SERIAL PRIMARY KEY,
    kode_institusi INTEGER,
    tipe enum_tipe_zakat NOT NULL,
    program_id INTEGER NOT NULL,
    kategori VARCHAR(150) NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    target_donasi BIGINT,
    start_date DATE,
    end_date DATE,
    bataswaktu_id INTEGER,
    link_campaign VARCHAR(100),
    prosen_biayaoperasional DECIMAL(10,2),
    biayaoperasional BIGINT DEFAULT 0,
    donasi BIGINT,
    url_fotoutama VARCHAR(100),
    no_rekening VARCHAR(30),
    nama_bank VARCHAR(100),
    atas_nama VARCHAR(100),
    coa_infak VARCHAR(20),
    coaid_infak INTEGER,
    coa_zakat VARCHAR(20),
    coaid_zakat INTEGER,
    informasi TEXT,
    mustahik_nama VARCHAR(150),
    tipe_mustahik enum_tipe_mustahik,
    nik_mustahik VARCHAR(25),
    hp_mustahik VARCHAR(25),
    email_mustahik VARCHAR(100),
    alamat_mustahik TEXT,
    campaign_latitude VARCHAR(50) NOT NULL DEFAULT '',
    campaign_longitude VARCHAR(50) NOT NULL DEFAULT '',
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP,
    status enum_status_campaign,
    program_pilihan enum_yes_no NOT NULL DEFAULT 'N',
    prioritas enum_yes_no NOT NULL DEFAULT 'N',
    closed_date TIMESTAMP,
    closed_by VARCHAR(50)
);

-- ============================================================================
-- TABLE: adm_campaign_donasi
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_donasi (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36),
    checksum VARCHAR(64),
    campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id),
    muzaki_id INTEGER,
    tipe_zakat enum_tipe_zakat NOT NULL,
    tipe enum_tipe_muzaki NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    npwz VARCHAR(100),
    doa_muzaki VARCHAR(200),
    nominal BIGINT,
    tgl_donasi DATE,
    metode_id INTEGER,
    prosen_biayaoperasional DECIMAL(10,2),
    biayaoperasional BIGINT,
    donasi BIGINT,
    donasi_net DECIMAL(15,2) DEFAULT 0,
    total_bayar DECIMAL(15,2) DEFAULT 0,
    biaya_admin BIGINT,
    status enum_status_donasi,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    hamba_allah enum_yes_no DEFAULT 'N',
    no_transaksi VARCHAR(50),
    tanggal VARCHAR(20),
    waktu VARCHAR(20),
    bsz VARCHAR(200),
    no_refrensi VARCHAR(200),
    nama_refrensi VARCHAR(200),
    kode_biller VARCHAR(200),
    url_qris VARCHAR(200),
    url_deeplink VARCHAR(255),
    tgl_expired TIMESTAMP,
    transaksi_id VARCHAR(50),
    order_id VARCHAR(50),
    partner_reference_no VARCHAR(100),
    dana_reference_no VARCHAR(100),
    dana_status VARCHAR(50),
    dana_web_redirect_url VARCHAR(500),
    dana_ott_token VARCHAR(500),
    dana_paid_at TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_donasi_uuid ON adm_campaign_donasi(uuid);
CREATE INDEX IF NOT EXISTS idx_donasi_muzaki_id ON adm_campaign_donasi(muzaki_id);
CREATE INDEX IF NOT EXISTS idx_donasi_partner_ref ON adm_campaign_donasi(partner_reference_no);
CREATE INDEX IF NOT EXISTS idx_donasi_dana_ref ON adm_campaign_donasi(dana_reference_no);
CREATE INDEX IF NOT EXISTS idx_donasi_dana_status ON adm_campaign_donasi(dana_status);
CREATE INDEX IF NOT EXISTS idx_donasi_order_id ON adm_campaign_donasi(order_id);
CREATE INDEX IF NOT EXISTS idx_donasi_campaign_id ON adm_campaign_donasi(campaign_id);

-- ============================================================================
-- TABLE: adm_campaign_histori
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_histori (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id),
    kode_institusi VARCHAR(50),
    tipe enum_tipe_zakat NOT NULL,
    program_id INTEGER NOT NULL,
    kategori VARCHAR(150) NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(255),
    target_donasi BIGINT,
    start_date DATE,
    end_date DATE,
    bataswaktu_id INTEGER,
    link_campaign VARCHAR(100),
    prosen_biayaoperasional DECIMAL(10,2),
    biayaoperasional BIGINT,
    donasi BIGINT,
    donasi_infak BIGINT,
    donasi_zakat BIGINT,
    url_fotoutama VARCHAR(100),
    no_rekening VARCHAR(30),
    nama_bank VARCHAR(100),
    atas_nama VARCHAR(100),
    coa_infak VARCHAR(20),
    coaid_infak INTEGER,
    coa_zakat VARCHAR(20),
    coaid_zakat INTEGER,
    informasi TEXT,
    mustahik_nama VARCHAR(150),
    tipe_mustahik enum_tipe_mustahik,
    nik_mustahik VARCHAR(25),
    hp_mustahik VARCHAR(25),
    email_mustahik VARCHAR(100),
    alamat_mustahik TEXT,
    campaign_latitude VARCHAR(50) NOT NULL DEFAULT '',
    campaign_longitude VARCHAR(50) NOT NULL DEFAULT '',
    status_histori VARCHAR(100),
    log_histori TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP,
    status enum_histori_status,
    program_pilihan enum_yes_no NOT NULL DEFAULT 'N',
    prioritas enum_yes_no NOT NULL DEFAULT 'N',
    closed_date TIMESTAMP,
    closed_by INTEGER
);

-- ============================================================================
-- TABLE: adm_campaign_info
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_info (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    tgl_berita DATE NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_campaign_notifikasi
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_notifikasi (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id),
    donasi_id INTEGER NOT NULL REFERENCES adm_campaign_donasi(id),
    nama_lengkap VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    handphone VARCHAR(100) NOT NULL,
    alamat VARCHAR(200),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_campaign_permohonan
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_permohonan (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id),
    kode_permohonan VARCHAR(20),
    tipe_permohonan VARCHAR(50),
    tgl_permohonan DATE,
    permohonan_pencairan BIGINT,
    permohonan_biayaoperasional BIGINT,
    catatan TEXT,
    status enum_tipe_permohonan,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_campaign_pembayaran
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_pembayaran (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES adm_campaign(id),
    permohonan_id INTEGER NOT NULL,
    tgl_pembayaran DATE NOT NULL,
    nominal_distribusi BIGINT,
    no_rekening VARCHAR(50),
    nama_bank VARCHAR(50) NOT NULL,
    atas_nama VARCHAR(50) NOT NULL,
    permbayaran_biayaoperasional BIGINT,
    bukti_transfer VARCHAR(50),
    catatan TEXT,
    status enum_tipe_permohonan,
    tindak_lanjut enum_yes_no NOT NULL DEFAULT 'N',
    alasan_kembali TEXT,
    tgl_dikembalikan TIMESTAMP,
    userid_pengembali VARCHAR(50),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_campaign_pembayaran_bukti
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_campaign_pembayaran_bukti (
    id BIGSERIAL PRIMARY KEY,
    permohonan_id BIGINT,
    pembayaran_id BIGINT,
    file_name VARCHAR(255)
);

-- ============================================================================
-- TABLE: adm_manual
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_manual (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    manual_file VARCHAR(255),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_mustahik
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_mustahik (
    id SERIAL PRIMARY KEY,
    tipe enum_tipe_mustahik NOT NULL,
    nama VARCHAR(100) NOT NULL,
    foto VARCHAR(100),
    nik VARCHAR(25),
    nim VARCHAR(50),
    npwp VARCHAR(25),
    npwz VARCHAR(25),
    handphone VARCHAR(25),
    no_rekening VARCHAR(25),
    nama_bank VARCHAR(100),
    email VARCHAR(100),
    alamat TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_muzaki
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_muzaki (
    id SERIAL PRIMARY KEY,
    tipe enum_tipe_muzaki NOT NULL,
    kelompok enum_kelompok,
    kode_institusi VARCHAR(50),
    nama VARCHAR(200),
    foto VARCHAR(100),
    nik VARCHAR(25),
    npwp VARCHAR(25),
    npwz VARCHAR(25),
    npwz_bg VARCHAR(255) NOT NULL DEFAULT '',
    tgl_daftar VARCHAR(16) NOT NULL DEFAULT '',
    handphone VARCHAR(25),
    email VARCHAR(100),
    alamat TEXT,
    email_cp VARCHAR(100),
    latitude VARCHAR(30),
    longitude VARCHAR(30),
    phone_cp VARCHAR(100),
    name_cp VARCHAR(100),
    tgl_lahir DATE,
    jenis_kelamin enum_gender,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_muzaki_email ON adm_muzaki(email);
CREATE INDEX IF NOT EXISTS idx_muzaki_npwz ON adm_muzaki(npwz);

-- ============================================================================
-- TABLE: adm_muzaki_npwz
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_muzaki_npwz (
    id SERIAL PRIMARY KEY,
    muzaki_id INTEGER,
    tipe enum_tipe_muzaki NOT NULL,
    kelompok enum_kelompok,
    kode_institusi VARCHAR(50),
    npwz VARCHAR(25),
    nama_npwz VARCHAR(100),
    npwz_bg VARCHAR(255) NOT NULL DEFAULT '',
    apikey VARCHAR(255),
    tgl_daftar DATE,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP,
    is_primary enum_yes_no NOT NULL DEFAULT 'N'
);

-- ============================================================================
-- TABLE: adm_pegawai
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_pegawai (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(50),
    nia VARCHAR(50),
    nama VARCHAR(100) NOT NULL,
    foto VARCHAR(100),
    nik VARCHAR(25),
    npwp VARCHAR(25),
    handphone VARCHAR(25),
    email VARCHAR(100),
    alamat TEXT,
    is_cp enum_yes_no,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: adm_program
-- ============================================================================
CREATE TABLE IF NOT EXISTS adm_program (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- ============================================================================
-- TABLE: groups
-- ============================================================================
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    description VARCHAR(100) NOT NULL,
    created_by INTEGER,
    created_on INTEGER,
    is_active SMALLINT DEFAULT 1,
    is_visible SMALLINT NOT NULL DEFAULT 1,
    has_admin_access SMALLINT NOT NULL DEFAULT 1
);

-- ============================================================================
-- TABLE: users
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    username VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL,
    salt VARCHAR(6),
    activation_selector VARCHAR(255) UNIQUE,
    activation_code VARCHAR(255),
    forgotten_password_selector VARCHAR(255) UNIQUE,
    forgotten_password_code VARCHAR(255),
    forgotten_password_time INTEGER,
    remember_selector VARCHAR(255) UNIQUE,
    remember_code VARCHAR(255),
    created_on INTEGER NOT NULL,
    last_login INTEGER,
    active SMALLINT,
    full_name VARCHAR(50),
    nia VARCHAR(50),
    tipe VARCHAR(15),
    gopay_id VARCHAR(50),
    handphone VARCHAR(15) NOT NULL DEFAULT '',
    muzaki_id INTEGER,
    dana_access_token VARCHAR(500),
    dana_refresh_token VARCHAR(500),
    dana_token_expires_at TIMESTAMP,
    dana_external_id VARCHAR(100),
    dana_user_id VARCHAR(100),
    dana_linked_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_dana_external_id ON users(dana_external_id);
CREATE INDEX IF NOT EXISTS idx_users_dana_user_id ON users(dana_user_id);

-- ============================================================================
-- TABLE: users_groups
-- ============================================================================
CREATE TABLE IF NOT EXISTS users_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    assign SMALLINT DEFAULT 0,
    UNIQUE (user_id, group_id)
);

-- ============================================================================
-- TABLE: users_profiles
-- ============================================================================
CREATE TABLE IF NOT EXISTS users_profiles (
    id SERIAL PRIMARY KEY,
    created TIMESTAMP,
    updated TIMESTAMP,
    created_by INTEGER,
    ordering_count INTEGER,
    user_id INTEGER NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    company VARCHAR(100),
    lang VARCHAR(2) NOT NULL DEFAULT 'en',
    bio TEXT,
    dob INTEGER,
    gender VARCHAR(2),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    address_line3 VARCHAR(255),
    postcode VARCHAR(20),
    website VARCHAR(255),
    updated_on INTEGER
);

-- ============================================================================
-- TABLE: users_otp
-- ============================================================================
CREATE TABLE IF NOT EXISTS users_otp (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    email VARCHAR(254) NOT NULL,
    tipe VARCHAR(254) NOT NULL,
    code_otp VARCHAR(255),
    created_on TIMESTAMP,
    active SMALLINT
);

-- ============================================================================
-- TABLE: users_otp_expsec
-- ============================================================================
CREATE TABLE IF NOT EXISTS users_otp_expsec (
    id SERIAL PRIMARY KEY,
    second INTEGER,
    appl_type VARCHAR(10),
    active INTEGER,
    created_by VARCHAR(155),
    created_date TIMESTAMP
);

-- ============================================================================
-- TABLE: users_google
-- ============================================================================
CREATE TABLE IF NOT EXISTS users_google (
    email VARCHAR(150),
    family_name VARCHAR(150),
    gender VARCHAR(32),
    given_name VARCHAR(150),
    hd VARCHAR(255),
    id BIGINT,
    link VARCHAR(255),
    locale VARCHAR(5),
    name VARCHAR(150),
    picture TEXT,
    verified_email SMALLINT DEFAULT 0,
    signin_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_google_email ON users_google(email);
CREATE INDEX IF NOT EXISTS idx_google_id ON users_google(id);

-- ============================================================================
-- TABLE: login_attempts
-- ============================================================================
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    login VARCHAR(100) NOT NULL,
    time INTEGER
);

-- ============================================================================
-- TABLE: roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(100),
    is_active SMALLINT NOT NULL DEFAULT 1,
    created_by INTEGER,
    created_on INTEGER,
    is_visible SMALLINT NOT NULL DEFAULT 1
);

-- ============================================================================
-- TABLE: roles_menu
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles_menu (
    id SERIAL PRIMARY KEY,
    role_id INTEGER,
    menu_id INTEGER,
    all_access SMALLINT NOT NULL DEFAULT 0,
    insert_access SMALLINT NOT NULL DEFAULT 0,
    read_access SMALLINT NOT NULL DEFAULT 0,
    edit_access SMALLINT NOT NULL DEFAULT 0,
    delete_access SMALLINT NOT NULL DEFAULT 0
);

-- ============================================================================
-- TABLE: groups_roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS groups_roles (
    id SERIAL PRIMARY KEY,
    group_id INTEGER,
    role_id INTEGER,
    assign SMALLINT NOT NULL DEFAULT 0
);

-- ============================================================================
-- TABLE: log_api
-- ============================================================================
CREATE TABLE IF NOT EXISTS log_api (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    aplikasi VARCHAR(100),
    url_api VARCHAR(200),
    parameter TEXT,
    response TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_log_api_aplikasi ON log_api(aplikasi);
CREATE INDEX IF NOT EXISTS idx_log_api_created_date ON log_api(created_date);

-- ============================================================================
-- TABLE: log_api_midtrans
-- ============================================================================
CREATE TABLE IF NOT EXISTS log_api_midtrans (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    aplikasi VARCHAR(100),
    url_api VARCHAR(200),
    parameter TEXT,
    response TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_provinsi
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_provinsi (
    id CHAR(2) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    update_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_kabupaten
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_kabupaten (
    id CHAR(4) PRIMARY KEY,
    province_id CHAR(2) NOT NULL REFERENCES ref_provinsi(id),
    name VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kabupaten_province_id ON ref_kabupaten(province_id);

-- ============================================================================
-- TABLE: ref_kecamatan
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_kecamatan (
    id CHAR(7) PRIMARY KEY,
    regency_id CHAR(4) NOT NULL REFERENCES ref_kabupaten(id),
    name VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kecamatan_regency_id ON ref_kecamatan(regency_id);

-- ============================================================================
-- TABLE: ref_kelurahan
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_kelurahan (
    id CHAR(10) PRIMARY KEY,
    district_id CHAR(7) NOT NULL REFERENCES ref_kecamatan(id),
    name VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kelurahan_district_id ON ref_kelurahan(district_id);

-- ============================================================================
-- TABLE: ref_kantor
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_kantor (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(50),
    tipe enum_kelompok NOT NULL,
    province_id CHAR(2),
    regency_id CHAR(4),
    name VARCHAR(100),
    alamat TEXT,
    telepon VARCHAR(20),
    email VARCHAR(100),
    cp VARCHAR(50),
    apikey VARCHAR(255),
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_kantor_logo
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_kantor_logo (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(50),
    logo VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_bank
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_bank (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    url_file VARCHAR(100),
    total_view INTEGER,
    total_download INTEGER,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_batas_waktu
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_batas_waktu (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    nilai INTEGER NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_campaign_kategori
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_campaign_kategori (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255)
);

-- ============================================================================
-- TABLE: ref_coa
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_coa (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    kode_institusi VARCHAR(50),
    title VARCHAR(100),
    description TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_coa_via
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_coa_via (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    kode_institusi VARCHAR(50),
    simbakey VARCHAR(255),
    title VARCHAR(100),
    description TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_dana_sosial
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_dana_sosial (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(50),
    code CHAR(15),
    name VARCHAR(100),
    year_activity INTEGER,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_metode_pembayaran
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_metode_pembayaran (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    kelompok enum_kelompok_pembayaran NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    bank VARCHAR(20) NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    va_number INTEGER NOT NULL DEFAULT 0,
    start_amount BIGINT NOT NULL DEFAULT 0,
    end_amount BIGINT NOT NULL DEFAULT 0,
    order_list INTEGER NOT NULL DEFAULT 0,
    biaya_admin DECIMAL(12,3),
    tahapan TEXT,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_nominal_donasi
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_nominal_donasi (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    nilai INTEGER NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- TABLE: ref_news_kategori
-- ============================================================================
CREATE TABLE IF NOT EXISTS ref_news_kategori (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- ============================================================================
-- TABLE: geo_provinces
-- ============================================================================
CREATE TABLE IF NOT EXISTS geo_provinces (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    alt_name VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);

-- ============================================================================
-- TABLE: geo_regencies
-- ============================================================================
CREATE TABLE IF NOT EXISTS geo_regencies (
    id BIGINT PRIMARY KEY,
    province_id BIGINT,
    name VARCHAR(100),
    alt_name VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_geo_regencies_province ON geo_regencies(province_id);

-- ============================================================================
-- PUBLICATION TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS pub_banner (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_gambar VARCHAR(255) NOT NULL,
    link VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    width VARCHAR(50),
    height VARCHAR(50),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_banner_log (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(100) NOT NULL,
    tanggal DATE NOT NULL,
    browser VARCHAR(200) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_berita (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    tgl_berita DATE NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP,
    kategori INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS pub_slider (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    url_link VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP,
    is_deleted VARCHAR(1) DEFAULT '0'
);

CREATE TABLE IF NOT EXISTS pub_tentang (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_faq (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

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
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_kirimpesan (
    id SERIAL PRIMARY KEY,
    nama_lengkap VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    handphone VARCHAR(100),
    pesan TEXT NOT NULL,
    ipaddress VARCHAR(200) NOT NULL,
    browser_aplikasi VARCHAR(200) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_download_app (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_gambar_playstore VARCHAR(100) NOT NULL,
    url_playstore VARCHAR(255) NOT NULL,
    url_gambar_appstore VARCHAR(100) NOT NULL,
    url_appstore VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_legal (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url_gambar VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    url_link VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_legal_img (
    id SERIAL PRIMARY KEY,
    legal_id INTEGER NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    url_link VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_penghargaan (
    id SERIAL PRIMARY KEY,
    url_gambar VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    url_link VARCHAR(255) NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pub_syarat_ketentuan (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    tgl_berita DATE NOT NULL,
    url_gambar VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- APP MENU TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS app_menu (
    id SERIAL PRIMARY KEY,
    menu_name VARCHAR(255),
    menu_location enum_menu_location,
    menu_type enum_menu_type,
    module_name VARCHAR(100),
    folder VARCHAR(100),
    controller VARCHAR(100),
    method VARCHAR(100),
    params VARCHAR(100),
    page_id INTEGER,
    site_uri VARCHAR(255),
    url_link VARCHAR(255),
    target enum_target,
    icon VARCHAR(100),
    class VARCHAR(100),
    created_by INTEGER,
    created_on INTEGER
);

CREATE TABLE IF NOT EXISTS app_menu_nav (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER,
    nav_type enum_nav_type,
    nav_title VARCHAR(255),
    nav_location enum_menu_location,
    menu_id INTEGER,
    nav_position enum_nav_position,
    nav_order INTEGER,
    created_by INTEGER,
    created_on INTEGER
);

CREATE TABLE IF NOT EXISTS app_modules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    version VARCHAR(20) NOT NULL,
    type VARCHAR(20),
    description TEXT,
    skip_xss SMALLINT NOT NULL DEFAULT 0,
    is_frontend SMALLINT NOT NULL DEFAULT 0,
    is_backend SMALLINT NOT NULL DEFAULT 0,
    menu VARCHAR(20) NOT NULL,
    enabled SMALLINT NOT NULL DEFAULT 0,
    installed SMALLINT NOT NULL DEFAULT 0,
    is_core SMALLINT NOT NULL DEFAULT 0,
    updated_on INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS app_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    module VARCHAR(50) NOT NULL,
    roles TEXT
);

CREATE INDEX IF NOT EXISTS idx_permissions_group ON app_permissions(group_id);

CREATE TABLE IF NOT EXISTS app_settings (
    slug VARCHAR(30) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    type VARCHAR(100) NOT NULL,
    default_value TEXT NOT NULL,
    value TEXT NOT NULL,
    options TEXT NOT NULL,
    is_required INTEGER NOT NULL DEFAULT 0,
    is_gui INTEGER NOT NULL DEFAULT 0,
    module VARCHAR(50) NOT NULL,
    order_num INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS app_navigation_groups (
    id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    abbrev VARCHAR(50) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nav_groups_abbrev ON app_navigation_groups(abbrev);

CREATE TABLE IF NOT EXISTS app_navigation_links (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL DEFAULT '',
    parent INTEGER,
    link_type VARCHAR(20) NOT NULL DEFAULT 'uri',
    page_id INTEGER,
    module_name VARCHAR(50) NOT NULL DEFAULT '',
    url VARCHAR(255) NOT NULL DEFAULT '',
    uri VARCHAR(255) NOT NULL DEFAULT '',
    navigation_group_id INTEGER NOT NULL DEFAULT 0,
    position INTEGER NOT NULL DEFAULT 0,
    target VARCHAR(10),
    restricted_to VARCHAR(255),
    class VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_nav_links_group ON app_navigation_links(navigation_group_id);

CREATE TABLE IF NOT EXISTS app_pages (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) NOT NULL DEFAULT '',
    class VARCHAR(255) NOT NULL DEFAULT '',
    title VARCHAR(255) NOT NULL DEFAULT '',
    uri TEXT,
    parent_id INTEGER NOT NULL DEFAULT 0,
    type_id VARCHAR(255) NOT NULL,
    entry_id VARCHAR(255),
    css TEXT,
    js TEXT,
    meta_title VARCHAR(255),
    meta_keywords CHAR(32),
    meta_robots_no_index SMALLINT,
    meta_robots_no_follow SMALLINT,
    meta_description TEXT,
    rss_enabled INTEGER NOT NULL DEFAULT 0,
    comments_enabled INTEGER NOT NULL DEFAULT 0,
    status enum_page_status NOT NULL DEFAULT 'draft',
    created_on INTEGER NOT NULL DEFAULT 0,
    updated_on INTEGER NOT NULL DEFAULT 0,
    restricted_to VARCHAR(255),
    is_home INTEGER NOT NULL DEFAULT 0,
    strict_uri SMALLINT NOT NULL DEFAULT 1,
    order_num INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_pages_slug ON app_pages(slug);
CREATE INDEX IF NOT EXISTS idx_pages_parent ON app_pages(parent_id);

CREATE TABLE IF NOT EXISTS app_page_types (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(255) NOT NULL DEFAULT '',
    title VARCHAR(60) NOT NULL,
    description TEXT,
    stream_id INTEGER NOT NULL,
    meta_title VARCHAR(255),
    meta_keywords CHAR(32),
    meta_description TEXT,
    body TEXT NOT NULL,
    css TEXT,
    js TEXT,
    theme_layout VARCHAR(100) NOT NULL DEFAULT 'default',
    updated_on INTEGER NOT NULL,
    save_as_files CHAR(1) NOT NULL DEFAULT 'n',
    content_label VARCHAR(60),
    title_label VARCHAR(100)
);

-- ============================================================================
-- OM (Organizational Management) TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS om_annual_work_plan_budget (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(20),
    annual_work_plan_budget VARCHAR(200),
    tipe_laporan enum_tipe_laporan,
    bulan VARCHAR(16),
    tahun INTEGER,
    nama_file VARCHAR(200),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS om_budget_realization (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(20),
    budget_realization VARCHAR(200),
    tipe_laporan enum_tipe_laporan,
    bulan VARCHAR(16),
    tahun INTEGER,
    nama_file VARCHAR(200),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS om_financial_reports (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(20),
    financial_reports VARCHAR(200),
    tipe_laporan enum_tipe_laporan,
    bulan VARCHAR(16),
    tahun INTEGER,
    nama_file VARCHAR(200),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS om_program_activities (
    id SERIAL PRIMARY KEY,
    kode_institusi VARCHAR(20),
    program_activities VARCHAR(200),
    tipe_laporan enum_tipe_laporan,
    bulan VARCHAR(16),
    tahun INTEGER,
    nama_file VARCHAR(200),
    is_active enum_yes_no DEFAULT 'Y',
    is_delete enum_yes_no DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    deleted_by VARCHAR(50),
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    deleted_date TIMESTAMP
);

-- ============================================================================
-- VIEW: v_dana_transactions
-- ============================================================================
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

-- ============================================================================
-- INSERT: Default DANA payment method
-- ============================================================================
INSERT INTO ref_metode_pembayaran (name, kelompok, url_gambar, bank, payment_type, va_number, start_amount, end_amount, order_list, biaya_admin, tahapan, is_active, is_delete, created_date)
SELECT 'DANA', 'e money', 'dana.png', 'DANA', 'emoney', 0, 10000, 50000000, 1, 0.000,
'1. Pilih metode pembayaran DANA
2. Anda akan diarahkan ke halaman DANA
3. Login dengan akun DANA Anda
4. Konfirmasi pembayaran
5. Pembayaran berhasil',
'Y', 'N', NOW()
WHERE NOT EXISTS (SELECT 1 FROM ref_metode_pembayaran WHERE payment_type = 'emoney' AND bank = 'DANA');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
