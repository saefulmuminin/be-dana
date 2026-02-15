from src.models.campaign_model import CampaignModel


class CampaignService:
    """
    Service untuk mengelola campaign/program zakat dan infak
    """
    
    def __init__(self):
        self.campaignModel = CampaignModel()

    def getCampaigns(self, data):
        """
        Ambil daftar campaign dengan filter dan pagination

        Request body:
        {
            "limit": 20,
            "offset": 0,
            "tipe": "zakat",  // optional: zakat/infak
            "kategori": "Pendidikan",  // optional
            "sort": "terbaru"  // optional: terbaru/terlama/terkumpul
        }
        """
        try:
            print(f"[CampaignService] getCampaigns called with data: {data}")

            limit = int(data.get('limit', 20))
            offset = int(data.get('offset', 0))
            tipe = data.get('tipe')
            kategori = data.get('kategori')
            sort = data.get('sort', 'terbaru')

            print(f"[CampaignService] Fetching campaigns: limit={limit}, offset={offset}, tipe={tipe}, kategori={kategori}, sort={sort}")

            campaigns = self.campaignModel.findAll(
                limit=limit,
                offset=offset,
                tipe=tipe,
                kategori=kategori,
                sort=sort
            )

            print(f"[CampaignService] Found {len(campaigns)} campaigns")

            # Format response sesuai cintazakat.id API
            results = []
            for campaign in campaigns:
                total_terkumpul = int(campaign.get('total_terkumpul', 0))
                target_donasi = int(campaign.get('target_donasi', 0))
                operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
                biayaoperasional = int(campaign.get('biayaoperasional', 0))

                # Format sisa_hari
                sisa_hari_value = campaign.get('sisa_hari')
                if sisa_hari_value is None or sisa_hari_value > 10000:
                    sisa_hari_display = "Selamanya"
                    batas_waktu = "18250"
                else:
                    sisa_hari_display = str(int(sisa_hari_value))
                    batas_waktu = str(int(sisa_hari_value))

                # Format dates
                created_date = campaign.get('created_date')
                start_date = campaign.get('start_date')
                end_date = campaign.get('end_date')

                results.append({
                    'id': str(campaign.get('id')),
                    'judul': campaign.get('name', ''),
                    'tipe_zakat': campaign.get('tipe', ''),
                    'kategori': campaign.get('kategori', ''),
                    'url_gambar': campaign.get('url_fotoutama', ''),
                    'total_terkumpul': str(total_terkumpul),
                    'total_kebutuhan': str(target_donasi),
                    'batas_waktu': batas_waktu,
                    'created_date': created_date.strftime('%Y-%m-%d %H:%M:%S') if created_date else '',
                    'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
                    'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
                    'abstract': (campaign.get('informasi', '') or '')[:200],
                    'sisa_hari': sisa_hari_display,
                    'nama_lembaga': 'BAZNAS RI (Pusat)',  # Default value
                    'kode_institusi': campaign.get('kode_institusi', ''),
                    'apikey': ''  # Empty for security
                })

            return {
                'code': 200,
                'message': 'sukses',
                'count': len(campaigns),
                'offset': offset,
                'limit': str(limit),
                'results': results
            }, 200
            
        except Exception as e:
            print(f"[CampaignService] Error getCampaigns: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'code': 500,
                'message': f'Internal server error: {str(e)}',
                'results': []
            }, 500

    def searchCampaigns(self, data):
        """
        Search campaign berdasarkan keyword
        
        Request body:
        {
            "keyword": "zakat",
            "limit": 20,
            "offset": 0
        }
        """
        try:
            keyword = data.get('keyword', '')
            limit = int(data.get('limit', 20))
            offset = int(data.get('offset', 0))
            
            if not keyword:
                return self.getCampaigns(data)
            
            campaigns = self.campaignModel.search(keyword, limit, offset)

            # Format response sesuai cintazakat.id API
            results = []
            for campaign in campaigns:
                total_terkumpul = int(campaign.get('total_terkumpul', 0))
                target_donasi = int(campaign.get('target_donasi', 0))

                # Format sisa_hari
                sisa_hari_value = campaign.get('sisa_hari')
                if sisa_hari_value is None or sisa_hari_value > 10000:
                    sisa_hari_display = "Selamanya"
                    batas_waktu = "18250"
                else:
                    sisa_hari_display = str(int(sisa_hari_value))
                    batas_waktu = str(int(sisa_hari_value))

                # Format dates
                created_date = campaign.get('created_date')
                start_date = campaign.get('start_date')
                end_date = campaign.get('end_date')

                results.append({
                    'id': str(campaign.get('id')),
                    'judul': campaign.get('name', ''),
                    'tipe_zakat': campaign.get('tipe', ''),
                    'kategori': campaign.get('kategori', ''),
                    'url_gambar': campaign.get('url_fotoutama', ''),
                    'total_terkumpul': str(total_terkumpul),
                    'total_kebutuhan': str(target_donasi),
                    'batas_waktu': batas_waktu,
                    'created_date': created_date.strftime('%Y-%m-%d %H:%M:%S') if created_date else '',
                    'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
                    'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
                    'abstract': (campaign.get('informasi', '') or '')[:200],
                    'sisa_hari': sisa_hari_display,
                    'nama_lembaga': 'BAZNAS RI (Pusat)',
                    'kode_institusi': campaign.get('kode_institusi', ''),
                    'apikey': ''
                })

            return {
                'code': 200,
                'message': 'sukses',
                'count': len(campaigns),
                'offset': offset,
                'limit': str(limit),
                'results': results
            }, 200
            
        except Exception as e:
            print(f"[CampaignService] Error searchCampaigns: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'code': 500,
                'message': f'Internal server error: {str(e)}',
                'results': []
            }, 500

    def getCampaignDetail(self, data):
        """
        Ambil detail campaign beserta list muzaki

        Request body:
        {
            "id": "1"
        }
        """
        try:
            from datetime import datetime, timezone

            campaign_id = data.get('id')

            if not campaign_id:
                return {
                    'code': 400,
                    'message': 'ID campaign wajib diisi',
                    'results': None
                }, 400

            campaign = self.campaignModel.findById(campaign_id)

            if not campaign:
                return {
                    'code': 404,
                    'message': 'Campaign tidak ditemukan',
                    'results': None
                }, 404

            # Helper function untuk waktu lalu
            def get_waktu_lalu(tgl_donasi):
                if not tgl_donasi:
                    return ""

                now = datetime.now()
                if tgl_donasi.tzinfo is None:
                    diff = now - tgl_donasi
                else:
                    diff = datetime.now(timezone.utc) - tgl_donasi

                days = diff.days
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60

                if days > 0:
                    return f"{days} hari yang lalu"
                elif hours > 0:
                    return f"{hours} jam yang lalu"
                elif minutes > 0:
                    return f"{minutes} menit yang lalu"
                else:
                    return "Baru saja"

            # Format muzaki list
            list_muzaki = []
            for muzaki in campaign.get('list_muzaki', []):
                tgl_donasi = muzaki.get('tgl_donasi')
                list_muzaki.append({
                    'nama_muzaki': muzaki.get('nama_muzaki', 'Hamba Allah'),
                    'url_gambar_muzaki': '',  # Empty untuk sekarang
                    'total_zakat': str(muzaki.get('total_zakat', 0)),
                    'tgl_zakat': tgl_donasi.strftime('%Y-%m-%d %H:%M:%S') if tgl_donasi else '',
                    'doa_muzaki': muzaki.get('doa_muzaki', ''),
                    'waktu_lalu': get_waktu_lalu(tgl_donasi)
                })

            # Format campaign detail
            total_terkumpul = int(campaign.get('total_terkumpul', 0))
            target_donasi = int(campaign.get('target_donasi', 0))
            operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
            biayaoperasional = int(campaign.get('biayaoperasional', 0))
            jumlah_muzaki = int(campaign.get('jumlah_muzaki', 0))

            # Format sisa_hari
            sisa_hari_value = campaign.get('sisa_hari')
            if sisa_hari_value is None or sisa_hari_value > 10000:
                sisa_hari_display = "Selamanya"
                batas_waktu = "18250"
            else:
                sisa_hari_display = str(int(sisa_hari_value))
                batas_waktu = str(int(sisa_hari_value))

            # Format dates
            created_date = campaign.get('created_date')
            start_date = campaign.get('start_date')

            # Generate URL kegiatan
            slug = campaign.get('slug', '')
            if not slug:
                # Generate slug dari name jika tidak ada
                name = campaign.get('name', '')
                slug = name.replace(' ', '-')
            url_kegiatan = f"https://cintazakat.baznas.go.id/kegiatan/detail/{slug}-{campaign_id}"

            result = {
                'id': str(campaign.get('id')),
                'judul': campaign.get('name', ''),
                'url_gambar': campaign.get('url_fotoutama', ''),
                'operasional_terkumpul': str(operasional_terkumpul),
                'operasional_kebutuhan': str(biayaoperasional),
                'tipe_zakat': campaign.get('tipe', ''),
                'batas_waktu': batas_waktu,
                'created_date': created_date.strftime('%Y-%m-%d %H:%M:%S') if created_date else '',
                'sisa_hari': sisa_hari_display,
                'url_kegiatan': url_kegiatan,
                'informasi': campaign.get('informasi', ''),
                'tgl_kegiatan': start_date.strftime('%Y-%m-%d') if start_date else '',
                'email': 'info@baznas.go.id',  # Default email
                'kode_institusi': str(campaign.get('kode_institusi', '')),
                'nama_lembaga': 'BAZNAS RI (Pusat)',
                'apikey': 'UnpGVVpsSkJZV3NyTTJob1ZYQkdjMk5hYWxsbVNIZHJlVmRPV25CUFpUVkpWVWxGVXpFMmFtbFlZM0oxZUZCQldqSXdkMmxrVHpobmVqY3JUbTVPUlVGTk0wMVpVblZDV0RVNVMzSmpXRVp1ZFU5R2FYSTRkMVpGVkd0cU5XaGxObE4xZGtnd2JXdFhSMmM5',  # Static API key
                'url_gambar_lembaga': 'https://amil.cintazakat.id/uploads/logobaznas/baznaspusat.jpg',
                'is_verified': 1,
                'is_organization': 1,
                'total_muzaki': jumlah_muzaki,
                'list_muzaki': list_muzaki
            }

            return {
                'code': 200,
                'message': 'sukses',
                'results': result
            }, 200

        except Exception as e:
            print(f"[CampaignService] Error getCampaignDetail: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'code': 500,
                'message': f'Internal server error: {str(e)}',
                'results': None
            }, 500

    def getInstitutions(self):
        """
        Ambil daftar institusi untuk filter
        Note: Schema tidak memiliki nama_lembaga, return empty untuk sekarang
        """
        try:
            # Karena schema tidak punya nama_lembaga, return empty array
            # Bisa diupdate nanti jika ada tabel ref_kantor atau sejenisnya
            return {
                'code': 200,
                'message': 'Success',
                'results': []
            }, 200
            
        except Exception as e:
            print(f"[CampaignService] Error getInstitutions: {str(e)}")
            return {
                'code': 500,
                'message': f'Internal server error: {str(e)}',
                'results': []
            }, 500

    def getCategories(self):
        """
        Ambil daftar kategori untuk filter
        """
        try:
            categories = self.campaignModel.getCategories()
            
            results = [{'category': cat.get('category')} for cat in categories]
            
            return {
                'code': 200,
                'message': 'Success',
                'results': results
            }, 200
            
        except Exception as e:
            print(f"[CampaignService] Error getCategories: {str(e)}")
            return {
                'code': 500,
                'message': f'Internal server error: {str(e)}',
                'results': []
            }, 500
