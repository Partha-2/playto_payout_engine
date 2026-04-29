from rest_framework import serializers
from .models import Merchant, Payout, LedgerEntry

class MerchantSerializer(serializers.ModelSerializer):
    balance_paise = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = ['id', 'name', 'balance_paise', 'created_at']

    def get_balance_paise(self, obj):
        return obj.get_balance_paise()

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ['id', 'amount_paise', 'bank_account_id', 'status', 'idempotency_key', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']

class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = ['id', 'amount_paise', 'entry_type', 'payout', 'description', 'created_at']
