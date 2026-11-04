# Security controls

- Admin bootstrap is environment-only; there is no public sign-up route.
- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes (310,000 iterations).
- Admin sessions are HMAC-SHA256 signed bearer tokens with an eight-hour expiry and issuer check.
- Admin write routes require an active user with the `admin` role.
- Login attempts are limited in-process to five attempts per source IP per minute.
- CORS uses an explicit origin allowlist; credentials are disabled.
- Security headers include frame denial, content-type sniffing protection, referrer policy, and a restrictive permissions policy.
- Pydantic schemas cap input lengths and restrict social links to HTTP(S).
- Visit records contain a daily hashed visitor key rather than a raw IP.

Before high-traffic production use, add a shared distributed rate limiter, secure HttpOnly cookie sessions with CSRF defenses if moving away from bearer tokens, centralized audit retention, object storage with upload scanning, automated dependency scanning, and a tested backup/restore schedule. The current in-memory login limiter resets on API restart and is not shared across multiple API instances.
