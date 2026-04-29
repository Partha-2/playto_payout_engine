from rest_framework import viewsets, status, response
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Merchant, Payout, LedgerEntry, IdempotencyRecord
from .serializers import MerchantSerializer, PayoutSerializer, LedgerEntrySerializer
from .tasks import process_payout_task
import uuid

class MerchantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        merchant = get_object_or_404(Merchant, pk=pk)
        ledger = LedgerEntry.objects.filter(merchant=merchant).order_by('-created_at')
        serializer = LedgerEntrySerializer(ledger, many=True)
        return response.Response(serializer.data)

class PayoutViewSet(viewsets.ViewSet):
    def create(self, request):
        idempotency_key = request.headers.get('Idempotency-Key')
        if not idempotency_key:
            return response.Response({"error": "Idempotency-Key header is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uuid.UUID(idempotency_key)
        except ValueError:
            return response.Response({"error": "Invalid Idempotency-Key format"}, status=status.HTTP_400_BAD_REQUEST)

        # Mocking merchant lookup - in a real app, this would be from request.user
        merchant_id = request.data.get('merchant_id')
        if not merchant_id:
            return response.Response({"error": "merchant_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        merchant = get_object_or_404(Merchant, pk=merchant_id)

        # 1. Idempotency Check
        existing_record = IdempotencyRecord.objects.filter(merchant=merchant, idempotency_key=idempotency_key).first()
        if existing_record:
            return response.Response(existing_record.response_body, status=existing_record.response_status)

        amount_paise = request.data.get('amount_paise')
        bank_account_id = request.data.get('bank_account_id')

        if not amount_paise or not bank_account_id:
            return response.Response({"error": "amount_paise and bank_account_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_paise = int(amount_paise)
            if amount_paise <= 0:
                raise ValueError()
        except ValueError:
            return response.Response({"error": "Invalid amount_paise"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Atomic Transaction with Concurrency Control
        with transaction.atomic():
            # Row-level lock on the merchant to prevent race conditions on balance check
            locked_merchant = Merchant.objects.select_for_update().get(pk=merchant.id)
            
            current_balance = locked_merchant.get_balance_paise()
            
            if current_balance < amount_paise:
                error_resp = {"error": "Insufficient balance"}
                IdempotencyRecord.objects.create(
                    merchant=locked_merchant,
                    idempotency_key=idempotency_key,
                    response_status=status.HTTP_400_BAD_REQUEST,
                    response_body=error_resp
                )
                return response.Response(error_resp, status=status.HTTP_400_BAD_REQUEST)

            # Create Payout
            payout = Payout.objects.create(
                merchant=locked_merchant,
                amount_paise=amount_paise,
                bank_account_id=bank_account_id,
                idempotency_key=idempotency_key,
                status='PENDING'
            )

            # Create Ledger Entry (Debit)
            LedgerEntry.objects.create(
                merchant=locked_merchant,
                amount_paise=-amount_paise, # Negative for debit
                entry_type='PAYOUT',
                payout=payout,
                description=f"Payout request to {bank_account_id}"
            )

            success_data = PayoutSerializer(payout).data
            
            # Record Idempotency
            IdempotencyRecord.objects.create(
                merchant=locked_merchant,
                idempotency_key=idempotency_key,
                response_status=status.HTTP_201_CREATED,
                response_body=success_data
            )

        # 3. Trigger Background Task
        transaction.on_commit(lambda: process_payout_task.delay(payout.id))
        
        return response.Response(success_data, status=status.HTTP_201_CREATED)

    def list(self, request):
        merchant_id = request.query_params.get('merchant_id')
        if not merchant_id:
            return response.Response({"error": "merchant_id query param is required"}, status=status.HTTP_400_BAD_REQUEST)
        payouts = Payout.objects.filter(merchant_id=merchant_id).order_by('-created_at')
        serializer = PayoutSerializer(payouts, many=True)
        return response.Response(serializer.data)
