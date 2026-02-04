-- ============================================================================
-- MINIMAL PostgreSQL Schema for DANA Mini Program API
-- Run this on Neon PostgreSQL for quick setup
-- ============================================================================

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS log_api CASCADE;
DROP TABLE IF EXISTS adm_campaign_donasi CASCADE;
DROP TABLE IF EXISTS ref_metode_pembayaran CASCADE;
DROP TABLE IF EXISTS adm_campaign CASCADE;
DROP TABLE IF EXISTS adm_muzaki CASCADE;
DROP TABLE IF EXISTS adm_user CASCADE;

-- Drop existing types
DROP TYPE IF EXISTS enum_tipe_zakat CASCADE;
DROP TYPE IF EXISTS enum_tipe_muzaki CASCADE;
DROP TYPE IF EXISTS enum_status_donasi CASCADE;
DROP TYPE IF EXISTS enum_yes_no CASCADE;

-- ============================================================================
-- CREATE ENUM TYPES
-- ============================================================================
CREATE TYPE enum_tipe_zakat AS ENUM ('zakat', 'infak');
CREATE TYPE enum_tipe_muzaki AS ENUM ('perorangan', 'lembaga');
CREATE TYPE enum_status_donasi AS ENUM ('belum', 'berhasil', 'menunggu', 'dibatalkan');
CREATE TYPE enum_yes_no AS ENUM ('Y', 'N');

-- ============================================================================
-- TABLE: adm_user (User accounts)
-- ============================================================================
CREATE TABLE adm_user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255),
    tipe VARCHAR(20) DEFAULT 'user',
    full_name VARCHAR(100),
    handphone VARCHAR(20),
    muzaki_id INTEGER,
    dana_access_token TEXT,
    dana_refresh_token TEXT,
    dana_external_id VARCHAR(100),
    dana_user_id VARCHAR(100),
    dana_token_expires_at TIMESTAMP,
    dana_linked_at TIMESTAMP,
    external_id VARCHAR(100),
    is_active VARCHAR(1) DEFAULT 'Y',
    is_delete VARCHAR(1) DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE INDEX idx_user_email ON adm_user(email);
CREATE INDEX idx_user_dana_external ON adm_user(dana_external_id);
CREATE INDEX idx_user_external_id ON adm_user(external_id);

-- ============================================================================
-- TABLE: adm_muzaki (Donors)
-- ============================================================================
CREATE TABLE adm_muzaki (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    nama VARCHAR(100),
    tipe enum_tipe_muzaki DEFAULT 'perorangan',
    handphone VARCHAR(20),
    npwz VARCHAR(50),
    kode_institusi VARCHAR(50),
    alamat TEXT,
    is_active VARCHAR(1) DEFAULT 'Y',
    is_delete VARCHAR(1) DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE INDEX idx_muzaki_email ON adm_muzaki(email);
CREATE INDEX idx_muzaki_npwz ON adm_muzaki(npwz);

-- ============================================================================
-- TABLE: adm_campaign (Campaigns/Programs)
-- ============================================================================
CREATE TABLE adm_campaign (
    id SERIAL PRIMARY KEY,
    kode_institusi INTEGER,
    tipe enum_tipe_zakat DEFAULT 'infak',
    program_id INTEGER DEFAULT 1,
    kategori VARCHAR(150) DEFAULT 'Donasi',
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(255),
    target_donasi BIGINT DEFAULT 0,
    start_date DATE,
    end_date DATE,
    prosen_biayaoperasional DECIMAL(10,2) DEFAULT 0,
    donasi BIGINT DEFAULT 0,
    url_fotoutama VARCHAR(255),
    informasi TEXT,
    is_active VARCHAR(1) DEFAULT 'Y',
    is_delete VARCHAR(1) DEFAULT 'N',
    status VARCHAR(20) DEFAULT 'publish',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE INDEX idx_campaign_slug ON adm_campaign(slug);

-- ============================================================================
-- TABLE: ref_metode_pembayaran (Payment Methods)
-- ============================================================================
CREATE TABLE ref_metode_pembayaran (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    kode VARCHAR(50),
    payment_type VARCHAR(50) DEFAULT 'emoney',
    payment_channel VARCHAR(50),
    biaya_admin DECIMAL(10,2) DEFAULT 0,
    url_gambar VARCHAR(255),
    is_active VARCHAR(1) DEFAULT 'Y',
    is_delete VARCHAR(1) DEFAULT 'N',
    created_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default DANA payment method
INSERT INTO ref_metode_pembayaran (id, name, kode, payment_type, payment_channel, biaya_admin, is_active)
VALUES (2, 'DANA', 'DANA', 'emoney', 'DANA', 0, 'Y');

-- ============================================================================
-- TABLE: adm_campaign_donasi (Donations)
-- ============================================================================
CREATE TABLE adm_campaign_donasi (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36),
    checksum VARCHAR(64),
    order_id VARCHAR(50),
    partner_reference_no VARCHAR(100),
    campaign_id INTEGER,
    muzaki_id INTEGER,
    metode_id INTEGER DEFAULT 2,
    tipe_zakat VARCHAR(20) DEFAULT 'infak',
    tipe VARCHAR(20) DEFAULT 'perorangan',
    nama_lengkap VARCHAR(100),
    email VARCHAR(100) NOT NULL,
    npwz VARCHAR(100),
    doa_muzaki VARCHAR(500),
    nominal BIGINT DEFAULT 0,
    prosen_biayaoperasional DECIMAL(10,2) DEFAULT 0,
    biayaoperasional BIGINT DEFAULT 0,
    biaya_admin BIGINT DEFAULT 0,
    donasi BIGINT DEFAULT 0,
    donasi_net DECIMAL(15,2) DEFAULT 0,
    total_bayar DECIMAL(15,2) DEFAULT 0,
    hamba_allah VARCHAR(1) DEFAULT 'N',
    status VARCHAR(20) DEFAULT 'belum',
    tgl_donasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dana_reference_no VARCHAR(100),
    dana_status VARCHAR(50),
    dana_web_redirect_url VARCHAR(500),
    dana_ott_token VARCHAR(500),
    dana_paid_at TIMESTAMP,
    is_active VARCHAR(1) DEFAULT 'Y',
    is_delete VARCHAR(1) DEFAULT 'N',
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE INDEX idx_donasi_order_id ON adm_campaign_donasi(order_id);
CREATE INDEX idx_donasi_partner_ref ON adm_campaign_donasi(partner_reference_no);
CREATE INDEX idx_donasi_dana_ref ON adm_campaign_donasi(dana_reference_no);
CREATE INDEX idx_donasi_email ON adm_campaign_donasi(email);
CREATE INDEX idx_donasi_muzaki_id ON adm_campaign_donasi(muzaki_id);
CREATE INDEX idx_donasi_campaign_id ON adm_campaign_donasi(campaign_id);

-- ============================================================================
-- TABLE: log_api (API Logs)
-- ============================================================================
CREATE TABLE log_api (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    aplikasi VARCHAR(50),
    url_api VARCHAR(500),
    parameter TEXT,
    response TEXT,
    is_active VARCHAR(1) DEFAULT 'Y',
    is_delete VARCHAR(1) DEFAULT 'N',
    created_by VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_log_name ON log_api(name);
CREATE INDEX idx_log_aplikasi ON log_api(aplikasi);

-- ============================================================================
-- INSERT SAMPLE DATA
-- ============================================================================

-- Sample Campaign
INSERT INTO adm_campaign (id, name, slug, tipe, kategori, target_donasi, prosen_biayaoperasional, informasi, status, is_active)
VALUES
(1, 'Donasi Umum', 'donasi-umum', 'infak', 'Donasi', 100000000, 0, 'Program donasi umum untuk membantu sesama', 'publish', 'Y'),
(2, 'Zakat Maal', 'zakat-maal', 'zakat', 'Zakat', 500000000, 0, 'Program zakat maal', 'publish', 'Y'),
(3, 'Bantuan Bencana', 'bantuan-bencana', 'infak', 'Kemanusiaan', 200000000, 5, 'Program bantuan korban bencana', 'publish', 'Y');

-- Sample User
INSERT INTO adm_user (email, full_name, tipe, is_active)
VALUES ('admin@cintazakat.id', 'Admin Cinta Zakat', 'admin', 'Y');

-- ============================================================================
-- DONE! Database ready for DANA Mini Program API
-- ============================================================================
