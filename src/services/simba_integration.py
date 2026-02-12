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
        if not config:
            print(f"[SIMBA] Using fallback account mapping for {tipe_zakat}")
            # Fallback ke environment variables
            return self._getFallbackAccountMapping(tipe_zakat)

        # Clean account string (remove dots, limit length)
        def cleanAccount(acc, length=12):
            if not acc:
                return ''
            return acc.replace('.', '')[:length]

        # Mapping berdasarkan tipe zakat
        tipe_lower = tipe_zakat.lower().strip()

        if tipe_lower in ['zakat penghasilan', 'zakatpenghasilan']:
            return {
                'akun': cleanAccount(config.get('zakatpenghasilanakun', '')),
                'kadar': '2.5'
            }
        elif tipe_lower in ['zakat fitrah', 'zakatfitrah']:
            return {
                'akun': cleanAccount(config.get('zakatfitrahakun', '')),
                'kadar': '0'
            }
        elif tipe_lower == 'fidyah':
            return {
                'akun': cleanAccount(config.get('fidyahakun', '')),
                'kadar': '0'
            }
        else:  # Default: infak/sedekah
            return {
                'akun': cleanAccount(config.get('infak_akun', '')),
                'kadar': '0'
            }

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
                'verifikasi': 'handphone' if handphone else 'email'
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

            # Check for Cloudflare protection
            if 'Just a moment' in response_text or 'cf-chl-bypass' in response_text:
                print(f"[SIMBA] Cloudflare protection detected")
                return {'success': False, 'error': 'Cloudflare Protection'}

            # Parse JSON response
            try:
                result = json.loads(response_text)
            except:
                print(f"[SIMBA] Invalid JSON response: {response_text[:200]}")
                return {'success': False, 'error': 'Invalid JSON response'}

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
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            print(f"[SIMBA] Registration error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def saveTransaction(self, npwz, amount, tanggal, tipe_zakat, order_id, program=None, via=None):
        """
        Simpan transaksi ke SIMBA
        
        Args:
            npwz: NPWZ muzaki
            amount: Jumlah donasi
            tanggal: Tanggal transaksi (format: dd/mm/yyyy)
            tipe_zakat: Jenis zakat (untuk mapping akun)
            order_id: Order ID untuk keterangan
            program: Program code (optional, akan fetch dari config)
            via: Via code (optional, akan fetch dari config)
        
        Returns:
            {'success': True, 'no_transaksi': '...'} atau {'success': False, 'error': '...'}
        """
        try:
            url = f"{self.base_url}/api/ajax_transaksi_simpan"

            # Get account mapping
            account_info = self.getAccountMapping(tipe_zakat)
            if not account_info or not account_info.get('akun'):
                print(f"[SIMBA] No account mapping found for {tipe_zakat}")
                return {'success': False, 'error': 'No account mapping'}

            # Get config for program and via
            config = self.getSimbaConfig()
            if config:
                program = program or self._cleanProgramString(config.get('kmprogram', ''))
                via = via or self._cleanAccountString(config.get('via', ''))
            else:
                program = program or Config.SIMBA_PROGRAM
                via = via or Config.SIMBA_VIA

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
                'amil': self.amil_email
            }

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

            # Check for Cloudflare protection
            if 'Just a moment' in response_text or 'cf-chl-bypass' in response_text:
                print(f"[SIMBA] Cloudflare protection detected")
                return {'success': False, 'error': 'Cloudflare Protection'}

            # Parse JSON response
            try:
                result = json.loads(response_text)
            except:
                print(f"[SIMBA] Invalid JSON response: {response_text[:200]}")
                return {'success': False, 'error': 'Invalid JSON response'}

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
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            print(f"[SIMBA] Transaction save error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _cleanAccountString(self, acc, length=12):
        """Clean account string: remove dots, limit length"""
        if not acc:
            return ''
        return acc.replace('.', '')[:length]

    def _cleanProgramString(self, prog, length=14):
        """Clean program string: digits only, limit length"""
        if not prog:
            return ''
        return ''.join(filter(str.isdigit, prog))[:length]
