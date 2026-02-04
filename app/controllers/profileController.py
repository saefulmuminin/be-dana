from flask import Blueprint, request, jsonify, current_app
import os, requests
from app.models.muzakiModel import Muzaki
from app.config import SIMBA_KEY, SIMBA_ORG, API_MUZAKI_REGISTER, API_MUZAKI_EDIT

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/update', methods=['POST'])
def profile_update():
    data = request.form
    id = data.get('id')
    nama = data.get('nama')
    nik = data.get('nik')
    npwp = data.get('npwp')
    handphone = data.get('handphone')
    alamat = data.get('alamat')
    tgl_lahir = data.get('tgl_lahir')
    jenis_kelamin = (data.get('jenis_kelamin') or '').lower()
    npwz = data.get('npwz')
    email = data.get('email')
    tipe = data.get('tipe')
    foto = data.get('up_foto', '')

    params = {
        'id': id,
        'nama': nama,
        'nik': nik,
        'npwp': npwp,
        'handphone': handphone,
        'alamat': alamat,
        'tgl_lahir': tgl_lahir,
        'jenis_kelamin': jenis_kelamin,
        'foto': foto
    }

    print("Data found!")
    print(params)
    result = None

    if not npwz:
        print("NPWZ not set.")
        postFields = {
            'key': SIMBA_KEY,
            'org': SIMBA_ORG,
            'tipe': tipe,
            'action': 'register',
            'tanggal': '23/10/2025',
            'nama': nama,
            'nik': nik,
            'email': email,
            'handphone': handphone,
            'alamat': alamat,
            'verifikasi': 'email',
            'amil': 'lusi.emawati@baznas.go.id'
        }

        response = requests.post(API_MUZAKI_REGISTER, data=postFields)
        json_data = response.json()

        if json_data.get('status_code') == '000':
            params['npwz'] = json_data['npwz']
            result = Muzaki.update_by_params(params)
    else:
        print("NPWZ set")

        dob = '0000-00-00'
        if tgl_lahir and len(tgl_lahir) == 10:
            arrDob = tgl_lahir.split('-')
            dob = f"{arrDob[2]}/{arrDob[1]}/{arrDob[0]}"

        postFields = {
            "org": SIMBA_ORG,
            "key": SIMBA_KEY,
            "npwz": npwz,
            "nama": nama,
            "nik": nik,
            "hp": handphone,
            "gender": jenis_kelamin,
            "tanggal_lahir": dob,
            "alamat": alamat,
            "email": email,
            "npwp": npwp,
            "pic_nama": "",
            "pic_hp": ""
        }

        response = requests.post(API_MUZAKI_EDIT, data=postFields)
        json_data = response.json()

        print("json_data:")
        print(json_data)
        if json_data.get('status_code') == '000':
            params['npwz'] = npwz
            result = Muzaki.update_by_params(params)

        print("DB END")
        print("Result:")
        print(result)
    if result == 'Berhasil Diubah':
        return jsonify({'code': 200, 'message': 'sukses', 'results': result}), 200
    else:
        return jsonify({'code': 404, 'message': f"No data were found: {json_data.get('status')}", 'results': result}), 404
