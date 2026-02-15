/**
 * EXAMPLE: Cara Update Mini-App untuk Menggunakan Internal API
 * 
 * File ini menunjukkan contoh perubahan yang perlu dilakukan
 * di file-file mini-app untuk menggunakan internal API
 */

// ============================================================================
// EXAMPLE 1: components/CampaignList/index.js
// ============================================================================

// SEBELUM (Hardcoded External API):
/*
Component({
  methods: {
    fetchInstitutions() {
      my.request({
        url: 'https://api.cintazakat.id/listfilter/byinstitusi',
        method: 'POST',
        // ...
      });
    },
    
    fetchData() {
      let apiUrl = 'https://api.cintazakat.id/kegiatan/index';
      if (type === 'zakat' || type === 'infak') {
        apiUrl = 'https://api.cintazakat.id/kegiatan/search';
      }
      // ...
    }
  }
});
*/

// SESUDAH (Menggunakan Config):
const CONFIG = require('../../utils/config.js');

Component({
  methods: {
    fetchInstitutions() {
      my.request({
        url: `${CONFIG.API_CAMPAIGN_BASE}${CONFIG.FILTER_BY_INSTITUTION}`,
        method: 'POST',
        // ...
      });
    },
    
    fetchCategories() {
      my.request({
        url: `${CONFIG.API_CAMPAIGN_BASE}${CONFIG.FILTER_BY_CATEGORY}`,
        method: 'POST',
        // ...
      });
    },
    
    fetchData() {
      const { type } = this.props;
      let endpoint = CONFIG.CAMPAIGN_LIST;
      
      if (type === 'zakat' || type === 'infak') {
        endpoint = CONFIG.CAMPAIGN_SEARCH;
      }
      
      my.request({
        url: `${CONFIG.API_CAMPAIGN_BASE}${endpoint}`,
        method: 'POST',
        // ...
      });
    }
  }
});


// ============================================================================
// EXAMPLE 2: pages/campaign-detail/index.js
// ============================================================================

// SEBELUM:
/*
const CONFIG = {
  API_BASE: 'https://api.cintazakat.id',
  CAMPAIGN_DETAIL: '/kegiatan/detail',
};

Page({
  fetchCampaignDetail(id) {
    my.request({
      url: `${CONFIG.API_BASE}${CONFIG.CAMPAIGN_DETAIL}`,
      // ...
    });
  }
});
*/

// SESUDAH:
const CONFIG = require('../../utils/config.js');

Page({
  fetchCampaignDetail(id) {
    my.request({
      url: `${CONFIG.API_CAMPAIGN_BASE}${CONFIG.CAMPAIGN_DETAIL}`,
      method: 'POST',
      data: { id: id },
      // ...
    });
  }
});


// ============================================================================
// EXAMPLE 3: pages/faq/index.js
// ============================================================================

// SEBELUM:
/*
Page({
  onLoad() {
    my.request({
      url: 'https://api.cintazakat.id/faq/index',
      // ...
    });
  }
});
*/

// SESUDAH:
const CONFIG = require('../../utils/config.js');

Page({
  onLoad() {
    my.request({
      url: `${CONFIG.API_CAMPAIGN_BASE}${CONFIG.FAQ}`,
      method: 'POST',
      // ...
    });
  }
});


// ============================================================================
// EXAMPLE 4: pages/hubungi/index.js (Send Message)
// ============================================================================

// SEBELUM:
/*
Page({
  onSubmit() {
    my.request({
      url: 'https://api.cintazakat.id/sendmessage',
      method: 'POST',
      data: {
        name: this.data.name,
        email: this.data.email,
        message: this.data.message
      }
      // ...
    });
  }
});
*/

// SESUDAH:
const CONFIG = require('../../utils/config.js');

Page({
  onSubmit() {
    my.request({
      url: `${CONFIG.API_CAMPAIGN_BASE}${CONFIG.SEND_MESSAGE}`,
      method: 'POST',
      data: {
        name: this.data.name,
        email: this.data.email,
        message: this.data.message
      }
      // ...
    });
  }
});


// ============================================================================
// SUMMARY: Files yang Perlu Diupdate
// ============================================================================

/*
DAFTAR FILE YANG PERLU DIUPDATE:

1. components/CampaignList/index.js
   - fetchInstitutions() → CONFIG.FILTER_BY_INSTITUTION
   - fetchCategories() → CONFIG.FILTER_BY_CATEGORY
   - fetchData() → CONFIG.CAMPAIGN_LIST atau CONFIG.CAMPAIGN_SEARCH

2. pages/campaign-detail/index.js
   - fetchCampaignDetail() → CONFIG.CAMPAIGN_DETAIL

3. pages/program/index.js
   - fetchInstitutions() → CONFIG.FILTER_BY_INSTITUTION
   - fetchCategories() → CONFIG.FILTER_BY_CATEGORY
   - fetchData() → CONFIG.CAMPAIGN_LIST atau CONFIG.CAMPAIGN_SEARCH

4. pages/faq/index.js
   - onLoad() → CONFIG.FAQ

5. pages/index/index.js
   - fetchContact() → CONFIG.CONTACT

6. pages/terms/index.js
   - onLoad() → CONFIG.SYARAT_KETENTUAN

7. pages/hubungi/index.js
   - onSubmit() → CONFIG.SEND_MESSAGE

8. components/tentang/index.js
   - fetchData() → CONFIG.TENTANG

9. components/HeroBanner/index.js
   - fetchBanners() → CONFIG.BANNER

10. components/Navbar/index.js
    - onSearch() → CONFIG.CAMPAIGN_SEARCH

LANGKAH-LANGKAH:
1. Tambahkan: const CONFIG = require('../../utils/config.js'); di awal file
2. Ganti semua hardcoded URL dengan: `${CONFIG.API_CAMPAIGN_BASE}${CONFIG.ENDPOINT_NAME}`
3. Test di development dengan: API_CAMPAIGN_BASE: 'http://localhost:5000/api/v1'
4. Deploy dengan: API_CAMPAIGN_BASE: 'https://be-dana.vercel.app/api/v1'
*/
