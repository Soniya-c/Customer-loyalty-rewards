# Assumptions and decisions

| Gap in brief | Assumption chosen | Why |
|---|---|---|
| Customer identity | Email address identifies a customer account | Simple for an MVP; avoids collecting unnecessary personal data. |
| Purchase verification | Each physical box contains a unique one-time alphanumeric code | Works without retailer integrations or requiring customers to upload receipts. |
| Code format | Three groups of four characters from an ambiguity-reduced alphabet | Easier to type and less error-prone than a long opaque string. |
| Code secrecy | Store only SHA-256 hashes; display generated raw codes once | Limits impact if the database is read. |
| Points value | 10 points per redeemed box by default | A simple configurable baseline; the business can tune it. |
| Redemption timing | Award points immediately after a valid code is redeemed | Keeps the customer experience fast and understandable. |
| Reward catalog | MVP tracks points but does not yet support point spending or reward fulfilment | Reward tiers, margins, and fulfilment rules were not supplied; avoids inventing liabilities. |
| Admin access | One shared admin password supplied through environment configuration | Minimal local demo; production should use individual accounts and hashed credentials. |
| Dashboard scope | Customer balances, aggregate counts, and recent redemptions | Covers the owner's basic view/manage/monitor needs without adding analytics complexity. |
| Deployment | Local runnable app; no hosting provider or domain supplied | A deployed URL cannot be truthfully provided without deployment credentials and infrastructure. |
| Database | SQLite for single-instance demonstration | Zero external services and easy local setup; production multi-instance deployments should use PostgreSQL. |
| Initial codes | Start with an empty code inventory; admin generates the first batch | Avoids inserting demo code hashes whose raw values are unavailable for redemption. |
| Abuse controls | Unique code hashes, single-use state, transactional redemption, and basic input validation | Core replay protection; production also needs throttling, CSRF, monitoring, and operational controls. |
