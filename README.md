# Meridian API

The Django REST Framework backend for [Meridian](../meridian) — an
integrated electronic patient health record platform. This is a **private**
API: it's called only server-side from the Next.js app (never from a
browser directly), so it carries no CORS/CSRF surface for public clients.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # demo staff + patients, password meridian123 for all
python manage.py runserver 8811
```

The Next.js app expects this running on `http://127.0.0.1:8811` in
development (see `DJANGO_API_URL` in `meridian/.env`).

## Architecture

- **Custom user model** (`accounts.User`) — staff accounts with a `role`
  field (ADMIN / DOCTOR / NURSE / RECORDS_OFFICER / PHARMACIST); `is_active`
  doubles as the ACTIVE/INACTIVE status the frontend expects.
- **Auth**: `djangorestframework-simplejwt`. `/api/auth/login/` returns an
  access + refresh token pair; the Next.js app only persists the access
  token (8h lifetime) in an httpOnly cookie — there's no refresh flow on
  the frontend, matching the shift-length session the app was designed
  around. `/api/auth/me/` is how the frontend resolves "who is this token."
- **RBAC**: `core/permissions.py` has a `role_required(*roles)` factory
  used across every view. This is the *real* authorization boundary — the
  Next.js side also hides nav items per role, but that's UX only.
- **Apps**: `accounts` (users/auth), `patients` (registration, search,
  dashboard/reports aggregation), `clinical` (medical records,
  prescriptions, lab results), `scheduling` (appointments).
- **Field naming**: serializers expose camelCase (`firstName`, `dateOfBirth`,
  ...) via DRF `source=` mapping, so the API reads naturally from a JS
  frontend despite Django/Python's snake_case convention underneath.
- **Database**: SQLite for development. Swap `DATABASES` in
  `core/settings.py` for Postgres in production (see the main project's
  README for a hosting recommendation).

## Useful commands

```bash
python manage.py createsuperuser   # for /admin/ access
python manage.py seed_demo         # wipes and reseeds demo data
python manage.py makemigrations && python manage.py migrate
```
