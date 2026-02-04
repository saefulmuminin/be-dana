-- --------------------------------------------------------
-- Host:                         34.101.118.36
-- Server version:               8.0.41-google - (Google)
-- Server OS:                    Linux
-- HeidiSQL Version:             12.10.0.7000
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for cintazak_dbcintazakat
CREATE DATABASE IF NOT EXISTS `cintazak_dbcintazakat` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `cintazak_dbcintazakat`;

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign
CREATE TABLE IF NOT EXISTS `adm_campaign` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` int DEFAULT NULL,
  `tipe` enum('zakat','infak') NOT NULL,
  `program_id` int NOT NULL,
  `kategori` varchar(150) NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `target_donasi` bigint DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `bataswaktu_id` int DEFAULT NULL,
  `link_campaign` varchar(100) DEFAULT NULL,
  `prosen_biayaoperasional` decimal(10,2) DEFAULT NULL,
  `biayaoperasional` bigint DEFAULT '0',
  `donasi` bigint DEFAULT NULL,
  `url_fotoutama` varchar(100) DEFAULT NULL,
  `no_rekening` varchar(30) DEFAULT NULL,
  `nama_bank` varchar(100) DEFAULT NULL,
  `atas_nama` varchar(100) DEFAULT NULL,
  `coa_infak` varchar(20) DEFAULT NULL,
  `coaid_infak` int DEFAULT NULL,
  `coa_zakat` varchar(20) DEFAULT NULL,
  `coaid_zakat` int DEFAULT NULL,
  `informasi` text,
  `mustahik_nama` varchar(150) DEFAULT NULL,
  `tipe_mustahik` enum('perorangan','kelompok') DEFAULT NULL,
  `nik_mustahik` varchar(25) DEFAULT NULL,
  `hp_mustahik` varchar(25) DEFAULT NULL,
  `email_mustahik` varchar(100) DEFAULT NULL,
  `alamat_mustahik` text,
  `campaign_latitude` varchar(50) NOT NULL,
  `campaign_longitude` varchar(50) NOT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  `status` enum('draft','publish','closed') DEFAULT NULL,
  `program_pilihan` enum('Y','N') NOT NULL,
  `prioritas` enum('Y','N') NOT NULL,
  `closed_date` datetime DEFAULT NULL,
  `closed_by` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_donasi
CREATE TABLE IF NOT EXISTS `adm_campaign_donasi` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_id` int NOT NULL,
  `tipe_zakat` enum('zakat','infak') NOT NULL,
  `tipe` enum('perorangan','lembaga') NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `npwz` varchar(100) DEFAULT NULL,
  `doa_muzaki` varchar(200) DEFAULT NULL,
  `nominal` bigint DEFAULT NULL,
  `tgl_donasi` date DEFAULT NULL,
  `metode_id` int DEFAULT NULL,
  `prosen_biayaoperasional` decimal(10,2) DEFAULT NULL,
  `biayaoperasional` bigint DEFAULT NULL,
  `donasi` bigint DEFAULT NULL,
  `biaya_admin` bigint DEFAULT NULL,
  `status` enum('belum','berhasil','menunggu','dibatalkan') DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `hamba_allah` enum('Y','N') DEFAULT 'N',
  `no_transaksi` varchar(50) DEFAULT NULL,
  `tanggal` varchar(20) DEFAULT NULL,
  `waktu` varchar(20) DEFAULT NULL,
  `bsz` varchar(200) DEFAULT NULL,
  `no_refrensi` varchar(200) DEFAULT NULL,
  `nama_refrensi` varchar(200) DEFAULT NULL,
  `kode_biller` varchar(200) DEFAULT NULL,
  `url_qris` varchar(200) DEFAULT NULL,
  `url_deeplink` varchar(255) DEFAULT NULL,
  `tgl_expired` datetime DEFAULT NULL,
  `transaksi_id` varchar(50) DEFAULT NULL,
  `order_id` varchar(50) DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_adm_campaign_donasi_adm_campaign` (`campaign_id`),
  CONSTRAINT `FK_adm_campaign_donasi_adm_campaign` FOREIGN KEY (`campaign_id`) REFERENCES `adm_campaign` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=48631 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_histori
CREATE TABLE IF NOT EXISTS `adm_campaign_histori` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_id` int NOT NULL,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `tipe` enum('zakat','infak') NOT NULL,
  `program_id` int NOT NULL,
  `kategori` varchar(150) NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `target_donasi` bigint DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `bataswaktu_id` int DEFAULT NULL,
  `link_campaign` varchar(100) DEFAULT NULL,
  `prosen_biayaoperasional` decimal(10,2) DEFAULT NULL,
  `biayaoperasional` bigint DEFAULT NULL,
  `donasi` bigint DEFAULT NULL,
  `donasi_infak` bigint DEFAULT NULL,
  `donasi_zakat` bigint DEFAULT NULL,
  `url_fotoutama` varchar(100) DEFAULT NULL,
  `no_rekening` varchar(30) DEFAULT NULL,
  `nama_bank` varchar(100) DEFAULT NULL,
  `atas_nama` varchar(100) DEFAULT NULL,
  `coa_infak` varchar(20) DEFAULT NULL,
  `coaid_infak` int DEFAULT NULL,
  `coa_zakat` varchar(20) DEFAULT NULL,
  `coaid_zakat` int DEFAULT NULL,
  `informasi` text,
  `mustahik_nama` varchar(150) DEFAULT NULL,
  `tipe_mustahik` enum('perorangan','kelompok') DEFAULT NULL,
  `nik_mustahik` varchar(25) DEFAULT NULL,
  `hp_mustahik` varchar(25) DEFAULT NULL,
  `email_mustahik` varchar(100) DEFAULT NULL,
  `alamat_mustahik` text,
  `campaign_latitude` varchar(50) NOT NULL,
  `campaign_longitude` varchar(50) NOT NULL,
  `status_histori` varchar(100) DEFAULT NULL,
  `log_histori` text,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  `status` enum('draft','simpan','edit','perpanjangan') DEFAULT NULL,
  `program_pilihan` enum('Y','N') NOT NULL,
  `prioritas` enum('Y','N') NOT NULL,
  `closed_date` datetime DEFAULT NULL,
  `closed_by` int DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_adm_campaign_histori_adm_campaign` (`campaign_id`),
  CONSTRAINT `FK_adm_campaign_histori_adm_campaign` FOREIGN KEY (`campaign_id`) REFERENCES `adm_campaign` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=309 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_info
CREATE TABLE IF NOT EXISTS `adm_campaign_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `tgl_berita` date NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_adm_campaign_info_adm_campaign` (`campaign_id`),
  CONSTRAINT `FK_adm_campaign_info_adm_campaign` FOREIGN KEY (`campaign_id`) REFERENCES `adm_campaign` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_notifikasi
CREATE TABLE IF NOT EXISTS `adm_campaign_notifikasi` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_id` int NOT NULL,
  `donasi_id` int NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `handphone` varchar(100) NOT NULL,
  `alamat` varchar(200) DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_adm_campaign_donasi_adm_campaign` (`campaign_id`),
  KEY `FK_adm_campaign_notifikasi_adm_campaign_donasi` (`donasi_id`),
  CONSTRAINT `adm_campaign_notifikasi_ibfk_1` FOREIGN KEY (`campaign_id`) REFERENCES `adm_campaign` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `FK_adm_campaign_notifikasi_adm_campaign_donasi` FOREIGN KEY (`donasi_id`) REFERENCES `adm_campaign_donasi` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=137 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_pembayaran
CREATE TABLE IF NOT EXISTS `adm_campaign_pembayaran` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_id` int NOT NULL,
  `permohonan_id` int NOT NULL,
  `tgl_pembayaran` date NOT NULL,
  `nominal_distribusi` bigint DEFAULT NULL,
  `no_rekening` varchar(50) DEFAULT NULL,
  `nama_bank` varchar(50) NOT NULL,
  `atas_nama` varchar(50) NOT NULL,
  `permbayaran_biayaoperasional` bigint DEFAULT NULL,
  `bukti_transfer` varchar(50) DEFAULT NULL,
  `catatan` text,
  `status` enum('draft','belum','sudah','kembali') DEFAULT NULL,
  `tindak_lanjut` enum('Y','N') NOT NULL,
  `alasan_kembali` text,
  `tgl_dikembalikan` datetime DEFAULT NULL,
  `userid_pengembali` varchar(50) DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_adm_campaign_pembayaran_adm_campaign` (`campaign_id`),
  CONSTRAINT `FK_adm_campaign_pembayaran_adm_campaign` FOREIGN KEY (`campaign_id`) REFERENCES `adm_campaign` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_pembayaran_bukti
CREATE TABLE IF NOT EXISTS `adm_campaign_pembayaran_bukti` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `permohonan_id` bigint DEFAULT NULL,
  `pembayaran_id` bigint DEFAULT NULL,
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_campaign_permohonan
CREATE TABLE IF NOT EXISTS `adm_campaign_permohonan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `campaign_id` int NOT NULL,
  `kode_permohonan` varchar(20) DEFAULT NULL,
  `tipe_permohonan` varchar(50) DEFAULT NULL,
  `tgl_permohonan` date DEFAULT NULL,
  `permohonan_pencairan` bigint DEFAULT NULL,
  `permohonan_biayaoperasional` bigint DEFAULT NULL,
  `catatan` text,
  `status` enum('draft','belum','sudah','kembali') DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_adm_campaign_permohonan_adm_campaign` (`campaign_id`),
  CONSTRAINT `FK_adm_campaign_permohonan_adm_campaign` FOREIGN KEY (`campaign_id`) REFERENCES `adm_campaign` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_manual
CREATE TABLE IF NOT EXISTS `adm_manual` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `manual_file` varchar(255) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_mustahik
CREATE TABLE IF NOT EXISTS `adm_mustahik` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipe` enum('perorangan','kelompok') NOT NULL,
  `nama` varchar(100) NOT NULL,
  `foto` varchar(100) DEFAULT NULL,
  `nik` varchar(25) DEFAULT NULL,
  `nim` varchar(50) DEFAULT NULL,
  `npwp` varchar(25) DEFAULT NULL,
  `npwz` varchar(25) DEFAULT NULL,
  `handphone` varchar(25) DEFAULT NULL,
  `no_rekening` varchar(25) DEFAULT NULL,
  `nama_bank` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `alamat` text,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=439 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_muzaki
CREATE TABLE IF NOT EXISTS `adm_muzaki` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipe` enum('perorangan','lembaga') NOT NULL,
  `kelompok` enum('BAZNAS_prov','BAZNAS_kab','LAZ_prov','LAZ_kab','UPZ','LAZNAS','Pusat') DEFAULT NULL,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `nama` varchar(200) DEFAULT NULL,
  `foto` varchar(100) DEFAULT NULL,
  `nik` varchar(25) DEFAULT NULL,
  `npwp` varchar(25) DEFAULT NULL,
  `npwz` varchar(25) DEFAULT NULL,
  `npwz_bg` varchar(255) NOT NULL,
  `tgl_daftar` varchar(16) NOT NULL,
  `handphone` varchar(25) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `alamat` text,
  `email_cp` varchar(100) DEFAULT NULL,
  `latitude` varchar(30) DEFAULT NULL,
  `longitude` varchar(30) DEFAULT NULL,
  `phone_cp` varchar(100) DEFAULT NULL,
  `name_cp` varchar(100) DEFAULT NULL,
  `tgl_lahir` date DEFAULT NULL,
  `jenis_kelamin` enum('pria','wanita','') DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12533 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_muzaki_npwz
CREATE TABLE IF NOT EXISTS `adm_muzaki_npwz` (
  `id` int NOT NULL AUTO_INCREMENT,
  `muzaki_id` int DEFAULT NULL,
  `tipe` enum('perorangan','lembaga') NOT NULL,
  `kelompok` enum('BAZNAS_prov','BAZNAS_kab','LAZ_prov','LAZ_kab','UPZ','LAZNAS','Pusat') DEFAULT NULL,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `npwz` varchar(25) DEFAULT NULL,
  `nama_npwz` varchar(100) DEFAULT NULL,
  `npwz_bg` varchar(255) NOT NULL,
  `apikey` varchar(255) DEFAULT NULL,
  `tgl_daftar` date DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  `is_primary` enum('Y','N') NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1036 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_pegawai
CREATE TABLE IF NOT EXISTS `adm_pegawai` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `nia` varchar(50) DEFAULT NULL,
  `nama` varchar(100) NOT NULL,
  `foto` varchar(100) DEFAULT NULL,
  `nik` varchar(25) DEFAULT NULL,
  `npwp` varchar(25) DEFAULT NULL,
  `handphone` varchar(25) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `alamat` text,
  `is_cp` enum('Y','N') DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=247 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.adm_program
CREATE TABLE IF NOT EXISTS `adm_program` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_menu
CREATE TABLE IF NOT EXISTS `app_menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `menu_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `menu_location` enum('Backend','Frontend') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `menu_type` enum('module','page','uri','url') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `module_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `folder` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `controller` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `method` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `params` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `page_id` int DEFAULT NULL,
  `site_uri` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url_link` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `target` enum('_blank','_self') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `icon` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `class` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_on` int DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_menu_nav
CREATE TABLE IF NOT EXISTS `app_menu_nav` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_id` int DEFAULT NULL,
  `nav_type` enum('label','link') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nav_title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nav_location` enum('Backend','Frontend') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `menu_id` int DEFAULT NULL,
  `nav_position` enum('Main','Top','Bottom') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nav_order` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_on` int DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_modules
CREATE TABLE IF NOT EXISTS `app_modules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `slug` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `version` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `type` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `skip_xss` tinyint(1) NOT NULL,
  `is_frontend` tinyint(1) NOT NULL,
  `is_backend` tinyint(1) NOT NULL,
  `menu` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `installed` tinyint(1) NOT NULL,
  `is_core` tinyint(1) NOT NULL,
  `updated_on` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `slug` (`slug`) USING BTREE,
  KEY `enabled` (`enabled`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_navigation_groups
CREATE TABLE IF NOT EXISTS `app_navigation_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `abbrev` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `abbrev` (`abbrev`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_navigation_links
CREATE TABLE IF NOT EXISTS `app_navigation_links` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `parent` int DEFAULT NULL,
  `link_type` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'uri',
  `page_id` int DEFAULT NULL,
  `module_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `url` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `uri` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `navigation_group_id` int NOT NULL DEFAULT '0',
  `position` int NOT NULL DEFAULT '0',
  `target` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `restricted_to` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `class` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `navigation_group_id` (`navigation_group_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_pages
CREATE TABLE IF NOT EXISTS `app_pages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `slug` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `class` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `title` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `uri` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `parent_id` int NOT NULL DEFAULT '0',
  `type_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `entry_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `css` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `js` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `meta_title` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `meta_keywords` char(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `meta_robots_no_index` tinyint(1) DEFAULT NULL,
  `meta_robots_no_follow` tinyint(1) DEFAULT NULL,
  `meta_description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `rss_enabled` int NOT NULL DEFAULT '0',
  `comments_enabled` int NOT NULL DEFAULT '0',
  `status` enum('draft','live') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'draft',
  `created_on` int NOT NULL DEFAULT '0',
  `updated_on` int NOT NULL DEFAULT '0',
  `restricted_to` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `is_home` int NOT NULL DEFAULT '0',
  `strict_uri` tinyint(1) NOT NULL DEFAULT '1',
  `order` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `slug` (`slug`) USING BTREE,
  KEY `parent_id` (`parent_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_page_types
CREATE TABLE IF NOT EXISTS `app_page_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `slug` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT '',
  `title` varchar(60) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `stream_id` int NOT NULL,
  `meta_title` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `meta_keywords` char(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `meta_description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `body` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `css` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `js` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `theme_layout` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'default',
  `updated_on` int NOT NULL,
  `save_as_files` char(1) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'n',
  `content_label` varchar(60) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `title_label` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_permissions
CREATE TABLE IF NOT EXISTS `app_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `module` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `roles` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `group_id` (`group_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.app_settings
CREATE TABLE IF NOT EXISTS `app_settings` (
  `slug` varchar(30) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `title` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `type` set('text','textarea','password','select','select-multiple','radio','checkbox') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `default` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `value` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `options` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `is_required` int NOT NULL,
  `is_gui` int NOT NULL,
  `module` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `order` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`slug`) USING BTREE,
  UNIQUE KEY `unique_slug` (`slug`) USING BTREE,
  KEY `slug` (`slug`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.geo_provinces
CREATE TABLE IF NOT EXISTS `geo_provinces` (
  `id` bigint NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `alt_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `latitude` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `longitude` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.geo_regencies
CREATE TABLE IF NOT EXISTS `geo_regencies` (
  `id` bigint NOT NULL,
  `province_id` bigint DEFAULT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `alt_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `latitude` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `longitude` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_id` (`id`),
  KEY `idx_prov_id` (`province_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.groups
CREATE TABLE IF NOT EXISTS `groups` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `description` varchar(100) NOT NULL,
  `created_by` int DEFAULT NULL,
  `created_on` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_visible` tinyint(1) NOT NULL DEFAULT '1',
  `has_admin_access` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb3;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.groups_roles
CREATE TABLE IF NOT EXISTS `groups_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `assign` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.login_attempts
CREATE TABLE IF NOT EXISTS `login_attempts` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(45) NOT NULL,
  `login` varchar(100) NOT NULL,
  `time` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.log_api
CREATE TABLE IF NOT EXISTS `log_api` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `aplikasi` varchar(100) DEFAULT NULL,
  `url_api` varchar(200) DEFAULT NULL,
  `parameter` text,
  `response` text,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5036 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.log_api_midtrans
CREATE TABLE IF NOT EXISTS `log_api_midtrans` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `aplikasi` varchar(100) DEFAULT NULL,
  `url_api` varchar(200) DEFAULT NULL,
  `parameter` text,
  `response` text,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.om_annual_work_plan_budget
CREATE TABLE IF NOT EXISTS `om_annual_work_plan_budget` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(20) DEFAULT NULL,
  `annual_work_plan_budget` varchar(200) DEFAULT NULL,
  `tipe_laporan` enum('bulanan','tahunan') DEFAULT NULL,
  `bulan` varchar(16) DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  `nama_file` varchar(200) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.om_budget_realization
CREATE TABLE IF NOT EXISTS `om_budget_realization` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(20) DEFAULT NULL,
  `budget_realization` varchar(200) DEFAULT NULL,
  `tipe_laporan` enum('bulanan','tahunan') DEFAULT NULL,
  `bulan` varchar(16) DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  `nama_file` varchar(200) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.om_financial_reports
CREATE TABLE IF NOT EXISTS `om_financial_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(20) DEFAULT NULL,
  `financial_reports` varchar(200) DEFAULT NULL,
  `tipe_laporan` enum('bulanan','tahunan') DEFAULT NULL,
  `bulan` varchar(16) DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  `nama_file` varchar(200) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.om_program_activities
CREATE TABLE IF NOT EXISTS `om_program_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(20) DEFAULT NULL,
  `program_activities` varchar(200) DEFAULT NULL,
  `tipe_laporan` enum('bulanan','tahunan') DEFAULT NULL,
  `bulan` varchar(16) DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  `nama_file` varchar(200) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_banner
CREATE TABLE IF NOT EXISTS `pub_banner` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar` varchar(255) NOT NULL,
  `link` varbinary(255) NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `width` varchar(50) DEFAULT NULL,
  `height` varchar(50) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_banner_log
CREATE TABLE IF NOT EXISTS `pub_banner_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(100) NOT NULL,
  `tanggal` date NOT NULL,
  `browser` varchar(200) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=900103 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_banner_settings
CREATE TABLE IF NOT EXISTS `pub_banner_settings` (
  `view` enum('random','slide') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `width` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `height` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_berita
CREATE TABLE IF NOT EXISTS `pub_berita` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `tgl_berita` date NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  `kategori` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_download_app
CREATE TABLE IF NOT EXISTS `pub_download_app` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar_playstore` varchar(100) NOT NULL,
  `url_playstore` varchar(255) NOT NULL,
  `url_gambar_appstore` varchar(100) NOT NULL,
  `url_appstore` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_faq
CREATE TABLE IF NOT EXISTS `pub_faq` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_hubungi
CREATE TABLE IF NOT EXISTS `pub_hubungi` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar` varchar(255) NOT NULL,
  `alamat` text NOT NULL,
  `telepon` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `latitude` varchar(50) NOT NULL,
  `longitude` varchar(50) NOT NULL,
  `url_map` varchar(255) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_kirimpesan
CREATE TABLE IF NOT EXISTS `pub_kirimpesan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `handphone` varchar(100) DEFAULT NULL,
  `pesan` text NOT NULL,
  `ipaddress` varchar(200) NOT NULL,
  `browser_aplikasi` varchar(200) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_legal
CREATE TABLE IF NOT EXISTS `pub_legal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `url_link` varchar(255) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_legal_img
CREATE TABLE IF NOT EXISTS `pub_legal_img` (
  `id` int NOT NULL AUTO_INCREMENT,
  `legal_id` int NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `url_link` varchar(255) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_penghargaan
CREATE TABLE IF NOT EXISTS `pub_penghargaan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `url_gambar` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `url_link` varchar(255) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_slider
CREATE TABLE IF NOT EXISTS `pub_slider` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `url_link` varchar(255) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  `is_deleted` enum('0','1') DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_syarat_ketentuan
CREATE TABLE IF NOT EXISTS `pub_syarat_ketentuan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `tgl_berita` date NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.pub_tentang
CREATE TABLE IF NOT EXISTS `pub_tentang` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `content` text NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_bank
CREATE TABLE IF NOT EXISTS `ref_bank` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `url_file` varchar(100) DEFAULT NULL,
  `total_view` int DEFAULT NULL,
  `total_download` int DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_batas_waktu
CREATE TABLE IF NOT EXISTS `ref_batas_waktu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `nilai` int NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_campaign_kategori
CREATE TABLE IF NOT EXISTS `ref_campaign_kategori` (
  `id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_coa
CREATE TABLE IF NOT EXISTS `ref_coa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `description` text,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8834 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_coa_backup
CREATE TABLE IF NOT EXISTS `ref_coa_backup` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `description` text,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=976 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_coa_via
CREATE TABLE IF NOT EXISTS `ref_coa_via` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `simbakey` varchar(255) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `description` text,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_dana_sosial
CREATE TABLE IF NOT EXISTS `ref_dana_sosial` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `code` char(15) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `year_activity` int DEFAULT NULL,
  `is_active` enum('Y','N') DEFAULT 'Y',
  `is_delete` enum('Y','N') DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8577 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_kabupaten
CREATE TABLE IF NOT EXISTS `ref_kabupaten` (
  `id` char(4) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `province_id` char(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `is_active` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'N',
  `created_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `updated_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `deleted_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `regencies_province_id_index` (`province_id`),
  CONSTRAINT `regencies_province_id_foreign` FOREIGN KEY (`province_id`) REFERENCES `ref_provinsi` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_kantor
CREATE TABLE IF NOT EXISTS `ref_kantor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `tipe` enum('BAZNAS_prov','BAZNAS_kab','LAZ_prov','LAZ_kab','UPZ','LAZNAS','Pusat') NOT NULL,
  `province_id` char(2) DEFAULT NULL,
  `regency_id` char(4) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `alamat` text,
  `telepon` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `cp` varchar(50) DEFAULT NULL,
  `apikey` varchar(255) DEFAULT NULL,
  `latitude` varchar(50) DEFAULT NULL,
  `longitude` varchar(50) DEFAULT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=737 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_kantor_logo
CREATE TABLE IF NOT EXISTS `ref_kantor_logo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kode_institusi` varchar(50) DEFAULT NULL,
  `logo` varchar(255) NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_kecamatan
CREATE TABLE IF NOT EXISTS `ref_kecamatan` (
  `id` char(7) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `regency_id` char(4) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `is_active` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'N',
  `created_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `updated_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `deleted_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `districts_id_index` (`regency_id`),
  CONSTRAINT `districts_regency_id_foreign` FOREIGN KEY (`regency_id`) REFERENCES `ref_kabupaten` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_kelurahan
CREATE TABLE IF NOT EXISTS `ref_kelurahan` (
  `id` char(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `district_id` char(7) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `is_active` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'N',
  `created_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `updated_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `deleted_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `villages_district_id_index` (`district_id`),
  CONSTRAINT `villages_district_id_foreign` FOREIGN KEY (`district_id`) REFERENCES `ref_kecamatan` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_metode_pembayaran
CREATE TABLE IF NOT EXISTS `ref_metode_pembayaran` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `kelompok` enum('pembayaran instan','virtual account','transfer bank','internet banking','counter store','e money','credit card') NOT NULL,
  `url_gambar` varchar(100) NOT NULL,
  `bank` varchar(20) NOT NULL,
  `payment_type` varchar(50) NOT NULL,
  `va_number` int NOT NULL,
  `start_amount` bigint NOT NULL,
  `end_amount` bigint NOT NULL,
  `order_list` int NOT NULL,
  `biaya_admin` decimal(12,3) DEFAULT NULL,
  `tahapan` text,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_news_kategori
CREATE TABLE IF NOT EXISTS `ref_news_kategori` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_nominal_donasi
CREATE TABLE IF NOT EXISTS `ref_nominal_donasi` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `nilai` int NOT NULL,
  `is_active` enum('Y','N') NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') NOT NULL DEFAULT 'N',
  `created_by` varchar(50) DEFAULT NULL,
  `updated_by` varchar(50) DEFAULT NULL,
  `deleted_by` varchar(50) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `updated_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.ref_provinsi
CREATE TABLE IF NOT EXISTS `ref_provinsi` (
  `id` char(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `is_active` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'Y',
  `is_delete` enum('Y','N') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'N',
  `created_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `updated_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `deleted_by` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `update_date` datetime DEFAULT NULL,
  `deleted_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_by` int DEFAULT NULL,
  `created_on` int DEFAULT NULL,
  `is_visible` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.roles_menu
CREATE TABLE IF NOT EXISTS `roles_menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` int DEFAULT NULL,
  `menu_id` int DEFAULT NULL,
  `all_access` tinyint(1) NOT NULL DEFAULT '0',
  `insert` tinyint(1) NOT NULL DEFAULT '0',
  `read` tinyint(1) NOT NULL DEFAULT '0',
  `edit` tinyint(1) NOT NULL DEFAULT '0',
  `delete` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=637 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(45) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(254) NOT NULL,
  `salt` varchar(6) DEFAULT NULL,
  `activation_selector` varchar(255) DEFAULT NULL,
  `activation_code` varchar(255) DEFAULT NULL,
  `forgotten_password_selector` varchar(255) DEFAULT NULL,
  `forgotten_password_code` varchar(255) DEFAULT NULL,
  `forgotten_password_time` int unsigned DEFAULT NULL,
  `remember_selector` varchar(255) DEFAULT NULL,
  `remember_code` varchar(255) DEFAULT NULL,
  `created_on` int unsigned NOT NULL,
  `last_login` int unsigned DEFAULT NULL,
  `active` tinyint unsigned DEFAULT NULL,
  `full_name` varchar(50) DEFAULT NULL,
  `nia` varchar(50) DEFAULT NULL,
  `tipe` varchar(15) DEFAULT NULL,
  `gopay_id` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `handphone` varchar(15) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `muzaki_id` int DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uc_activation_selector` (`activation_selector`) USING BTREE,
  UNIQUE KEY `uc_forgotten_password_selector` (`forgotten_password_selector`) USING BTREE,
  UNIQUE KEY `uc_remember_selector` (`remember_selector`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4092 DEFAULT CHARSET=utf8mb3;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.users_google
CREATE TABLE IF NOT EXISTS `users_google` (
  `email` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `familyName` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `givenName` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hd` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id` bigint DEFAULT NULL,
  `link` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `locale` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `picture` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `verifiedEmail` tinyint(1) DEFAULT '0',
  `signin_date` datetime DEFAULT NULL,
  KEY `email` (`email`) USING BTREE,
  KEY `id` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.users_groups
CREATE TABLE IF NOT EXISTS `users_groups` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned NOT NULL,
  `group_id` mediumint unsigned NOT NULL,
  `assign` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uc_users_groups` (`user_id`,`group_id`) USING BTREE,
  KEY `fk_users_groups_users1_idx` (`user_id`) USING BTREE,
  KEY `fk_users_groups_groups1_idx` (`group_id`) USING BTREE,
  CONSTRAINT `fk_users_groups_groups1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_users_groups_users1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=389 DEFAULT CHARSET=utf8mb3;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.users_otp
CREATE TABLE IF NOT EXISTS `users_otp` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(45) NOT NULL,
  `email` varchar(254) NOT NULL,
  `tipe` varchar(254) NOT NULL,
  `code_otp` varchar(255) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `active` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4319 DEFAULT CHARSET=utf8mb3 ROW_FORMAT=DYNAMIC;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.users_otp_expsec
CREATE TABLE IF NOT EXISTS `users_otp_expsec` (
  `id` int NOT NULL AUTO_INCREMENT,
  `second` int DEFAULT NULL,
  `appl_type` varchar(10) DEFAULT NULL,
  `active` int DEFAULT NULL,
  `created_by` varchar(155) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table cintazak_dbcintazakat.users_profiles
CREATE TABLE IF NOT EXISTS `users_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `ordering_count` int DEFAULT NULL,
  `user_id` int unsigned NOT NULL,
  `display_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `first_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `last_name` varchar(50) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
  `company` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `lang` varchar(2) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL DEFAULT 'en',
  `bio` text CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci,
  `dob` int DEFAULT NULL,
  `gender` set('m','f','') CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `mobile` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `address_line1` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `address_line2` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `address_line3` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `postcode` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `website` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `updated_on` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `user_id` (`user_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

-- Data exporting was unselected.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
