#!/bin/bash

BASE_URL="http://localhost:8899/api/v1"
echo "Starting Integration Tests on $BASE_URL"

# 1. Health Check
echo "Testing Health Check..."
curl -s "$BASE_URL/../" | grep "healthy" && echo "PASS" || echo "FAILED"

# 2. Auth - Seamless Login
echo "Testing Seamless Login..."
LOGIN_RES=$(curl -s -X POST "$BASE_URL/auth/seamless-login" -H "Content-Type: application/json" -d '{"authCode": "12345"}')
TOKEN=$(echo $LOGIN_RES | grep -o '"token": *"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Login FAILED"
    exit 1
fi
echo "Login PASS, Token: $TOKEN"

# 3. Content - Banner
echo "Testing Content - Banner..."
curl -s "$BASE_URL/content/banner" | grep "success" && echo "PASS" || echo "FAILED"

# 4. Content - Berita
echo "Testing Content - Berita..."
curl -s "$BASE_URL/content/berita?keyword=zakat" | grep "success" && echo "PASS" || echo "FAILED"

# 5. Content - Payment Channels
echo "Testing Payment Channels..."
curl -s "$BASE_URL/content/payment-channels" | grep "success" && echo "PASS" || echo "FAILED"

echo "Integration Tests Completed."
