# Society Parking Payment Management App

A small full-stack app for a residential society to track monthly parking
payments: residents upload a payment screenshot each month, an admin
approves/rejects it, and everyone can see a 2D parking map colored by status.

- **Frontend:** React + Vite + Tailwind CSS (deploys to Vercel)
- **Backend:** FastAPI + SQLAlchemy + Alembic (deployable anywhere that runs Python)
- **Database:** MySQL
- **Auth:** JWT (access tokens) + bcrypt password hashing

Built for ~80–200 users. Intentionally no Redis, WebSockets, or microservices.

---

## Project structure

```
society-parking-app/
  backend/     FastAPI app, SQLAlchemy models, Alembic migrations
  frontend/    Vite + React + Tailwind SPA
```

---

## 1. Local setup — Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit DATABASE_URL, JWT_SECRET_KEY, etc.
```

Create the MySQL database (once):

```sql
CREATE DATABASE society_parking CHARACTER SET utf8mb4;
CREATE USER 'parking_user'@'localhost' IDENTIFIED BY 'parking_pass';
GRANT ALL PRIVILEGES ON society_parking.* TO 'parking_user'@'localhost';
```

Run migrations and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Optional: seed an admin user for local testing
(`admin@society.local` / `Admin@12345`):

```bash
python -m scripts.seed_admin
```

API docs: http://localhost:8000/docs

### Key environment variables (`backend/.env`)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | MySQL connection string |
| `JWT_SECRET_KEY` | Secret for signing access/reset tokens |
| `FRONTEND_URL` | Allowed CORS origin |
| `UPLOAD_DIR` | Where compressed screenshots are stored |
| `PAYMENT_GRACE_DAYS` | Days after month-end before a payment is marked OVERDUE |
| `DEFAULT_PAYMENT_AMOUNT` | Amount charged per month (flat rate for now) |

> **Note:** `forgot-password` currently returns the reset token directly in
> the API response instead of emailing it, since no email service is wired
> up yet. Swap this out for a real email provider before production use.

---

## 2. Local setup — Frontend

```bash
cd frontend
npm install
cp .env.example .env             # set VITE_API_BASE_URL if backend isn't on :8000
npm run dev
```

App runs at http://localhost:5173

---

## 3. Deployment

### Frontend → Vercel

1. Push `frontend/` to a Git repo (or import the whole monorepo and set
   **Root Directory** to `frontend` in the Vercel project settings).
2. Framework preset: Vite.
3. Set the environment variable `VITE_API_BASE_URL` to your deployed
   backend URL.
4. `vercel.json` already includes an SPA rewrite so client-side routing
   works on refresh/deep links.

### Backend → any Python host (Render, Railway, EC2, etc.)

1. Set the same environment variables as `.env.example` on the host.
2. Run `alembic upgrade head` once against the production database.
3. Start with a production server, e.g.:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
   ```
4. Make sure `UPLOAD_DIR` points at persistent storage (a mounted volume,
   not an ephemeral filesystem) so screenshots survive restarts/deploys.
5. Set `FRONTEND_URL` to your deployed Vercel URL so CORS allows it.

---

## 4. How the payment status logic works

- Each payment period is keyed by `(user_id, month, year)`, so periods like
  January 2027 don't collide with January 2026.
- A resident can only submit for the **current month**, or the **previous
  month if it's still unpaid**.
- A submission starts as `PENDING`. An admin then approves (`APPROVED` /
  green) or rejects (`REJECTED`) it.
- If a period has no approved payment and it's more than
  `PAYMENT_GRACE_DAYS` past the end of that month, it displays as
  `OVERDUE` (red) — whether or not there's a rejected submission sitting
  underneath it.
- Duplicate active submissions (pending or approved) for the same
  user/month/year are blocked; a rejected or overdue period can always
  receive a fresh submission.

## 5. Adding Razorpay later

The payment model already separates "submission" from "verification," so
Razorpay (or any gateway) can slot in as an alternative to the manual
screenshot flow: create the payment row with a `gateway_reference` instead
of a screenshot, mark it `APPROVED` automatically on a verified webhook,
and leave the manual-upload path as a fallback.
