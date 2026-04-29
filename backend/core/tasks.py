import random
import time
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Payout, LedgerEntry

@shared_task(bind=True)
def process_payout_task(self, payout_id):
    try:
        payout = Payout.objects.get(id=payout_id)
    except Payout.DoesNotExist:
        return

    if payout.status not in ['PENDING', 'PROCESSING']:
        return

    # Update status to PROCESSING if it was PENDING
    if payout.status == 'PENDING':
        payout.status = 'PROCESSING'
        payout.save()

    # Simulate bank settlement
    # 70% success, 20% fail, 10% hang
    outcome = random.random()

    if outcome < 0.70:
        # SUCCESS
        payout.status = 'COMPLETED'
        payout.save()
    elif outcome < 0.90:
        # FAIL - Return funds
        with transaction.atomic():
            payout.status = 'FAILED'
            payout.save()
            
            LedgerEntry.objects.create(
                merchant=payout.merchant,
                amount_paise=payout.amount_paise, # Positive to credit back
                entry_type='REFUND',
                payout=payout,
                description=f"Reversal of failed payout {payout.id}"
            )
    else:
        # HANG - Stay in PROCESSING
        # This will be picked up by the stuck_payouts_watcher
        pass

@shared_task
def stuck_payouts_watcher():
    """
    Finds payouts stuck in PROCESSING for > 30 seconds and retries them.
    """
    cutoff = timezone.now() - timedelta(seconds=30)
    stuck_payouts = Payout.objects.filter(
        status='PROCESSING',
        updated_at__lte=cutoff,
        retry_count__lt=3
    )

    for payout in stuck_payouts:
        payout.retry_count += 1
        payout.updated_at = timezone.now() # Reset timer
        payout.save()
        process_payout_task.delay(payout.id)

    # Payouts that failed after max retries
    failed_after_retries = Payout.objects.filter(
        status='PROCESSING',
        updated_at__lte=cutoff,
        retry_count__gte=3
    )

    for payout in failed_after_retries:
        with transaction.atomic():
            payout.status = 'FAILED'
            payout.save()
            LedgerEntry.objects.create(
                merchant=payout.merchant,
                amount_paise=payout.amount_paise,
                entry_type='REFUND',
                payout=payout,
                description=f"Failed after max retries {payout.id}"
            )
