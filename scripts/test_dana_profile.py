import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.dana_auth_service import DanaAuthService
from src.config.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_query_profile(access_token):
    print(f"\nTesting QueryUserProfile with Access Token: {access_token[:10]}...")
    print(f"Endpoint: {Config.DANA_BASE_URL}/dana/member/query/queryUserProfile.htm")
    print(f"Client ID: {Config.DANA_CLIENT_ID}")
    
    service = DanaAuthService()
    result = service._queryUserProfile(access_token)
    
    print("\n=== RESULT ===")
    if result.get('success'):
        print("SUCCESS!")
        print(f"User Login ID (Phone): {result.get('userLoginId')}")
        print(f"Name: {result.get('name')}")
        print(f"Email: {result.get('email')}")
        print(f"Public User ID: {result.get('publicUserId')}")
        print(f"Avatar: {result.get('avatar')}")
    else:
        print("FAILED!")
        print(f"Error: {result.get('error')}")
    
    if 'raw' in result:
        print("\n=== RAW RESPONSE ===")
        import json
        print(json.dumps(result['raw'], indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_dana_profile.py <ACCESS_TOKEN>")
        print("Note: You need a valid DANA Access Token obtained from 'applyToken'.")
        sys.exit(1)
    
    token = sys.argv[1]
    test_query_profile(token)
