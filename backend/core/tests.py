import uuid
import concurrent.futures
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Merchant, Payout, LedgerEntry

class PayoutIntegrityTest(TransactionTestCase):
    """
    Tests for Idempotency and Concurrency.
    Uses TransactionTestCase to allow testing atomic transactions.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.merchant = Merchant.objects.create(name="Concurrency Test Merchant")
        # Seed with 100 INR (10,000 paise)
        LedgerEntry.objects.create(
            merchant=self.merchant,
            amount_paise=10000,
            entry_type='PAYMENT',
            description="Initial deposit"
        )

    def test_idempotency_enforcement(self):
        """
        Verify that multiple calls with the same key return the same response
        and do not create duplicate payouts.
        """
        key = str(uuid.uuid4())
        payload = {
            "merchant_id": self.merchant.id,
            "amount_paise": 5000,
            "bank_account_id": "BANK-123"
        }
        
        # First request
        resp1 = self.client.post('/api/v1/payouts', payload, HTTP_IDEMPOTENCY_KEY=key, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        
        # Second request with same key
        resp2 = self.client.post('/api/v1/payouts', payload, HTTP_IDEMPOTENCY_KEY=key, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp1.data['id'], resp2.data['id'])
        
        # Check DB state
        self.assertEqual(Payout.objects.filter(merchant=self.merchant).count(), 1)
        self.assertEqual(self.merchant.get_balance_paise(), 5000)

    def test_concurrency_protection(self):
        """
        Simulate two simultaneous payout requests that would exceed balance.
        Balance is 10,000. Both requests ask for 6,000.
        Exactly one must succeed.
        """
        url = '/api/v1/payouts'
        
        def make_request(amount, key):
            # Using a new client per thread to simulate different requests
            client = APIClient()
            return client.post(
                url, 
                {"merchant_id": self.merchant.id, "amount_paise": amount, "bank_account_id": "B-X"},
                HTTP_IDEMPOTENCY_KEY=key,
                format='json'
            )

        # Run 2 requests in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(make_request, 6000, str(uuid.uuid4())),
                executor.submit(make_request, 6000, str(uuid.uuid4()))
            ]
            results = [f.result() for f in futures]

        status_codes = [r.status_code for r in results]
        
        # In a perfectly concurrent environment with SELECT FOR UPDATE:
        # One should be 201, the other should be 400 (Insufficient Balance)
        self.assertIn(status.HTTP_201_CREATED, status_codes)
        self.assertIn(status.HTTP_400_BAD_REQUEST, status_codes)
        
        # Final balance should be 4000 (10000 - 6000)
        self.assertEqual(self.merchant.get_balance_paise(), 4000)
        self.assertEqual(Payout.objects.filter(merchant=self.merchant).count(), 1)
