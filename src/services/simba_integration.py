"""
SIMBA Integration Helper untuk DANA Payment Service
Menangani registrasi muzaki dan penyimpanan transaksi ke SIMBA (Baznas)
"""

import requests
import json
from datetime import datetime
from src.config.config import Config


class SimbaIntegration:
    """
    Helper class untuk integrasi dengan SIMBA API (Baznas)
    """

    def __init__(self):
        self.base_url = Config.SIMBA_BASE_URL
        self.org = Config.SIMBA_ORG
        self.key = Config.SIMBA_KEY
        self.divisi = Config.SIMBA_DIVISI
        self.amil_email = Config.SIMBA_AMIL_EMAIL

        # Cache untuk config SIMBA
        self._simba_config_cache = None

        # Database connection untuk logging
        from src.utils.database import Database
        self.db = Database()

    def _logApiCall(self, endpoint, method, request_data, response_status, response_body, error=None):
        """Log SIMBA API call ke database"""
        try:
            conn = self.db.getConnection()
            with conn.cursor() as cursor:
                # Mask sensitive data
                safe_request = request_data.copy() if request_data else {}
                if 'key' in safe_request:
                    safe_request['key'] = '***MASKED***'
                
                sql = """
                    INSERT INTO log_api
                    (name, aplikasi, url_api, parameter, response, created_date, created_by, is_active, is_delete)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Y', 'N')
                """
                cursor.execute(sql, (
                    f"SIMBA_{method}",
                    'SIMBA_BAZNAS',
                    endpoint,
                    json.dumps(safe_request) if safe_request else None,
                    json.dumps(response_body) if response_body else str(error),
                    datetime.now(),
                    'system'
                ))
                conn.commit()
        except Exception as e:
            print(f"[SIMBA] Failed to log API call: {str(e)}")

    def getSimbaConfig(self):
        """
        Fetch SIMBA payment gateway configuration
        Returns account mappings untuk berbagai jenis zakat
        """
        if self._simba_config_cache:
            return self._simba_config_cache

        try:
            url = f"{self.base_url}/api/ajax_payment_gateway"
            payload = {
                'org': self.org,
                'key': self.key
            }

            print(f"[SIMBA] Fetching config from {url}")

            response = requests.post(
                url,
                data=payload,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json'
                },
                timeout=10
            )

            if response.status_code == 200:
                config = response.json()
                print(f"[SIMBA] Config fetched successfully")
                self._simba_config_cache = config
                return config
            else:
                print(f"[SIMBA] Config fetch failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"[SIMBA] Error fetching config: {str(e)}")
            return None

    def getAccountMapping(self, tipe_zakat):
        """
        Map tipe zakat ke akun SIMBA
        Returns: {'akun': '...', 'kadar': '...'}
        """
        config = self.getSimbaConfig()
        
        print(f"[SIMBA] Getting account mapping for: {tipe_zakat}")
        print(f"[SIMBA] Config available: {config is not None}")
        
        if not config:
            print(f"[SIMBA] Using fallback account mapping for {tipe_zakat}")
            # Fallback ke environment variables
            return self._getFallbackAccountMapping(tipe_zakat)

        # Debug: print config keys
        print(f"[SIMBA] Config keys: {list(config.keys()) if config else 'None'}")

        # Clean account string (remove dots, limit to 8 digits for SIMBA)
        def cleanAccount(acc, length=8):
            if not acc:
                return ''
            cleaned = str(acc).replace('.', '')[:length]
            print(f"[SIMBA] Cleaned account: {acc} → {cleaned}")
            return cleaned

        # Mapping berdasarkan tipe zakat
        tipe_lower = tipe_zakat.lower().strip()

        account_info = None
        if tipe_lower in ['zakat penghasilan', 'zakatpenghasilan', 'zakat']:
            akun = cleanAccount(config.get('zakatpenghasilanakun', ''))
            account_info = {
                'akun': akun if akun else Config.SIMBA_ACCOUNT_ZAKAT_PENGHASILAN,
                'kadar': '2.5'
            }
        elif tipe_lower in ['zakat fitrah', 'zakatfitrah']:
            akun = cleanAccount(config.get('zakatfitrahakun', ''))
            account_info = {
                'akun': akun if akun else Config.SIMBA_ACCOUNT_ZAKAT_FITRAH,
                'kadar': '0'
            }
        elif tipe_lower == 'fidyah':
            akun = cleanAccount(config.get('fidyahakun', ''))
            account_info = {
                'akun': akun if akun else Config.SIMBA_ACCOUNT_FIDYAH,
                'kadar': '0'
            }
        else:  # Default: infak/sedekah
            akun = cleanAccount(config.get('infak_akun', ''))
            account_info = {
                'akun': akun if akun else Config.SIMBA_ACCOUNT_INFAK,
                'kadar': '0'
            }
        
        print(f"[SIMBA] Account mapping result: {account_info}")
        return account_info

    def _getFallbackAccountMapping(self, tipe_zakat):
        """Fallback mapping dari environment variables"""
        tipe_lower = tipe_zakat.lower().strip()

        if tipe_lower in ['zakat penghasilan', 'zakatpenghasilan']:
            return {
                'akun': Config.SIMBA_ACCOUNT_ZAKAT_PENGHASILAN,
                'kadar': '2.5'
            }
        elif tipe_lower in ['zakat fitrah', 'zakatfitrah']:
            return {
                'akun': Config.SIMBA_ACCOUNT_ZAKAT_FITRAH,
                'kadar': '0'
            }
        elif tipe_lower == 'fidyah':
            return {
                'akun': Config.SIMBA_ACCOUNT_FIDYAH,
                'kadar': '0'
            }
        else:
            return {
                'akun': Config.SIMBA_ACCOUNT_INFAK,
                'kadar': '0'
            }

    def registerMuzaki(self, nama, email, handphone, tipe='perorangan'):
        """
        Register muzaki ke SIMBA dan dapatkan NPWZ
        
        Args:
            nama: Nama lengkap muzaki
            email: Email muzaki
            handphone: Nomor HP muzaki
            tipe: 'perorangan' atau 'lembaga'
        
        Returns:
            {'success': True, 'npwz': '12345'} atau {'success': False, 'error': '...'}
        """
        try:
            url = f"{self.base_url}/api/ajax_muzaki_register"

            # Format tanggal untuk SIMBA
            tanggal = datetime.now().strftime('%d/%m/%Y')

            payload = {
                'org': self.org,
                'key': self.key,
                'nama': nama or 'Tidak Diketahui',
                'email': email or '',
                'handphone': handphone or '',
                'tipe': tipe,
                'action': 'register',
                'tanggal': tanggal,
                'verifikasi': 'handphone' if handphone else 'email',
                'amil': self.amil_email  # Required field: Amil penanggungjawab
            }

            print(f"[SIMBA] Registering muzaki: {nama} ({email or handphone})")

            response = requests.post(
                url,
                data=payload,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json'
                },
                timeout=15
            )

            response_text = response.text
            response_status = response.status_code

            # Check for Cloudflare protection
            if 'Just a moment' in response_text or 'cf-chl-bypass' in response_text:
                print(f"[SIMBA] Cloudflare protection detected")
                self._logApiCall(url, 'REGISTER_MUZAKI', payload, response_status, {'error': 'Cloudflare Protection'})
                return {'success': False, 'error': 'Cloudflare Protection'}

            # Parse JSON response
            try:
                result = json.loads(response_text)
            except:
                print(f"[SIMBA] Invalid JSON response: {response_text[:200]}")
                self._logApiCall(url, 'REGISTER_MUZAKI', payload, response_status, {'error': 'Invalid JSON', 'raw': response_text[:200]})
                return {'success': False, 'error': 'Invalid JSON response'}

            # Log API call
            self._logApiCall(url, 'REGISTER_MUZAKI', payload, response_status, result)

            # Check status
            if result.get('status_code') in ['00', '000'] or result.get('status') == 'success':
                npwz = result.get('npwz') or result.get('data', {}).get('npwz') or '0'
                print(f"[SIMBA] Muzaki registered successfully. NPWZ: {npwz}")
                return {'success': True, 'npwz': npwz, 'response': result}
            else:
                error_msg = result.get('error') or result.get('message') or 'Unknown error'
                print(f"[SIMBA] Registration failed: {error_msg}")
                return {'success': False, 'error': error_msg, 'response': result}

        except requests.Timeout:
            print(f"[SIMBA] Registration timeout")
            self._logApiCall(url, 'REGISTER_MUZAKI', payload, 0, None, error='Request timeout')
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            print(f"[SIMBA] Registration error: {str(e)}")
            self._logApiCall(url, 'REGISTER_MUZAKI', payload, 0, None, error=str(e))
            return {'success': False, 'error': str(e)}

    def saveTransaction(self, npwz, amount, tanggal, tipe_zakat, order_id, program=None, via=None,
                       campaign_kategori=None, campaign_tipe=None, campaign_coa=None, campaign_name=None, campaign_kegiatan_code=None):
        """
        Simpan transaksi ke SIMBA

        Args:
            npwz: NPWZ muzaki
            amount: Jumlah donasi
            tanggal: Tanggal transaksi (format: dd/mm/yyyy)
            tipe_zakat: Jenis zakat (untuk mapping akun - legacy support)
            order_id: Order ID untuk keterangan
            program: Program code (optional, akan di-generate dari campaign_kategori)
            via: Via code (optional, dari Config.SIMBA_VIA)
            campaign_kategori: Kategori dari campaign (untuk mapping akun & program)
            campaign_tipe: Tipe dari campaign ('zakat' atau 'infak')
            campaign_coa: COA dari campaign (coa_zakat atau coa_infak)
            campaign_name: Nama campaign (fallback jika kategori = 'Lainnya')
            campaign_kegiatan_code: Kode kegiatan dari ref_dana_sosial.code (DANA: 113019977)

        Returns:
            {'success': True, 'no_transaksi': '...'} atau {'success': False, 'error': '...'}
        """
        payload = None
        url = f"{self.base_url}/api/ajax_transaksi_simpan"
        try:

            # Determine account_info and program based on campaign data (NEW)
            if campaign_kategori:
                print(f"[SIMBA] Using campaign-based mapping: name={campaign_name}, kategori={campaign_kategori}, tipe={campaign_tipe}, coa={campaign_coa}, kegiatan_code={campaign_kegiatan_code}")

                # Get account info from campaign kategori (or name as fallback)
                account_info = self.getKodeAkunByKategori(
                    kategori=campaign_kategori,
                    tipe=campaign_tipe or 'infak',
                    coa_from_campaign=campaign_coa,
                    campaign_name=campaign_name
                )

                # Program selalu di-generate dari kategori
                if not program:
                    program = self.getKodeProgramByKategori(
                        kategori=campaign_kategori,
                        tipe=campaign_tipe or 'infak',
                        campaign_name=campaign_name
                    )

                print(f"[SIMBA] Campaign mapping result - Account: {account_info['akun']}, Program: {program}")
            else:
                # Fallback to legacy mapping (OLD)
                print(f"[SIMBA] Using legacy mapping for tipe_zakat: {tipe_zakat}")
                account_info = self._getFallbackAccountMapping(tipe_zakat)

                if not program:
                    program = Config.SIMBA_PROGRAM or '113010000'  # Default program

            if not account_info or not account_info.get('akun'):
                print(f"[SIMBA] No account mapping found")
                return {'success': False, 'error': 'No account mapping'}

            # Use SIMBA_VIA config (kas/debet account), fallback to account if not set
            if not via:
                via = Config.SIMBA_VIA or account_info['akun']

            # Kegiatan code hardcoded
            kegiatan = '113019977'
            print(f"[SIMBA] ✓ Kegiatan hardcoded: {kegiatan}")

            # Validate and clean field lengths to match SIMBA requirements
            program = self._cleanProgramString(program, 9)  # Must be 9 digits
            via = self._cleanAccountString(via, 8)  # Must be 8 digits
            account_info['akun'] = self._cleanAccountString(account_info['akun'], 8)  # Must be 8 digits

            print(f"[SIMBA] Final mapping - Account: {account_info['akun']}, Program: {program}, Via: {via}, Kegiatan: {kegiatan}")

            # Final validation
            if len(program) != 9:
                print(f"[SIMBA] ⚠️  Program code invalid: '{program}' (expected 9 digits, got {len(program)})")
                return {'success': False, 'error': f'Program code must be 9 digits, got {len(program)}'}
            if len(via) != 8:
                print(f"[SIMBA] ⚠️  Via code invalid: '{via}' (expected 8 digits, got {len(via)})")
                return {'success': False, 'error': f'Via code must be 8 digits, got {len(via)}'}
            if len(account_info['akun']) != 8:
                print(f"[SIMBA] ⚠️  Account code invalid: '{account_info['akun']}' (expected 8 digits, got {len(account_info['akun'])})")
                return {'success': False, 'error': f'Account code must be 8 digits, got {len(account_info["akun"])}'}

            keterangan = f"payment{order_id}"

            payload = {
                'key': self.key,
                'org': self.org,
                'subjek': npwz or '0',
                'tanggal': tanggal,
                'divisi': self.divisi,
                'program': program,
                'via': via,
                'akun': account_info['akun'],
                'jumlah': str(amount),
                'kadar': account_info['kadar'],
                'keterangan': keterangan,
                'amil': self.amil_email,
                'notif': 'false'  # Required field to prevent server error
            }

            # Tambahkan kegiatan jika tersedia
            if kegiatan:
                payload['kegiatan'] = kegiatan

            print(f"[SIMBA] Saving transaction: {order_id}, Amount: {amount}, NPWZ: {npwz}")

            response = requests.post(
                url,
                data=payload,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'PostmanRuntime/7.11.0',
                    'Accept': '*/*',
                    'Cache-Control': 'no-cache'
                },
                timeout=15
            )

            response_text = response.text
            response_status = response.status_code

            # Check for Cloudflare protection
            if 'Just a moment' in response_text or 'cf-chl-bypass' in response_text:
                print(f"[SIMBA] Cloudflare protection detected")
                self._logApiCall(url, 'SAVE_TRANSACTION', payload, response_status, {'error': 'Cloudflare Protection'})
                return {'success': False, 'error': 'Cloudflare Protection'}

            # Parse JSON response
            try:
                result = json.loads(response_text)
            except:
                print(f"[SIMBA] Invalid JSON response: {response_text[:200]}")
                self._logApiCall(url, 'SAVE_TRANSACTION', payload, response_status, {'error': 'Invalid JSON', 'raw': response_text[:200]})
                return {'success': False, 'error': 'Invalid JSON response'}

            # Log API call
            self._logApiCall(url, 'SAVE_TRANSACTION', payload, response_status, result)

            # Check status
            if result.get('status_code') in ['00', '000']:
                no_transaksi = result.get('no_transaksi', '')
                print(f"[SIMBA] Transaction saved successfully. No: {no_transaksi}")
                return {'success': True, 'no_transaksi': no_transaksi, 'response': result}
            else:
                error_msg = result.get('error') or result.get('message') or 'Unknown error'
                print(f"[SIMBA] Transaction save failed: {error_msg}")
                return {'success': False, 'error': error_msg, 'response': result}

        except requests.Timeout:
            print(f"[SIMBA] Transaction save timeout")
            self._logApiCall(url, 'SAVE_TRANSACTION', payload, 0, None, error='Request timeout')
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            print(f"[SIMBA] Transaction save error: {str(e)}")
            self._logApiCall(url, 'SAVE_TRANSACTION', payload, 0, None, error=str(e))
            return {'success': False, 'error': str(e)}

    def _cleanAccountString(self, acc, length=8):
        """Clean account string: remove dots, limit to 8 digits for SIMBA"""
        if not acc:
            return ''
        return acc.replace('.', '')[:length]

    def _cleanProgramString(self, prog, length=9):
        """Clean program string: digits only, limit to 9 digits for SIMBA"""
        if not prog:
            return ''
        return ''.join(filter(str.isdigit, prog))[:length]

    def getKodeProgramByKategori(self, kategori, tipe='infak', campaign_name=None):
        """
        Map kategori campaign ke kode program

        Kode Program (9 digits):
        - Maal & Infak Tidak Terikat: 110100000 (1.1.01.00.00)
        - Infaq Terikat, Fitrah, Fidyah: 120100000 (1.2.01.00.00)

        Args:
            kategori: Kategori dari campaign (e.g., 'Zakat Fitrah', 'Zakat Penghasilan', 'Fidyah')
            tipe: Tipe dari campaign ('zakat' atau 'infak')
            campaign_name: Nama campaign (fallback jika kategori = 'Lainnya')

        Returns:
            str: Kode program (9 digits exactly)
        """
        kategori_lower = kategori.lower().strip() if kategori else ''
        tipe_lower = tipe.lower().strip() if tipe else 'infak'
        name_lower = campaign_name.lower().strip() if campaign_name else ''

        print(f"[SIMBA] getKodeProgramByKategori - Kategori: '{kategori}', Name: '{campaign_name}', Tipe: '{tipe}'")

        # Mapping untuk kategori yang menggunakan program 1.2.01.00.00 (Infaq Terikat, Fitrah, Fidyah)
        program_terikat_keywords = [
            'fitrah',
            'zakat fitrah',
            'fidyah',
            'infak terikat',
            'infaq terikat',
            'infaq sedekah terikat',
            'infak sedekah terikat',
            # Program terikat spesifik (42010104-42010109)
            'dakwah',
            'kesehatan',
            'pendidikan',
            'beasiswa',
            'ekonomi',
            'usaha',
            'umkm',
            'kemanusiaan',
            'bencana',
            'darurat',
            'solidaritas',
            'palestina',
            'dunia islam',
        ]

        # Check jika kategori termasuk program terikat
        for keyword in program_terikat_keywords:
            if keyword in kategori_lower:
                print(f"[SIMBA] ✓ Matched kategori '{keyword}' → Program: 120100000 (Terikat/Fitrah/Fidyah)")
                return '120100000'  # 9 digits: 1.2.01.00.00

        # FALLBACK: Check campaign name jika kategori = "Lainnya"
        if kategori_lower == 'lainnya' or not kategori_lower:
            for keyword in program_terikat_keywords:
                if keyword in name_lower:
                    print(f"[SIMBA] ✓ Matched name '{keyword}' (fallback) → Program: 120100000 (Terikat/Fitrah/Fidyah)")
                    return '120100000'  # 9 digits: 1.2.01.00.00

        # Default: Maal & Infak Tidak Terikat (including Zakat Penghasilan/Maal)
        print(f"[SIMBA] ✓ Default match → Program: 110100000 (Maal/Infak Tidak Terikat)")
        return '110100000'  # 9 digits: 1.1.01.00.00

    def getKodeAkunByKategori(self, kategori, tipe='infak', coa_from_campaign=None, campaign_name=None):
        """
        Map kategori campaign ke kode akun

        Kode Akun (8 digits) berdasarkan Daftar Jenis Akun Level 5 BAZNAS:
        - Maal (Zakat Penghasilan): 41020201 (4.1.02.02.01)
        - Fitrah: 41020101 (4.1.02.01.01)
        - Fidyah: 42010601 (4.2.01.06.01)
        - Infaq Terikat - Program (umum): 42010101 (4.2.01.01.01)
        - Infaq Terikat - Dakwah: 42010104 (4.2.01.01.04)
        - Infaq Terikat - Kesehatan: 42010105 (4.2.01.01.05)
        - Infaq Terikat - Pendidikan: 42010106 (4.2.01.01.06)
        - Infaq Terikat - Ekonomi: 42010107 (4.2.01.01.07)
        - Infaq Terikat - Kemanusiaan & Bencana: 42010108 (4.2.01.01.08)
        - Infaq Terikat - Solidaritas Dunia Islam: 42010109 (4.2.01.01.09)
        - Infaq Sedekah Tidak Terikat: 42020101 (4.2.02.01.01)

        Args:
            kategori: Kategori dari campaign
            tipe: Tipe dari campaign ('zakat' atau 'infak')
            coa_from_campaign: COA yang sudah tersimpan di campaign (coa_zakat atau coa_infak)
            campaign_name: Nama campaign (fallback jika kategori = 'Lainnya')

        Returns:
            dict: {'akun': '...', 'kadar': '...'}
        """
        print(f"[SIMBA] getKodeAkunByKategori - Kategori: '{kategori}', Name: '{campaign_name}', Tipe: '{tipe}', COA: '{coa_from_campaign}'")

        # Prioritas 1: Gunakan COA dari campaign jika ada
        if coa_from_campaign:
            cleaned_coa = self._cleanAccountString(coa_from_campaign)
            if cleaned_coa:
                # Tentukan kadar berdasarkan tipe
                kadar = '2.5' if tipe.lower() == 'zakat' else '0'
                print(f"[SIMBA] ✓ Using COA from campaign: {coa_from_campaign} → {cleaned_coa}")
                return {'akun': cleaned_coa, 'kadar': kadar}

        # Prioritas 2: Map berdasarkan kategori
        kategori_lower = kategori.lower().strip() if kategori else ''
        tipe_lower = tipe.lower().strip() if tipe else 'infak'
        name_lower = campaign_name.lower().strip() if campaign_name else ''

        # Mapping berdasarkan kategori (URUTAN PENTING: specific keywords dulu!)

        # 1. Zakat Fitrah
        if 'fitrah' in kategori_lower:
            print(f"[SIMBA] ✓ Matched kategori 'fitrah' → Akun: 41020101 (Fitrah), Kadar: 0")
            return {'akun': '41020101', 'kadar': '0'}  # 4.1.02.01.01

        # 2. Fidyah
        elif 'fidyah' in kategori_lower:
            print(f"[SIMBA] ✓ Matched kategori 'fidyah' → Akun: 42010601 (Fidyah), Kadar: 0")
            return {'akun': '42010601', 'kadar': '0'}  # 4.2.01.06.01

        # 3. Program Terikat Spesifik (urutan penting: cek sebelum 'infak terikat' generik)
        elif 'dakwah' in kategori_lower:
            print(f"[SIMBA] ✓ Matched kategori 'dakwah' → Akun: 42010104 (Kas Program Dakwah), Kadar: 0")
            return {'akun': '42010104', 'kadar': '0'}  # 4.2.01.01.04

        elif any(kw in kategori_lower for kw in ['kesehatan', 'health']):
            print(f"[SIMBA] ✓ Matched kategori 'kesehatan' → Akun: 42010105 (Kas Program Kesehatan), Kadar: 0")
            return {'akun': '42010105', 'kadar': '0'}  # 4.2.01.01.05

        elif any(kw in kategori_lower for kw in ['pendidikan', 'beasiswa', 'education']):
            print(f"[SIMBA] ✓ Matched kategori 'pendidikan' → Akun: 42010106 (Kas Program Pendidikan), Kadar: 0")
            return {'akun': '42010106', 'kadar': '0'}  # 4.2.01.01.06

        elif any(kw in kategori_lower for kw in ['ekonomi', 'usaha', 'umkm']):
            print(f"[SIMBA] ✓ Matched kategori 'ekonomi' → Akun: 42010107 (Kas Program Ekonomi), Kadar: 0")
            return {'akun': '42010107', 'kadar': '0'}  # 4.2.01.01.07

        elif any(kw in kategori_lower for kw in ['kemanusiaan', 'bencana', 'darurat']):
            print(f"[SIMBA] ✓ Matched kategori 'kemanusiaan/bencana' → Akun: 42010108 (Kas Program Kemanusiaan dan Bencana), Kadar: 0")
            return {'akun': '42010108', 'kadar': '0'}  # 4.2.01.01.08

        elif any(kw in kategori_lower for kw in ['solidaritas', 'dunia islam', 'palestina']):
            print(f"[SIMBA] ✓ Matched kategori 'solidaritas' → Akun: 42010109 (Kas Program Solidaritas Dunia Islam), Kadar: 0")
            return {'akun': '42010109', 'kadar': '0'}  # 4.2.01.01.09

        # 4. Infaq/Infak Terikat (generik)
        elif 'infak terikat' in kategori_lower or 'infaq terikat' in kategori_lower or 'sedekah terikat' in kategori_lower:
            print(f"[SIMBA] ✓ Matched kategori 'terikat' → Akun: 42010101 (Infaq Terikat), Kadar: 0")
            return {'akun': '42010101', 'kadar': '0'}  # 4.2.01.01.01

        # 5. Infaq/Infak Tidak Terikat (explicit)
        elif 'infak tidak terikat' in kategori_lower or 'infaq tidak terikat' in kategori_lower or 'sedekah tidak terikat' in kategori_lower:
            print(f"[SIMBA] ✓ Matched kategori 'tidak terikat' → Akun: 42020101 (Infaq Tidak Terikat), Kadar: 0")
            return {'akun': '42020101', 'kadar': '0'}  # 4.2.02.01.01

        # FALLBACK: Check campaign name jika kategori = "Lainnya"
        elif kategori_lower == 'lainnya' or not kategori_lower:
            # Check fitrah in name
            if 'fitrah' in name_lower:
                print(f"[SIMBA] ✓ Matched name 'fitrah' (fallback) → Akun: 41020101 (Fitrah), Kadar: 0")
                return {'akun': '41020101', 'kadar': '0'}  # 4.1.02.01.01

            # Check fidyah in name
            elif 'fidyah' in name_lower:
                print(f"[SIMBA] ✓ Matched name 'fidyah' (fallback) → Akun: 42010601 (Fidyah), Kadar: 0")
                return {'akun': '42010601', 'kadar': '0'}  # 4.2.01.06.01

            # Check program spesifik in name
            elif 'dakwah' in name_lower:
                print(f"[SIMBA] ✓ Matched name 'dakwah' (fallback) → Akun: 42010104 (Kas Program Dakwah), Kadar: 0")
                return {'akun': '42010104', 'kadar': '0'}  # 4.2.01.01.04

            elif any(kw in name_lower for kw in ['kesehatan', 'health']):
                print(f"[SIMBA] ✓ Matched name 'kesehatan' (fallback) → Akun: 42010105 (Kas Program Kesehatan), Kadar: 0")
                return {'akun': '42010105', 'kadar': '0'}  # 4.2.01.01.05

            elif any(kw in name_lower for kw in ['pendidikan', 'beasiswa']):
                print(f"[SIMBA] ✓ Matched name 'pendidikan' (fallback) → Akun: 42010106 (Kas Program Pendidikan), Kadar: 0")
                return {'akun': '42010106', 'kadar': '0'}  # 4.2.01.01.06

            elif any(kw in name_lower for kw in ['ekonomi', 'usaha', 'umkm']):
                print(f"[SIMBA] ✓ Matched name 'ekonomi' (fallback) → Akun: 42010107 (Kas Program Ekonomi), Kadar: 0")
                return {'akun': '42010107', 'kadar': '0'}  # 4.2.01.01.07

            elif any(kw in name_lower for kw in ['kemanusiaan', 'bencana', 'darurat']):
                print(f"[SIMBA] ✓ Matched name 'kemanusiaan' (fallback) → Akun: 42010108 (Kas Program Kemanusiaan dan Bencana), Kadar: 0")
                return {'akun': '42010108', 'kadar': '0'}  # 4.2.01.01.08

            elif any(kw in name_lower for kw in ['solidaritas', 'palestina', 'dunia islam']):
                print(f"[SIMBA] ✓ Matched name 'solidaritas' (fallback) → Akun: 42010109 (Kas Program Solidaritas Dunia Islam), Kadar: 0")
                return {'akun': '42010109', 'kadar': '0'}  # 4.2.01.01.09

            # Check terikat (generik) in name
            elif 'terikat' in name_lower:
                print(f"[SIMBA] ✓ Matched name 'terikat' (fallback) → Akun: 42010101 (Infaq Terikat), Kadar: 0")
                return {'akun': '42010101', 'kadar': '0'}  # 4.2.01.01.01

            # If tipe = zakat but no specific match, use Maal
            elif tipe_lower == 'zakat':
                print(f"[SIMBA] ✓ Fallback Zakat (Maal/Penghasilan) → Akun: 41020201, Kadar: 2.5")
                return {'akun': '41020201', 'kadar': '2.5'}  # 4.1.02.02.01

            # Default infak
            else:
                print(f"[SIMBA] ✓ Fallback Infak (Tidak Terikat) → Akun: 42020101, Kadar: 0")
                return {'akun': '42020101', 'kadar': '0'}  # 4.2.02.01.01

        # 5. Zakat (Maal/Penghasilan) - fallback untuk semua zakat selain Fitrah
        elif tipe_lower == 'zakat':
            print(f"[SIMBA] ✓ Default Zakat (Maal/Penghasilan) → Akun: 41020201, Kadar: 2.5")
            return {'akun': '41020201', 'kadar': '2.5'}  # 4.1.02.02.01

        # 6. Default untuk infak = Infaq Tidak Terikat
        else:
            print(f"[SIMBA] ✓ Default Infak (Tidak Terikat) → Akun: 42020101, Kadar: 0")
            return {'akun': '42020101', 'kadar': '0'}  # 4.2.02.01.01
