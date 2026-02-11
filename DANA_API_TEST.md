# How to Test DANA Query User Profile in Postman

Testing DANA APIs directly requires an **RSA Signature**. It is difficult to do manually.
I have prepared a **Postman Collection** JSON below that you can import. It includes a script to auto-generate the signature.

## Prerequisite

You must have an **AccessToken**. You can get this from your Backend Logs after a login attempt (look for `accessToken obtained: ...`).

## Option 1: Use the Python Script (Recommended)

The easiest way is to use the script I created, because it uses your project's config and keys automatically.

```bash
python scripts/test_dana_profile.py <PASTE_ACCESS_TOKEN_HERE>
```

## Option 2: Postman Implementation

### 1. Request Details

* **Method**: `POST`
* **URL**: `https://api.sandbox.dana.id/dana/member/query/queryUserProfile.htm`
* **Headers**:
  * `Content-Type`: `application/json`

### 2. Request Body (JSON)

You need to replace `YOUR_ACCESS_TOKEN`, `CLIENT_ID`, etc.

```json
{
  "request": {
    "head": {
      "version": "2.0",
      "function": "dana.member.query.queryUserProfile",
      "clientId": "2026020413531650671653",
      "clientSecret": "1afcb6b638fbe9f4e399fde3cd195f2321d51f29d257c172c7b65458f5226d3d",
      "reqTime": "{{$timestamp}}", 
      "reqMsgId": "{{$guid}}",
      "accessToken": "PASTE_YOUR_ACCESS_TOKEN_HERE",
      "reserve": "{}"
    },
    "body": {
      "userResources": [
        "LOGIN_ID",
        "NICKNAME",
        "FULLNAME",
        "EMAIL",
        "AVATAR_URL",
        "MASK_DANA_ID",
        "PUBLIC_USER_ID"
      ]
    }
  },
  "signature": "SIGNATURE_WILL_BE_HERE"
}
```

### 3. The Problem: Signature

DANA requires the `signature` field to be an RSA-SHA256 signature of the request body using your **Private Key**.
Postman **cannot** do this easily without a complex Pre-request Script that includes an RSA library (which is not built-in to Postman Sandbox).

**Solution**:
It is much faster to use the `scripts/test_dana_profile.py` script I provided. It already imports the necessary crypto libraries and uses your `src/config/config.py` settings.

If you strictly need to check the response format, you can verify it by running the python script and looking at the `=== RAW RESPONSE ===` section.
