# Tests

## Automated tests
Run:
```bash
python -m unittest discover -s tests -v
```
The automated suite uses a temporary SQLite database and Flask's test client. Expected results are documented in the test names and assertions.

## Manual acceptance test plan
| # | Scenario | Steps | Expected result |
|---|---|---|---|
| 1 | First run | Start app with a clean database | Tables and five demo code hashes are initialized; home page loads |
| 2 | Valid code | Generate a code in admin and redeem it with an email | Success message; points and box count increase |
| 3 | Replay | Submit the same code again | Rejected as already redeemed; balance unchanged |
| 4 | Invalid code | Submit a made-up code | Rejected; no customer record created |
| 5 | Admin login | Visit `/admin`, sign in with configured password | Dashboard appears |
| 6 | Wrong admin password | Submit an incorrect password | Login rejected |
| 7 | Batch bounds | Request 0 or 501 codes | Validation error; no codes generated |
| 8 | Batch creation | Generate 10 codes | 10 unique codes shown once; unused count increases by 10 |
| 9 | Dashboard monitoring | Redeem one generated code | Redeemed count, points, customer and recent activity update |
| 10 | Health endpoint | Request `/health` | JSON status is `ok` |

## Execution status
Automated tests are included and intended to be run locally after installing `requirements.txt`. Manual scenarios are a checklist, not claimed as executed in this packaging environment. Production sign-off should add concurrency tests, rate-limit tests, CSRF tests, and a database backup/restore drill.
