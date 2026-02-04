# API Cinta Zakat

Service API untuk pengelolaan zakat dan donasi, terintegrasi dengan payment gateway DANA.

## Instalasi

### Persyaratan Server

- **Sistem Operasi**: Linux/Unix/MacOS
- **Container**: Docker engine 20.10+ & Docker Compose 1.29+
- **Bahasa Pemrograman**: Python 3.9 (dalam container)
- **Database**: MySQL 8.0 (dalam container)
- **Web Server**: Nginx (dalam container)
- **Libraries**: Lihat `requirements.txt` (Flask, PyMySQL, Gunicorn, dll)

### Instalasi & Menjalankan Service

1. Clone repository ini.
2. Pastikan Docker sudah berjalan.
3. Jalankan perintah berikut:

    ```bash
    docker-compose up -d --build
    ```

4. Service akan berjalan pada port `8899`.

### Struktur Folder

- `src/`: Source code aplikasi (Python Flask).
  - `config/`: Konfigurasi environment.
  - `controllers/`: (Merged into services/routes for Flask simplicity).
  - `models/`: Representasi data database.
  - `services/`: Business logic.
  - `routes/`: Definisi endpoint API.
  - `middlewares/`: Middleware auth dan error handling.
  - `utils/`: Helper functions.
- `database/`: Schema database (`schema.sql`).
- `nginx/`: Konfigurasi Nginx.
- `reffs/`: Dokumen referensi dan instruksi.

## Dokumentasi API

Spesifikasi endpoint dapat dilihat pada file [endpoints.md](reffs/endpoint.md).

## Update Versi

Untuk melakukan update versi:

1. Pull perubahan terbaru dari git.
2. Jalankan build ulang container:

    ```bash
    docker-compose up -d --build
    ```

## Release Notes

Catatan rilis dapat dilihat pada file [release.md](release.md).

## Testing

### Unit Testing

Unit testing memverifikasi logika model dan service.

```bash
# Pastikan dependencies terinstall (atau masuk ke container)
pip install -r requirements.txt
python3 -m unittest src/tests/test_units.py
```

### Integration Testing

Integration testing memverifikasi endpoint API secara langsung menggunakan `curl`.
Pastikan service sudah berjalan di port 8899.

```bash
chmod +x src/tests/integration.sh
./src/tests/integration.sh
```

## Deployment ke Google Cloud Platform (CI/CD)

Aplikasi ini mendukung deployment otomatis ke Google Cloud Run menggunakan Cloud Build.

### 1. Persiapan GCP & Bitbucket

1. **Enable APIs**: Aktifkan API berikut di Google Cloud Console:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API
   - Secret Manager API
2. **Artifact Registry**: Buat repository Docker di Artifact Registry dengan nama `cinta-zakat-repo` di region `asia-southeast2`.
3. **Bitbucket Connection**:
   - Buka Google Cloud Console > Cloud Build > Repositories.
   - Klik **Connect Repository**.
   - Pilih **Bitbucket Cloud**.
   - Ikuti langkah autentikasi dan pilih repository `cinta-zakat-api`.
   - Pastikan Anda menggunakan App Password dengan scope `Repository:Read` dan `Admin` (jika diminta untuk Webhook).

### 2. Konfigurasi Secret Manager

Simpan seluruh credential berikut di **Secret Manager** agar dapat dibaca otomatis oleh Cloud Run:

- Database: `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
- Simba: `SIMBA_KEY`, `SIMBA_ORG`, `SIMBA_URL`, `API_MUZAKI_REGISTER`, `API_MUZAKI_EDIT`
- Dana: `DANA_CLIENT_ID`, `DANA_CLIENT_SECRET`, `DANA_MERCHANT_ID`, `DANA_BASE_URL`, `DANA_WEBHOOK_PUBLIC_KEY`, `DANA_WEBHOOK_PUBLIC_KEY_PATH`, `DANA_PRIVATE_KEY`
- App: `APP_REDIRECT_URL`, `API_BASE_URL`, `SECRET_KEY`

### 3. Membuat Cloud Build Trigger

1. Buka Cloud Build > Triggers.
2. Klik **Create Trigger**.
3. Nama: `deploy-on-push`.
4. Event: `Push to a branch`.
5. Source: Pilih repository Bitbucket yang sudah dikoneksikan.
6. Configuration: `Cloud Build configuration file (yaml)`.
7. Location: `Repository` (otomatis mendeteksi `cloudbuild.yaml`).
8. Klik **Create**.

### 4. IAM Permissions

Pastikan Service Account Cloud Build memiliki role berikut:

- `Cloud Run Admin`
- `Service Account User`
- `Secret Manager Secret Accessor`

### 5. Verifikasi

Setiap push ke branch utama akan memicu deployment. Setelah selesai, cek status service:
`https://[URL-CLOUD-RUN]/api/v1/auth/health`

---
