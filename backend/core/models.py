from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

class Merchant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_balance_paise(self):
        """
        Calculates the available balance using DB-level aggregation.
        Sum of all ledger entries.
        """
        return LedgerEntry.objects.filter(merchant=self).aggregate(
            balance=Coalesce(Sum('amount_paise'), 0, output_field=models.BigIntegerField())
        )['balance']

    def __str__(self):
        return self.name

class Payout(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='payouts')
    amount_paise = models.BigIntegerField()
    bank_account_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    idempotency_key = models.UUIDField()
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('merchant', 'idempotency_key')

class LedgerEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('PAYMENT', 'Payment'),
        ('PAYOUT', 'Payout'),
        ('REFUND', 'Refund'),
    ]
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='ledger_entries')
    amount_paise = models.BigIntegerField() # Positive for credit, Negative for debit
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    payout = models.ForeignKey(Payout, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class IdempotencyRecord(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    idempotency_key = models.UUIDField()
    response_status = models.IntegerField()
    response_body = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('merchant', 'idempotency_key')
        indexes = [
            models.Index(fields=['created_at']),
        ]
