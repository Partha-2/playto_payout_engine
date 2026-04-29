# Playto Founding Engineer Challenge - Technical Explainer

### 1. The Ledger
**Balance Calculation Query:**
```python
LedgerEntry.objects.filter(merchant=self).aggregate(
    balance=Coalesce(Sum('amount_paise'), 0, output_field=models.BigIntegerField())
)['balance']
```
**Why model credits and debits this way?**
We use a **Double-Entry-inspired Ledger**. Every movement of money is an immutable record in the `LedgerEntry` table. 
- **Credits** (Customer payments) are stored as positive integers.
- **Debits** (Payouts) are stored as negative integers.
- **Refunds** (Failed payouts) are stored as positive integers (reversing the debit).
This approach provides a perfect audit trail. The balance is never stored as a mutable column on the `Merchant` model (which is prone to desync), but is always derived from the sum of its parts. This ensures the invariant: `Sum(Credits) - Sum(Debits) == Displayed Balance`.

### 2. The Lock
**Concurrency Control Code:**
```python
with transaction.atomic():
    # Row-level lock on the merchant to prevent race conditions on balance check
    locked_merchant = Merchant.objects.select_for_update().get(pk=merchant.id)
    current_balance = locked_merchant.get_balance_paise()
    
    if current_balance < amount_paise:
        # Reject...
```
**Database Primitive:**
This relies on **`SELECT FOR UPDATE`**. When a payout request arrives, we lock the specific `Merchant` row in the database. Any other concurrent request for the same merchant will block at the `select_for_update()` line until the first transaction commits or rolls back. This prevents the "double-spend" race condition where two requests both see a 100 INR balance, and both proceed to deduct 60 INR.

### 3. The Idempotency
**How the system knows it has seen a key before:**
We use an `IdempotencyRecord` table that stores the `Idempotency-Key` (UUID) scoped to a `Merchant`. 
Before processing any logic, we check:
```python
existing_record = IdempotencyRecord.objects.filter(merchant=merchant, idempotency_key=idempotency_key).first()
if existing_record:
    return response.Response(existing_record.response_body, status=existing_record.response_status)
```
**What happens if the first request is in flight when the second arrives?**
The `IdempotencyRecord` is created *inside* the same atomic transaction as the payout. However, to handle the "in-flight" case properly, we rely on the `unique_together` constraint on `(merchant, idempotency_key)`. If two identical requests arrive at the exact same millisecond, the second one will either:
1. Block on the `select_for_update` of the Merchant (if the first one is already there).
2. Fail with a `IntegrityError` when trying to save the `Payout` or `IdempotencyRecord` because of the uniqueness constraint.
In our implementation, the `IdempotencyRecord` is checked first. If it doesn't exist, we enter the transaction.

### 4. The State Machine
**Blocking illegal transitions:**
The state machine logic is enforced in the `tasks.py` and `views.py`.
```python
if payout.status not in ['PENDING', 'PROCESSING']:
    return # Ignore if already COMPLETED or FAILED
```
In a more complex system, I would use `django-fsm`. Here, the check is explicit: once a payout hits `COMPLETED` or `FAILED`, no further background processing (retries or simulation) can modify its state. The refund logic for `FAILED` payouts is wrapped in a `transaction.atomic()` block to ensure the state change and the money return happen together or not at all.

### 5. The AI Audit
**Example of AI-generated bug:**
Initially, an AI might suggest calculating the balance in Python:
```python
# AI SUGGESTION (WRONG)
entries = LedgerEntry.objects.filter(merchant=merchant)
balance = sum(e.amount_paise for e in entries) 
```
**The Catch:** This is a "check-then-act" race condition. Between the time Python fetches the rows and the time it saves the new payout, another process could have added a debit. 
**The Replacement:** I replaced this with **database-level aggregation** (`Sum`) combined with **`select_for_update()`**. This ensures that the balance calculation happens within a locked context, and no other process can modify the ledger for that merchant until we are done.
