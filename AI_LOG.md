# AI interaction log

The following are representative prompts/interactions used while designing this MVP. The log records mistakes and corrections rather than treating AI output as authoritative.

1. **Prompt:** "Design a loyalty flow for boxed products without retailer integrations."  
   **Useful result:** a unique code inside each box is a low-friction proof-of-purchase mechanism.  
   **Decision:** adopted; documented in `ASSUMPTIONS.md`.

2. **Prompt:** "How should the app prevent a customer from redeeming a code twice?"  
   **Useful result:** hash codes at rest, unique constraints, and transactional state changes.  
   **Decision:** implemented in the redemption endpoint and schema.

3. **Prompt:** "Generate a Flask/SQLite data model for codes, customers, and redemptions."  
   **AI was wrong:** an early draft only checked `status='unused'` and then updated it in a separate transaction, which could allow two simultaneous requests to pass the check.  
   **How noticed:** reviewed the sequence and recognized a time-of-check/time-of-use race.  
   **Fix:** use `BEGIN IMMEDIATE`, a conditional `UPDATE ... WHERE status='unused'`, and verify exactly one row changed.

4. **Prompt:** "Create a customer redemption form with email and code."  
   **Useful result:** simple server-rendered form with validation.  
   **Decision:** adopted; added email normalization and length checks.

5. **Prompt:** "Build an owner dashboard to monitor loyalty performance."  
   **AI was wrong:** an early dashboard proposal showed a lifetime points total but did not distinguish redeemed from unused codes, making packaging inventory hard to monitor.  
   **How noticed:** compared dashboard metrics against the owner's requirement to manage and monitor rewards and code inventory.  
   **Fix:** added separate redeemed/unused counts, customer balances, and recent redemption history.

6. **Prompt:** "What should happen when a code is invalid or already used?"  
   **Useful result:** clear, non-sensitive customer messages.  
   **Decision:** adopted without revealing stored hashes or internal IDs.

7. **Prompt:** "Write tests for the main redemption paths."  
   **Useful result:** test success, invalid code, replay, and admin access.  
   **Decision:** implemented automated `unittest` coverage; production concurrency/load tests remain a follow-up.

8. **Prompt:** "Review the repository for launch risks."  
   **Useful result:** identified missing CSRF, rate limiting, hardened cookies, password hashing, and production database concerns.  
   **Decision:** documented as explicit production hardening work in `README.md` and `ARCHITECTURE.md`.
