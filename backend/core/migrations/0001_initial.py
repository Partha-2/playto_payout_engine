# Generated migration for core app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paise', models.BigIntegerField()),
                ('bank_account_id', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('idempotency_key', models.UUIDField()),
                ('retry_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to='core.merchant')),
            ],
            options={
                'unique_together': {('merchant', 'idempotency_key')},
            },
        ),
        migrations.CreateModel(
            name='LedgerEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paise', models.BigIntegerField()),
                ('entry_type', models.CharField(choices=[('PAYMENT', 'Payment'), ('PAYOUT', 'Payout'), ('REFUND', 'Refund')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ledger_entries', to='core.merchant')),
                ('payout', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.payout')),
            ],
        ),
        migrations.CreateModel(
            name='IdempotencyRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idempotency_key', models.UUIDField()),
                ('response_status', models.IntegerField()),
                ('response_body', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.merchant')),
            ],
            options={
                'unique_together': {('merchant', 'idempotency_key')},
                'indexes': [models.Index(fields=['created_at'], name='core_idempo_created_idx')],
            },
        ),
    ]
