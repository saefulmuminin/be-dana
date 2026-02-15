#!/usr/bin/env python3
"""
Script untuk testing complete donation flow
Dari create order sampai webhook dan verify di campaign
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.dana_payment_service import DanaPaymentService
from src.services.campaign_service import CampaignService
from src.models.donation_model import DonationModel


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}\n")


def test_create_order():
    """Test create order"""
    print_section("1. CREATE ORDER")

    service = DanaPaymentService()

    order_data = {
        "nominal": 25000,
        "email": "test.donation@example.com",
        "campaign_id": 67,  # Zakat Penghasilan
        "nama_lengkap": "Test Donor",
        "doa_muzaki": "Semoga berkah dan bermanfaat",
        "tipe_zakat": "zakat",
        "hamba_allah": "N",
        "metode_id": 1
    }

    print("Creating order with data:")
    print(json.dumps(order_data, indent=2))

    result = service.createOrder(order_data)

    if result[1] == 200:
        data = result[0]['data']
        order_id = data['orderId']
        print(f"\n✅ Order created successfully!")
        print(f"   Order ID: {order_id}")
        print(f"   Amount: Rp {data['amount']:,}")
        print(f"   Status: {data['status']}")
        return order_id
    else:
        print(f"\n❌ Failed to create order!")
        print(f"   Error: {result[0]}")
        return None


def verify_donation_in_db(order_id):
    """Verify donation was inserted to database"""
    print_section("2. VERIFY DATABASE INSERT")

    model = DonationModel()
    donation = model.findByOrderId(order_id)

    if donation:
        print("✅ Donation found in database!")
        print(f"   ID: {donation['id']}")
        print(f"   Order ID: {donation['order_id']}")
        print(f"   Campaign ID: {donation['campaign_id']}")
        print(f"   Nama: {donation['nama_lengkap']}")
        print(f"   Email: {donation['email']}")
        print(f"   Nominal: Rp {donation['nominal']:,}")
        print(f"   Status: {donation['status']}")
        print(f"   Created: {donation['created_date']}")
        return True
    else:
        print("❌ Donation NOT found in database!")
        return False


def simulate_webhook(order_id, status="SUCCESS"):
    """Simulate DANA webhook"""
    print_section("3. SIMULATE DANA WEBHOOK")

    service = DanaPaymentService()

    webhook_data = {
        "originalPartnerReferenceNo": order_id,
        "originalReferenceNo": f"DANA-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "merchantId": "216610000000045289850",
        "latestTransactionStatus": status,
        "amount": {
            "value": "25000.00",
            "currency": "IDR"
        },
        "transactionStatusDesc": "Payment successful" if status == "SUCCESS" else "Payment failed",
        "additionalInfo": {
            "paymentInfo": {
                "paidTime": datetime.now().isoformat(),
                "payOptionInfos": [
                    {
                        "payMethod": "BALANCE"
                    }
                ]
            }
        }
    }

    print("Sending webhook with data:")
    print(json.dumps(webhook_data, indent=2))

    result = service.webhook(webhook_data)

    if result[1] == 200:
        print(f"\n✅ Webhook processed successfully!")
        print(f"   Response Code: {result[0]['responseCode']}")
        print(f"   Response Message: {result[0]['responseMessage']}")
        return True
    else:
        print(f"\n❌ Webhook processing failed!")
        print(f"   Error: {result[0]}")
        return False


def verify_status_updated(order_id):
    """Verify donation status was updated"""
    print_section("4. VERIFY STATUS UPDATE")

    model = DonationModel()
    donation = model.findByOrderId(order_id)

    if donation:
        print("✅ Donation status updated!")
        print(f"   Status: {donation['status']}")
        print(f"   DANA Status: {donation.get('dana_status', 'N/A')}")
        print(f"   DANA Reference: {donation.get('dana_reference_no', 'N/A')}")
        print(f"   Paid At: {donation.get('dana_paid_at', 'N/A')}")

        if donation['status'] == 'berhasil':
            print(f"\n   ✅ Status is 'berhasil' - donation will appear in campaign!")
            return True
        else:
            print(f"\n   ⚠️  Status is '{donation['status']}' - donation will NOT appear in campaign yet")
            return False
    else:
        print("❌ Donation NOT found in database!")
        return False


def verify_in_campaign(campaign_id):
    """Verify donation appears in campaign"""
    print_section("5. VERIFY IN CAMPAIGN")

    service = CampaignService()

    # Get campaign detail
    result = service.getCampaignDetail({'id': str(campaign_id)})

    if result[1] == 200:
        data = result[0]['results']
        print(f"Campaign: {data['judul']}")
        print(f"Total Terkumpul: Rp {int(data['total_terkumpul']):,}")
        print(f"Total Kebutuhan: Rp {int(data['total_kebutuhan']):,}")

        muzaki_count = len(data['list_muzaki'])
        print(f"\nList Muzaki: {muzaki_count} donors")

        if muzaki_count > 0:
            print("\n✅ Muzaki list (latest 3):")
            for i, muzaki in enumerate(data['list_muzaki'][:3], 1):
                print(f"\n   {i}. {muzaki['nama_muzaki']}")
                print(f"      Rp {int(muzaki['total_zakat']):,}")
                print(f"      {muzaki['tgl_donasi']}")
                if muzaki['doa_muzaki']:
                    print(f"      Doa: {muzaki['doa_muzaki'][:50]}...")
            return True
        else:
            print("\n⚠️  No muzaki found yet. Check if status is 'berhasil'")
            return False
    else:
        print(f"❌ Failed to get campaign detail!")
        print(f"   Error: {result[0]}")
        return False


def main():
    """Run complete test"""
    print(f"\n{'#' * 60}")
    print(f"# DONATION FLOW TEST")
    print(f"# Testing complete flow from create order to campaign display")
    print(f"{'#' * 60}")

    # Step 1: Create order
    order_id = test_create_order()
    if not order_id:
        print("\n❌ Test failed at Step 1: Create Order")
        return

    # Step 2: Verify in database
    if not verify_donation_in_db(order_id):
        print("\n❌ Test failed at Step 2: Database Insert")
        return

    # Step 3: Simulate webhook
    if not simulate_webhook(order_id, status="SUCCESS"):
        print("\n❌ Test failed at Step 3: Webhook Processing")
        return

    # Step 4: Verify status update
    if not verify_status_updated(order_id):
        print("\n⚠️  Warning at Step 4: Status not updated to 'berhasil'")
        # Continue anyway to show current state

    # Step 5: Verify in campaign
    verify_in_campaign(campaign_id=67)

    # Final summary
    print_section("TEST SUMMARY")
    print("✅ All steps completed!")
    print(f"\nTest Order ID: {order_id}")
    print("\nTo manually verify:")
    print(f"  1. Check database:")
    print(f"     SELECT * FROM adm_campaign_donasi WHERE order_id = '{order_id}';")
    print(f"  2. Check campaign API:")
    print(f"     POST /api/v1/kegiatan/detail")
    print(f"     Body: {{'id': '67'}}")


if __name__ == "__main__":
    main()
