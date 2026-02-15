# API Kegiatan Documentation

API untuk mengelola campaign/kegiatan zakat dan infak, menggantikan API eksternal cintazakat.id.

## Base URL

**Production:** `https://be-dana.vercel.app`

**Local Development:** `http://127.0.0.1:8899`

---

## Endpoints

### 1. List Campaigns

Get list of all campaigns with pagination and filters.

**Endpoint:** `POST /api/v1/kegiatan/index`

**Request Body:**
```json
{
  "limit": 20,
  "offset": 0,
  "tipe": "zakat",      // optional: "zakat" or "infak"
  "kategori": "Lainnya", // optional: filter by category
  "sort": "terbaru"      // optional: "terbaru", "terlama", or "terkumpul"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "sukses",
  "count": 10,
  "offset": 0,
  "limit": "10",
  "results": [
    {
      "id": "84",
      "judul": "Zakat Fitrah",
      "tipe_zakat": "zakat",
      "kategori": "Lainnya",
      "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Zakat_Fitrah1.jpg",
      "total_terkumpul": "0",
      "total_kebutuhan": "1000000000",
      "batas_waktu": "18250",
      "created_date": "2026-02-04 11:34:55",
      "start_date": "2026-02-04",
      "end_date": "9999-12-31",
      "abstract": "Zakat fitrah adalah kebiasaan baik...",
      "sisa_hari": "Selamanya",
      "nama_lembaga": "BAZNAS RI (Pusat)",
      "kode_institusi": 3171100,
      "apikey": ""
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST https://be-dana.vercel.app/api/v1/kegiatan/index \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "offset": 0}'
```

---

### 2. Search Campaigns

Search campaigns by keyword.

**Endpoint:** `POST /api/v1/kegiatan/search`

**Request Body:**
```json
{
  "keyword": "zakat",
  "limit": 20,
  "offset": 0
}
```

**Response:** Same format as List Campaigns

**cURL Example:**
```bash
curl -X POST https://be-dana.vercel.app/api/v1/kegiatan/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "zakat", "limit": 10}'
```

---

### 3. Campaign Detail

Get detail of a single campaign including list of muzaki (donors).

**Endpoint:** `POST /api/v1/kegiatan/detail`

**Request Body:**
```json
{
  "id": "84"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "sukses",
  "results": {
    "id": "84",
    "judul": "Zakat Fitrah",
    "tipe_zakat": "zakat",
    "kategori": "Lainnya",
    "url_gambar": "https://amil.cintazakat.id/uploads/campaign/Zakat_Fitrah1.jpg",
    "total_terkumpul": "0",
    "total_kebutuhan": "1000000000",
    "batas_waktu": "18250",
    "created_date": "2026-02-04 11:34:55",
    "start_date": "2026-02-04",
    "end_date": "9999-12-31",
    "abstract": "Zakat fitrah adalah kebiasaan baik...",
    "informasi": "Full description text here...",
    "sisa_hari": "Selamanya",
    "nama_lembaga": "BAZNAS RI (Pusat)",
    "kode_institusi": 3171100,
    "apikey": "",
    "list_muzaki": [
      {
        "nama_muzaki": "Ahmad Hidayat",
        "total_zakat": "50000",
        "tgl_donasi": "2026-02-10 08:30:15",
        "doa_muzaki": "Semoga Allah memberikan keberkahan..."
      }
    ]
  }
}
```

**cURL Example:**
```bash
curl -X POST https://be-dana.vercel.app/api/v1/kegiatan/detail \
  -H "Content-Type: application/json" \
  -d '{"id": "84"}'
```

---

### 4. List Categories

Get all available categories for filtering.

**Endpoint:** `POST /api/v1/listfilter/bycategory`

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "code": 200,
  "message": "Success",
  "results": [
    {
      "category": "Lainnya"
    },
    {
      "category": "Pendidikan"
    },
    {
      "category": "Kesehatan"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST https://be-dana.vercel.app/api/v1/listfilter/bycategory \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 5. List Institutions

Get all available institutions for filtering.

**Endpoint:** `POST /api/v1/listfilter/byinstitusi`

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "code": 200,
  "message": "Success",
  "results": []
}
```

**Note:** Currently returns empty array as institution filter is not implemented in schema.

**cURL Example:**
```bash
curl -X POST https://be-dana.vercel.app/api/v1/listfilter/byinstitusi \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Response Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Campaign ID |
| `judul` | string | Campaign title |
| `tipe_zakat` | string | Type: "zakat" or "infak" |
| `kategori` | string | Category name |
| `url_gambar` | string | Campaign image URL |
| `total_terkumpul` | string | Total amount collected |
| `total_kebutuhan` | string | Target amount needed |
| `batas_waktu` | string | Days remaining (or "18250" for unlimited) |
| `created_date` | string | Creation date (YYYY-MM-DD HH:MM:SS) |
| `start_date` | string | Campaign start date (YYYY-MM-DD) |
| `end_date` | string | Campaign end date (YYYY-MM-DD) |
| `abstract` | string | Short description (max 200 chars) |
| `informasi` | string | Full description (detail endpoint only) |
| `sisa_hari` | string | Days remaining display ("Selamanya" for unlimited) |
| `nama_lembaga` | string | Institution name |
| `kode_institusi` | integer | Institution code |
| `apikey` | string | Always empty for security |
| `list_muzaki` | array | List of donors (detail endpoint only) |

---

## Error Responses

### 400 Bad Request
```json
{
  "status_code": 400,
  "status": "error",
  "message": "Bad Request"
}
```

### 404 Not Found
```json
{
  "code": 404,
  "message": "Campaign tidak ditemukan",
  "results": null
}
```

### 500 Internal Server Error
```json
{
  "code": 500,
  "message": "Internal server error: [error detail]",
  "results": []
}
```

---

## Database Schema

Campaign data is stored in `adm_campaign` table with the following key fields:

- `id` (integer) - Primary key
- `kode_institusi` (integer) - Institution code
- `tipe` (enum) - "zakat" or "infak"
- `kategori` (varchar) - Category name
- `name` (varchar) - Campaign name
- `slug` (varchar) - URL-friendly slug
- `target_donasi` (bigint) - Target amount
- `start_date` (date) - Start date
- `end_date` (date) - End date
- `url_fotoutama` (varchar) - Main image URL
- `informasi` (text) - Full description
- `status` (enum) - Campaign status ("publish", "draft", etc.)
- `is_active` (enum) - "Y" or "N"
- `is_delete` (enum) - "Y" or "N"
- `prioritas` (enum) - "Y" or "N" (for featured campaigns)

---

## Notes

1. **All POST requests** require `Content-Type: application/json` header
2. **sisa_hari** displays "Selamanya" (Forever) for campaigns with `end_date` > 10000 days or `9999-12-31`
3. **total_terkumpul** is calculated from `adm_campaign_donasi` table where `status = 'berhasil'`
4. **list_muzaki** only appears in detail endpoint
5. **Pagination** is supported via `limit` and `offset` parameters
6. **Sorting** options:
   - `terbaru` - Latest first (default, prioritizes featured campaigns)
   - `terlama` - Oldest first
   - `terkumpul` - By amount collected (ascending)

---

## Sample Data

The database currently contains **10 sample campaigns**:

- 3 Zakat campaigns (Zakat Fitrah, Zakat Penghasilan, Zakat Maal)
- 7 Infak campaigns (various social programs)

All campaigns are set with:
- `status = "publish"`
- `is_active = "Y"`
- `is_delete = "N"`

---

## Testing

### JavaScript/Fetch Example
```javascript
fetch('https://be-dana.vercel.app/api/v1/kegiatan/index', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    limit: 10,
    offset: 0,
    tipe: 'zakat'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### Python Example
```python
import requests

url = 'https://be-dana.vercel.app/api/v1/kegiatan/index'
headers = {'Content-Type': 'application/json'}
data = {
    'limit': 10,
    'offset': 0,
    'tipe': 'zakat'
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## Migration from cintazakat.id

This API replaces the external cintazakat.id API with the same response format. Key changes:

1. **Endpoint prefix**: Changed from `/kegiatan/` to `/api/v1/kegiatan/`
2. **Authentication**: No authentication required (simplified)
3. **Database**: Data stored in local PostgreSQL (Neon) instead of external API
4. **Performance**: Faster response time (no external API calls)

---

## Support

For issues or questions, please contact the development team or create an issue in the repository.

**Repository:** https://github.com/saefulmuminin/be-dana

**Deployment:** Vercel (auto-deploy from `main` branch)
