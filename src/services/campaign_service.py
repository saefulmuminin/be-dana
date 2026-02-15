from src.models.campaign_model import CampaignModel
from datetime import datetime, timezone


class CampaignService:
    """
    Service untuk mengelola campaign/program zakat dan infak
    """
    
    def __init__(self):
        self.campaignModel = CampaignModel()

    def getCampaigns(self, data):
        """
        Ambil daftar campaign dengan filter dan pagination
        """
        try:
            limit = int(data.get('limit', 10))
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
            
            total_count = self.campaignModel.countAll(tipe=tipe)
            
            results = []
            for campaign in campaigns:
                results.append(self._format_campaign_list_item(campaign))
            
            return {
                'code': 200,
                'message': 'sukses',
                'count': total_count,
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
        """
        try:
            keyword = data.get('keyword', '')
            limit = int(data.get('limit', 10))
            offset = int(data.get('offset', 0))
            
            if not keyword:
                return self.getCampaigns(data)
            
            campaigns = self.campaignModel.search(keyword, limit, offset)
            
            total_count = len(campaigns) 
            
            results = []
            for campaign in campaigns:
                results.append(self._format_campaign_list_item(campaign))
            
            return {
                'code': 200,
                'message': 'sukses',
                'count': total_count,
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
                tgl_zakat_dt = muzaki.get('tgl_donasi')
                tgl_zakat_str = tgl_zakat_dt.strftime('%Y-%m-%d %H:%M:%S') if tgl_zakat_dt else ''
                
                # Calculate waktu_lalu
                waktu_lalu = ""
                if tgl_zakat_dt:
                    now = datetime.now()
                    if tgl_zakat_dt.tzinfo:
                         now = datetime.now(tgl_zakat_dt.tzinfo)
                    
                    diff = now - tgl_zakat_dt
                    days = diff.days
                    if days > 0:
                        waktu_lalu = f"{days} hari yang lalu"
                    else:
                        hours = diff.seconds // 3600
                        if hours > 0:
                            waktu_lalu = f"{hours} jam yang lalu"
                        else:
                            minutes = diff.seconds // 60
                            waktu_lalu = f"{minutes} menit yang lalu"

                list_muzaki.append({
                    'nama_muzaki': muzaki.get('nama_muzaki', 'Hamba Allah'),
                    'url_gambar_muzaki': "", 
                    'total_zakat': str(int(muzaki.get('total_zakat', 0))),
                    'tgl_zakat': tgl_zakat_str,
                    'doa_muzaki': muzaki.get('doa_muzaki', '') or "",
                    'waktu_lalu': waktu_lalu
                })
            
            total_terkumpul = int(campaign.get('total_terkumpul', 0))
            target_donasi = int(campaign.get('target_donasi', 0))
            operasional_terkumpul = int(campaign.get('operasional_terkumpul', 0))
            biayaoperasional = int(campaign.get('biayaoperasional', 0))
            
            sisa_hari_val = campaign.get('sisa_hari')
            sisa_hari_str = str(int(sisa_hari_val)) if sisa_hari_val is not None else "Selamanya"
            if sisa_hari_val and int(sisa_hari_val) > 3650:
                 sisa_hari_str = "Selamanya"

            kode_institusi = str(campaign.get('kode_institusi', '3171100'))
            nama_lembaga = "BAZNAS RI (Pusat)" 
            
            # Slug generation if missing
            slug = campaign.get('slug', '')
            if not slug and campaign.get('name'):
                 slug = campaign.get('name').replace(' ', '-')
            
            result = {
                'id': str(campaign.get('id')),
                'judul': campaign.get('name', ''),
                'url_gambar': campaign.get('url_fotoutama', ''),
                'total_terkumpul': str(total_terkumpul),
                'total_kebutuhan': str(target_donasi),
                'operasional_terkumpul': str(operasional_terkumpul),
                'operasional_kebutuhan': str(biayaoperasional),
                'tipe_zakat': campaign.get('tipe', ''),
                'batas_waktu': "18250", 
                'created_date': campaign.get('created_date').strftime('%Y-%m-%d %H:%M:%S') if campaign.get('created_date') else '',
                'sisa_hari': sisa_hari_str,
                'url_kegiatan': f"https://cintazakat.baznas.go.id/kegiatan/detail/{slug}-{campaign_id}",
                'informasi': campaign.get('informasi', ''),
                'tgl_kegiatan': campaign.get('start_date').strftime('%Y-%m-%d') if campaign.get('start_date') else '',
                'email': "halimatussadiah@baznas.go.id",
                'kode_institusi': kode_institusi,
                'nama_lembaga': nama_lembaga,
                'apikey': "UnpGVVpsSkJZV3NyTTJob1ZYQkdjMk5hYWxsbVNEZHJlVmRPV25CUFpUVkpWVWxGVXpFMmFtbFlZM0oxZUZCQldqSXdkMmxrVHpobmVqY3JUbTVPUlVGTk0wMVpVblZDV0RVNVMzSmpXRVp1ZFU5R2FYSTRkMVpGVkd0cU5XaGxObE4xZGtnd2JXdFhSMmM5",
                'url_gambar_lembaga': "https://amil.cintazakat.id/uploads/logobaznas/baznaspusat.jpg",
                'is_verified': 1,
                'is_organization': 1,
                'total_muzaki': campaign.get('jumlah_muzaki', 0),
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
        """
        try:
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

    def _format_campaign_list_item(self, campaign):
        total_terkumpul = int(campaign.get('total_terkumpul', 0))
        target_donasi = int(campaign.get('target_donasi', 0))
        
        sisa_hari_val = campaign.get('sisa_hari')
        sisa_hari_str = str(int(sisa_hari_val)) if sisa_hari_val is not None else "Selamanya"
        if sisa_hari_val and int(sisa_hari_val) > 3650: 
             sisa_hari_str = "Selamanya"

        informasi = campaign.get('informasi', '')
        # Remove html tags simple approach if needed, but per example raw text or html might be ok. 
        # Example shows text without tags in "abstract". 
        import re
        clean_text = re.sub('<[^<]+?>', '', informasi) if informasi else ""
        abstract = clean_text[:200]
        
        return {
            'id': str(campaign.get('id')),
            'judul': campaign.get('name', ''),
            'tipe_zakat': campaign.get('tipe', ''),
            'kategori': campaign.get('kategori', '') or 'Lainnya',
            'url_gambar': campaign.get('url_fotoutama', ''),
            'total_terkumpul': str(total_terkumpul),
            'total_kebutuhan': str(target_donasi),
            'batas_waktu': "18250",
            'created_date': campaign.get('created_date').strftime('%Y-%m-%d %H:%M:%S') if campaign.get('created_date') else '',
            'start_date': campaign.get('start_date').strftime('%Y-%m-%d') if campaign.get('start_date') else '9999-12-31',
            'end_date': campaign.get('end_date').strftime('%Y-%m-%d') if campaign.get('end_date') else '9999-12-31',
            'abstract': abstract,
            'sisa_hari': sisa_hari_str,
            'nama_lembaga': "BAZNAS RI (Pusat)",
            'kode_institusi': str(campaign.get('kode_institusi', '3171100')),
            'apikey': "UnpGVVpsSkJZV3NyTTJob1ZYQkdjMk5hYWxsbVNEZHJlVmRPV25CUFpUVkpWVWxGVXpFMmFtbFlZM0oxZUZCQldqSXdkMmxrVHpobmVqY3JUbTVPUlVGTk0wMVpVblZDV0RVNVMzSmpXRVp1ZFU5R2FYSTRkMVpGVkd0cU5XaGxObE4xZGtnd2JXdFhSMmM5"
        }
