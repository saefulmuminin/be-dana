import requests
from src.config.config import Config
from datetime import datetime
from src.utils.response import Response

class SimbaService:
    def registerMuzaki(self, donasiData, kantorData):
        payload = {
            'org': kantorData.get('kode_institusi'),
            'key': kantorData.get('apikey'),
            'nama': donasiData.get('nama_lengkap'),
            'alamat': '',
            'handphone': donasiData.get('no_hp') or donasiData.get('handphone') or '',
            'nik': '',
            'email': donasiData.get('email'),
            'tanggal': datetime.now().strftime('%d/%m/%Y'),
            'tipe': donasiData.get('tipe', 'perorangan'),
            'gender': '1',
            'verifikasi': 'email',
            'amil': kantorData.get('email') or ''
        }
        
        try:
            base = Config.SIMBA_URL.rstrip('/')
            endpoint = Config.API_MUZAKI_REGISTER.lstrip('/')
            url = f"{base}/{endpoint}"

            print(f"[SIMBA] registerMuzaki -> {url}")
            print(f"[SIMBA] payload: nama={payload['nama']}, email={payload['email']}, hp={payload['handphone']}, org={payload['org']}")

            resp = requests.post(url, data=payload, verify=False)
            data = resp.json()

            print(f"[SIMBA] registerMuzaki response: {data}")

            if data.get('status_code') == '000':
                return data.get('npwz')
            return None
        except Exception as e:
            print(f"[SIMBA] Register Error: {e}")
            return None

    def saveTransaction(self, donasiData, campaignData, kantorData, programData):
        via = campaignData.get('coa_zakat') if campaignData.get('tipe') == 'zakat' else campaignData.get('coa_infak')
        akun = via 
        
        note = f"CINTA ZAKAT - {campaignData.get('name')} ID:{donasiData.get('id')}"
        
        code_program = programData.get('code', '')
        if len(code_program) < 9: 
             code_program = '0' + code_program

        payload = {
            'org': kantorData.get('kode_institusi'),
            'key': kantorData.get('apikey'),
            'subjek': donasiData.get('npwz'),
            'tanggal': datetime.now().strftime('%d/%m/%Y'),
            'divisi': '22',
            'program': code_program,
            'via': via,
            'akun': akun,
            'kadar': '2.5' if campaignData.get('tipe') == 'zakat' else '0',
            'jumlah': donasiData.get('nominal'),
            'keterangan': note,
            'amil': kantorData.get('email'),
            'campaign': donasiData.get('campaign_id'),
            'lokasi': '',
            'notif': 'true'
        }

        try:
            url = f"{Config.SIMBA_URL}/ajax_transaksi_simpan"
            resp = requests.post(url, data=payload, verify=False)
            data = resp.json()
            
            if data.get('status_code') in ['000', '404']: 
                return {
                    'no_transaksi': data.get('no_transaksi'),
                    'bsz': data.get('bsz'),
                    'tanggal': data.get('tanggal'),
                    'waktu': data.get('waktu')
                }
            return None
        except Exception as e:
            print(f"SIMBA Save Transaction Error: {e}")
            return None
