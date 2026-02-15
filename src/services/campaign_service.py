from src.models.campaign_model import CampaignModel
from src.utils.db_connection import get_db_connection


class CampaignService:
    """
    Service untuk mengelola campaign/program zakat dan infak
    """
    
    def __init__(self):
        self.conn = get_db_connection()
        self.campaignModel = CampaignModel(self.conn)

    def getCampaigns(self, data):
        """
        Ambil daftar campaign dengan filter dan pagination
        
        Request body:
        {
            "limit": 20,
            "offset": 0,
            "tipe": "zakat",  // optional: zakat/infak
            "institusi": "BAZNAS",  // optional
            "kategori": "Pendidikan",  // optional
            "sort": "terbaru"  // optional: terbaru/terlama/terkumpul
        }
        """
        try:
            limit = int(data.get('limit', 20))
            offset = int(data.get('offset', 0))
            tipe = data.get('tipe')
            institusi = data.get('institusi')
            kategori = data.get('kategori')
            sort = data.get('sort', 'terbaru')
            
            campaigns = self.campaignModel.findAll(
                limit=limit,
                offset=offset,
                tipe=tipe,
                institusi=institusi,
                kategori=kategori,
                sort=sort
            )
            
            # Format response sesuai external API
            results = []
            for campaign in campaigns:
                total_terkumpul = int(campaign.get('total_terkumpul', 0))
                total_kebutuhan = int(campaign.get('total_kebutuhan', 0))
                operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
                operasional_kebutuhan = int(campaign.get('operasional_kebutuhan', 0))
                
                results.append({
                    'id': str(campaign.get('id')),
                    'judul': campaign.get('judul', ''),
                    'slug': campaign.get('slug', ''),
                    'deskripsi': campaign.get('deskripsi', ''),
                    'url_gambar': campaign.get('url_fotoutama', ''),
                    'nama_lembaga': campaign.get('nama_lembaga', ''),
                    'kategori': campaign.get('kategori', ''),
                    'tipe': campaign.get('tipe', ''),
                    'total_terkumpul': str(total_terkumpul),
                    'total_kebutuhan': str(total_kebutuhan),
                    'operasional_terkumpul': str(operasional_terkumpul),
                    'operasional_kebutuhan': str(operasional_kebutuhan),
                    'sisa_hari': campaign.get('sisa_hari', 0),
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
                total_kebutuhan = int(campaign.get('total_kebutuhan', 0))
                operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
                operasional_kebutuhan = int(campaign.get('operasional_kebutuhan', 0))
                
                results.append({
                    'id': str(campaign.get('id')),
                    'judul': campaign.get('judul', ''),
                    'slug': campaign.get('slug', ''),
                    'deskripsi': campaign.get('deskripsi', ''),
                    'url_gambar': campaign.get('url_fotoutama', ''),
                    'nama_lembaga': campaign.get('nama_lembaga', ''),
                    'kategori': campaign.get('kategori', ''),
                    'tipe': campaign.get('tipe', ''),
                    'total_terkumpul': str(total_terkumpul),
                    'total_kebutuhan': str(total_kebutuhan),
                    'operasional_terkumpul': str(operasional_terkumpul),
                    'operasional_kebutuhan': str(operasional_kebutuhan),
                    'sisa_hari': campaign.get('sisa_hari', 0),
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
            total_kebutuhan = int(campaign.get('total_kebutuhan', 0))
            operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
            operasional_kebutuhan = int(campaign.get('operasional_kebutuhan', 0))
            
            result = {
                'id': str(campaign.get('id')),
                'judul': campaign.get('judul', ''),
                'slug': campaign.get('slug', ''),
                'deskripsi': campaign.get('deskripsi', ''),
                'informasi': campaign.get('informasi', campaign.get('deskripsi', '')),
                'url_gambar': campaign.get('url_fotoutama', ''),
                'nama_lembaga': campaign.get('nama_lembaga', ''),
                'kategori': campaign.get('kategori', ''),
                'tipe': campaign.get('tipe', ''),
                'total_terkumpul': str(total_terkumpul),
                'total_kebutuhan': str(total_kebutuhan),
                'operasional_terkumpul': str(operasional_terkumpul),
                'operasional_kebutuhan': str(operasional_kebutuhan),
                'sisa_hari': campaign.get('sisa_hari', 0),
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
            return {
                'code': 500,
                'message': f'Internal server error: {str(e)}',
                'results': None
            }, 500

    def getInstitutions(self):
        """
        Ambil daftar institusi untuk filter
        """
        try:
            institutions = self.campaignModel.getInstitutions()
            
            results = [{'name': inst.get('name')} for inst in institutions]
            
            return {
                'code': 200,
                'message': 'Success',
                'results': results
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
