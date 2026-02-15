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
            limit = int(data.get('limit', 20))
            offset = int(data.get('offset', 0))
            tipe = data.get('tipe')
            kategori = data.get('kategori')
            sort = data.get('sort', 'terbaru')
            
            campaigns = self.campaignModel.findAll(
                limit=limit,
                offset=offset,
                tipe=tipe,
                kategori=kategori,
                sort=sort
            )
            
            # Format response sesuai external API
            results = []
            for campaign in campaigns:
                total_terkumpul = int(campaign.get('total_terkumpul', 0))
                target_donasi = int(campaign.get('target_donasi', 0))
                operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
                biayaoperasional = int(campaign.get('biayaoperasional', 0))
                
                results.append({
                    'id': str(campaign.get('id')),
                    'judul': campaign.get('name', ''),  # name -> judul
                    'slug': campaign.get('slug', ''),
                    'deskripsi': campaign.get('informasi', '')[:200] if campaign.get('informasi') else '',  # Short description
                    'url_gambar': campaign.get('url_fotoutama', ''),
                    'nama_lembaga': '',  # Not in schema, leave empty
                    'kategori': campaign.get('kategori', ''),
                    'tipe': campaign.get('tipe', ''),
                    'total_terkumpul': str(total_terkumpul),
                    'total_kebutuhan': str(target_donasi),  # target_donasi -> total_kebutuhan
                    'operasional_terkumpul': str(operasional_terkumpul),
                    'operasional_kebutuhan': str(biayaoperasional),  # biayaoperasional -> operasional_kebutuhan
                    'sisa_hari': int(campaign.get('sisa_hari', 0)) if campaign.get('sisa_hari') else 0,
                    'created_date': campaign.get('created_date').isoformat() if campaign.get('created_date') else '',
                    'jumlah_muzaki': campaign.get('jumlah_muzaki', 0)
                })
            
            return {
                'code': 200,
                'message': 'Success',
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
            
            # Format response
            results = []
            for campaign in campaigns:
                total_terkumpul = int(campaign.get('total_terkumpul', 0))
                target_donasi = int(campaign.get('target_donasi', 0))
                operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
                biayaoperasional = int(campaign.get('biayaoperasional', 0))
                
                results.append({
                    'id': str(campaign.get('id')),
                    'judul': campaign.get('name', ''),
                    'slug': campaign.get('slug', ''),
                    'deskripsi': campaign.get('informasi', '')[:200] if campaign.get('informasi') else '',
                    'url_gambar': campaign.get('url_fotoutama', ''),
                    'nama_lembaga': '',
                    'kategori': campaign.get('kategori', ''),
                    'tipe': campaign.get('tipe', ''),
                    'total_terkumpul': str(total_terkumpul),
                    'total_kebutuhan': str(target_donasi),
                    'operasional_terkumpul': str(operasional_terkumpul),
                    'operasional_kebutuhan': str(biayaoperasional),
                    'sisa_hari': int(campaign.get('sisa_hari', 0)) if campaign.get('sisa_hari') else 0,
                    'created_date': campaign.get('created_date').isoformat() if campaign.get('created_date') else '',
                    'jumlah_muzaki': campaign.get('jumlah_muzaki', 0)
                })
            
            return {
                'code': 200,
                'message': 'Success',
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
            
            # Format muzaki list
            list_muzaki = []
            for muzaki in campaign.get('list_muzaki', []):
                list_muzaki.append({
                    'nama_muzaki': muzaki.get('nama_muzaki', 'Hamba Allah'),
                    'total_zakat': str(muzaki.get('total_zakat', 0)),
                    'tgl_donasi': muzaki.get('tgl_donasi').isoformat() if muzaki.get('tgl_donasi') else '',
                    'doa_muzaki': muzaki.get('doa_muzaki', '')
                })
            
            # Format campaign detail
            total_terkumpul = int(campaign.get('total_terkumpul', 0))
            target_donasi = int(campaign.get('target_donasi', 0))
            operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
            biayaoperasional = int(campaign.get('biayaoperasional', 0))
            
            result = {
                'id': str(campaign.get('id')),
                'judul': campaign.get('name', ''),
                'slug': campaign.get('slug', ''),
                'deskripsi': campaign.get('informasi', '')[:200] if campaign.get('informasi') else '',
                'informasi': campaign.get('informasi', ''),
                'url_gambar': campaign.get('url_fotoutama', ''),
                'nama_lembaga': '',
                'kategori': campaign.get('kategori', ''),
                'tipe': campaign.get('tipe', ''),
                'total_terkumpul': str(total_terkumpul),
                'total_kebutuhan': str(target_donasi),
                'operasional_terkumpul': str(operasional_terkumpul),
                'operasional_kebutuhan': str(biayaoperasional),
                'sisa_hari': int(campaign.get('sisa_hari', 0)) if campaign.get('sisa_hari') else 0,
                'created_date': campaign.get('created_date').isoformat() if campaign.get('created_date') else '',
                'jumlah_muzaki': campaign.get('jumlah_muzaki', 0),
                'list_muzaki': list_muzaki
            }
            
            return {
                'code': 200,
                'message': 'Success',
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
