# Campaign API Documentation

## Overview

API endpoints untuk mengelola campaign/program zakat dan infak. API ini menggantikan external API (api.cintazakat.id) dengan backend internal.

## Base URL

**Production:** `https://be-dana.vercel.app/api/v1`  
**Development:** `http://localhost:5000/api/v1`

## Endpoints

### 1. List Campaign

**Endpoint:** `POST /kegiatan/index`

**Description:** Mengambil daftar semua campaign dengan filter dan pagination

**Request Body:**

```json
{
  "limit": 20,
  "offset": 0,
  "tipe": "zakat",         // optional: "zakat" atau "infak"
  "institusi": "BAZNAS",   // optional: nama institusi
  "kategori": "Pendidikan", // optional: nama kategori
  "sort": "terbaru"        // optional: "terbaru", "terlama", "terkumpul"
}
```

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": [
    {
      "id": "1",
      "judul": "Zakat Fitrah 2024",
      "slug": "zakat-fitrah-2024",
      "deskripsi": "Program zakat fitrah...",
      "url_gambar": "https://...",
      "nama_lembaga": "BAZNAS",
      "kategori": "Zakat",
      "tipe": "zakat",
      "total_terkumpul": "5000000",
      "total_kebutuhan": "10000000",
      "operasional_terkumpul": "500000",
      "operasional_kebutuhan": "1000000",
      "sisa_hari": 30,
      "created_date": "2024-01-01T00:00:00",
      "jumlah_muzaki": 150
    }
  ]
}
```

---

### 2. Search Campaign

**Endpoint:** `POST /kegiatan/search`

**Description:** Mencari campaign berdasarkan keyword

**Request Body:**

```json
{
  "keyword": "zakat",
  "limit": 20,
  "offset": 0
}
```

**Response:** Same as List Campaign

---

### 3. Campaign Detail

**Endpoint:** `POST /kegiatan/detail`

**Description:** Mengambil detail campaign beserta list muzaki

**Request Body:**

```json
{
  "id": "1"
}
```

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": {
    "id": "1",
    "judul": "Zakat Fitrah 2024",
    "deskripsi": "Program zakat fitrah...",
    "informasi": "Detail informasi lengkap...",
    "url_gambar": "https://...",
    "nama_lembaga": "BAZNAS",
    "kategori": "Zakat",
    "tipe": "zakat",
    "total_terkumpul": "5000000",
    "total_kebutuhan": "10000000",
    "operasional_terkumpul": "500000",
    "operasional_kebutuhan": "1000000",
    "sisa_hari": 30,
    "created_date": "2024-01-01T00:00:00",
    "jumlah_muzaki": 150,
    "list_muzaki": [
      {
        "nama_muzaki": "Ahmad S***",
        "total_zakat": "100000",
        "tgl_donasi": "2024-01-15T10:00:00",
        "doa_muzaki": "Semoga berkah"
      }
    ]
  }
}
```

---

### 4. Filter by Institution

**Endpoint:** `POST /listfilter/byinstitusi`

**Description:** Mengambil daftar institusi untuk filter

**Request Body:** `{}`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": [
    {
      "name": "BAZNAS"
    },
    {
      "name": "Dompet Dhuafa"
    }
  ]
}
```

---

### 5. Filter by Category

**Endpoint:** `POST /listfilter/bycategory`

**Description:** Mengambil daftar kategori untuk filter

**Request Body:** `{}`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": [
    {
      "category": "Pendidikan"
    },
    {
      "category": "Kesehatan"
    }
  ]
}
```

---

## Content Endpoints

### 6. Banner List

**Endpoint:** `POST /banner/index`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": []
}
```

---

### 7. FAQ List

**Endpoint:** `POST /faq/index`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": []
}
```

---

### 8. Tentang Kami

**Endpoint:** `POST /tentang/index`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": {
    "judul": "Tentang Kami",
    "deskripsi": "Informasi tentang organisasi"
  }
}
```

---

### 9. Syarat & Ketentuan

**Endpoint:** `POST /tentang/syaratketentuan`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": {
    "judul": "Syarat dan Ketentuan",
    "deskripsi": "Syarat dan ketentuan penggunaan"
  }
}
```

---

### 10. Contact Info

**Endpoint:** `POST /contact/index`

**Response:**

```json
{
  "code": 200,
  "message": "Success",
  "results": {
    "email": "info@example.com",
    "phone": "021-12345678",
    "address": "Jakarta, Indonesia"
  }
}
```

---

### 11. Send Message

**Endpoint:** `POST /sendmessage`

**Request Body:**

```json
{
  "name": "Nama Pengirim",
  "email": "email@example.com",
  "message": "Pesan yang ingin disampaikan"
}
```

**Response:**

```json
{
  "code": 200,
  "message": "Pesan berhasil dikirim",
  "results": null
}
```

---

## Migration Guide

### Untuk Mini-App

1. **Update config.js:**

   ```javascript
   // Ganti dari external API
   API_CAMPAIGN_BASE: 'https://api.cintazakat.id'
   
   // Menjadi internal API
   API_CAMPAIGN_BASE: 'https://be-dana.vercel.app/api/v1'
   ```

2. **Update semua request URL:**

   ```javascript
   // Sebelumnya
   url: 'https://api.cintazakat.id/kegiatan/index'
   
   // Sekarang
   url: `${CONFIG.API_CAMPAIGN_BASE}/kegiatan/index`
   ```

3. **Test di development:**

   ```javascript
   // Untuk local testing
   API_CAMPAIGN_BASE: 'http://localhost:5000/api/v1'
   ```

### Database Requirements

Campaign API membutuhkan tabel berikut:

1. **adm_campaign** - Tabel campaign/program
   - id, judul, slug, deskripsi, informasi
   - url_fotoutama, nama_lembaga, kategori, tipe
   - total_kebutuhan, operasional_kebutuhan
   - tgl_selesai, prioritas, status
   - is_active, is_delete, created_date

2. **adm_campaign_donasi** - Tabel donasi (sudah ada)
   - campaign_id, nominal, status
   - nama_lengkap, hamba_allah
   - created_date

## Error Responses

All endpoints return consistent error format:

```json
{
  "code": 400,
  "message": "Error message",
  "results": null
}
```

**Error Codes:**

- `400` - Bad Request (missing required fields)
- `404` - Not Found (campaign tidak ditemukan)
- `500` - Internal Server Error
