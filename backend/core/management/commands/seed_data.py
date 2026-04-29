from django.core.management.base import BaseCommand
from core.models import Merchant, LedgerEntry
import random

class Command(BaseCommand):
    help = 'Seed merchants and credit history'

    def handle(self, *args, **options):
        merchants = [
            'Alice Agencies',
            'Bob Freelancing',
            'Charlie Studios'
        ]

        for name in merchants:
            merchant, created = Merchant.objects.get_or_create(name=name)
            if created:
                # Add some initial payments (Credits)
                for i in range(5):
                    amount = random.randint(10000, 50000) # 100 to 500 INR
                    LedgerEntry.objects.create(
                        merchant=merchant,
                        amount_paise=amount,
                        entry_type='PAYMENT',
                        description=f"Client payment {i+1}"
                    )
                self.stdout.write(self.style.SUCCESS(f'Created merchant {name} with balance {merchant.get_balance_paise()}'))
            else:
                self.stdout.write(f'Merchant {name} already exists')
