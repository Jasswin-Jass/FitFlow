# FitFlow — Business Intelligence Platform for Gyms

> **Turn gym operations data into actionable business intelligence.**

FitFlow is a multi-tenant SaaS platform built for gym owners. Unlike generic gym management tools that focus on attendance logs or workout lists, FitFlow is purpose-built as an **executive business intelligence engine**. It captures real-world operational gym data (members, memberships, recurring plans, payments) and aggregates them into deterministic financial and retention KPIs.

---

## 🚀 Key Highlights & Architecture

- **True Database-Level Multi-Tenancy**: Tenant root is `gyms`. Every tenant-owned record has a `gym_id UUID NOT NULL REFERENCES gyms(id)`. PostgreSQL Row-Level Security (RLS) policies enforce zero data leakage at the database layer.
- **Fast Dashboard with Precomputed Analytics**: The executive dashboard reads precomputed daily metrics from `summary_metrics` rather than executing expensive live table scans on every page load.
- **pg_cron Scheduled Aggregation & Manual Trigger**: Runs nightly background aggregation in PostgreSQL (`pg_cron`) and provides an on-demand recomputation endpoint (`POST /admin/recompute-metrics`) for real-time validation.
- **Mathematically Deterministic KPIs**:
  - **Active Members**: Members with active memberships valid today.
  - **MRR (Monthly Recurring Revenue)**: Normalized to a 30-day baseline across all active memberships:
    $$\text{MRR} = \sum_{\text{active memberships}} \left(\text{price} \times \frac{30}{\text{duration\_days}}\right)$$
  - **Renewal Rate**: Deterministic ratio of members renewed over a 30-day rolling window of expiring contracts.
  - **At-Risk Members**: Pure deterministic rule flagging members expiring within 7 days or having recent overdue failed payments.
- **Modern Premium Stack**:
  - **Backend**: Python 3.12, FastAPI modular monolith, Async SQLAlchemy 2.0, Alembic, Pydantic v2.
  - **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, TanStack Query, Recharts, Sonner.

---

## 📁 Project Structure

```
FitFlow/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 001_initial_schema.py        # All 8 tables, indexes, constraints
│   │   │   ├── 002_rls_policies.py          # PostgreSQL Row-Level Security (RLS)
│   │   │   └── 003_pg_cron_setup.sql        # pg_cron scheduled aggregation procedure
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── app/
│   │   ├── core/                            # Config, security (bcrypt & JWT), exceptions
│   │   ├── database/                        # Async session & tenant RLS session context
│   │   ├── models/                          # Gym, User, Member, Trainer, Plan, Membership, Payment, SummaryMetric
│   │   ├── schemas/                         # Pydantic v2 validation models
│   │   ├── services/                        # Member, trainer, membership, payment services
│   │   ├── auth/                            # Auth service & RBAC / tenant dependencies
│   │   ├── analytics/                       # Deterministic KPI engine & aggregation service
│   │   ├── api/v1/                          # REST routers
│   │   └── main.py                          # FastAPI app entry point & centralized handlers
│   ├── tests/                               # 100% passing Pytest suite (Auth, RLS, CRUD, Analytics)
│   ├── seed.py                              # Realistic Tamil Nadu gym seed script
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── (auth)/                          # Login (with 1-click switcher) & Registration
│   │   ├── (dashboard)/                     # Hero BI Dashboard, Members, Memberships, Payments, Trainers
│   │   ├── layout.tsx                       # App layout with TanStack QueryProvider & Sonner
│   │   └── globals.css                      # Tailwind dark theme variables
│   ├── components/                          # KPI cards, historical charts, at-risk table, sidebar, header
│   ├── hooks/                               # TanStack Query custom hooks
│   ├── lib/                                 # API client with token injection, formatters
│   ├── types/                               # TypeScript API types
│   └── package.json
├── DEMO.md                                  # Step-by-step hackathon live presentation script
└── README.md
```

---

## ⚡ Prerequisites

- **Node.js**: v18.17+ or v20+ (tested on Node v22.11.0)
- **Python**: 3.11+ (tested on Python 3.12.3)
- **Database**: PostgreSQL (Local or Supabase) or local fallback SQLite (`sqlite+aiosqlite:///./fitflow.db`).

---

## 🛠️ Supabase / PostgreSQL Setup

### 1. Connecting to Supabase
In `backend/.env`, set your connection string:
```env
DATABASE_URL=postgresql+asyncpg://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### 2. Enabling RLS & pg_cron in Supabase
In your Supabase SQL Editor:
1. Run the migration script in `backend/alembic/versions/003_pg_cron_setup.sql`.
2. This creates the stored procedure `recompute_gym_metrics_for_all()` and schedules it to run automatically every night at 02:00 UTC.

---

## 📦 Quick Start Guide

### 1. Start the Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
# source venv/bin/activate

# (Optional) Install dependencies if running on a new machine:
pip install -r requirements.txt

# Run database seed script (Seeds Gym A and Gym B with realistic data)
python seed.py

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

FastAPI interactive OpenAPI documentation is available at:
👉 **`http://localhost:8000/docs`**

---

### 2. Start the Frontend

In a second terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Start Next.js development server on port 3000
npm run dev
```

Open your browser to:
👉 **`http://localhost:3000`**

---

## 🔑 Demo Credentials

FitFlow comes pre-loaded with realistic, production-grade seed data for demonstration:

| Gym Name | Location | Email | Password | Details |
|---|---|---|---|---|
| **FitCore Fitness** (Gym A) | Chennai, TN | `karthik.ramesh@fitcorefitness.com` | `FitCore@2026` | 18 members, 3 trainers, ₹22.7K MRR, 3 at-risk |
| **Urban Strength Club** (Gym B) | Coimbatore, TN | `arjun.kumar@urbanstrength.in` | `Urban@2026` | 10 members, 2 trainers, ₹12.0K MRR, 1 at-risk |

*(On the `/login` screen, use the **1-Click Demo Buttons** to sign in instantly with either tenant without typing credentials).*

---

## 🧪 Running Automated Tests

Run the complete backend pytest suite:

```bash
cd backend
.\venv\Scripts\python -m pytest -v
```

**Test Coverage**:
- `test_auth.py`: Gym registration, JWT issuance, password verification, duplicate email prevention.
- `test_tenant_isolation.py`: Cross-tenant boundary verification (Gym A cannot read, write, or delete Gym B records).
- `test_crud.py`: Members, Trainers, Plans, Memberships, and Payments CRUD operations.
- `test_analytics.py`: Mathematical accuracy of the aggregation engine and `summary_metrics` persistence.

---

## 🔒 Multi-Tenancy Explanation

FitFlow enforces multi-tenancy at two complementary layers:

1. **Database Layer (PostgreSQL Row-Level Security)**:
   - Every tenant table has `gym_id UUID NOT NULL`.
   - On request authentication, FastAPI sets the session parameter:
     `SET LOCAL app.current_gym_id = '<user.gym_id>'`.
   - PostgreSQL RLS policies enforce `USING (gym_id = NULLIF(current_setting('app.current_gym_id', true), '')::uuid)`.
   - Direct raw SQL queries from unauthorized tenants are rejected by the PostgreSQL engine itself.

2. **Application Layer (FastAPI Service Level)**:
   - All queries filter by `WHERE gym_id = current_user.gym_id`.
   - Cross-tenant lookups raise `TenantAccessDeniedException` (HTTP 403 Forbidden).
   - Role-Based Access Control (`owner`, `trainer`, `staff`) protects administrative actions like plan creation and metric recomputation.

---

## 🎯 Verification & Demo Script

See **[DEMO.md](file:///e:/Computer%20Science/Web%20dev/Web%20projects/FitFlow/DEMO.md)** for the complete 7-step presentation guide.
