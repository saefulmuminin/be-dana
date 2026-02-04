from flask import current_app
from datetime import datetime

class Muzaki:
    table_name = 'adm_muzaki'
    @staticmethod
    def update_by_params(params):
        print("DB START")
        print("Param")
        print(params)
        conn = current_app.db
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {Muzaki.table_name} WHERE id = %s", (params['id'],))
            print("Query:")
            print(f"SELECT id FROM {Muzaki.table_name} WHERE id = %s", (params['id'],))
            result = cursor.fetchone()

            print("Result:")
            print(result)
            if result:
                data = {
                    'nama': params.get('nama'),
                    'npwp': params.get('npwp'),
                    'nik': params.get('nik'),
                    'handphone': params.get('handphone'),
                    'alamat': params.get('alamat'),
                    'tgl_lahir': params.get('tgl_lahir'),
                    'jenis_kelamin': params.get('jenis_kelamin'),
                    'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                if params.get('foto'):
                    data['foto'] = params['foto']

                set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
                values = list(data.values())
                values.append(params['id']) 

                sql = f"UPDATE {Muzaki.table_name} SET {set_clause} WHERE id = %s"
                cursor.execute(sql, values)
                conn.commit()

                print("Success")
                return 'Berhasil Diubah'
            else:
                print("Failed")
                return 'Gagal Diubah'
