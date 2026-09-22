# FitFlow — Hackathon Presentation & Live Demo Guide

This presentation script guides you through the live demonstration of **FitFlow**, proving that every business intelligence metric is real, deterministic, and isolated between gym tenants.

---

## Demo Credentials Summary

| Gym | Tenant Name | Location | Email | Password | Pre-seeded State |
|---|---|---|---|---|---|
| **Gym A** | **FitCore Fitness** | Chennai, TN | `karthik.ramesh@fitcorefitness.com` | `FitCore@2026` | 18 Members, 3 Plans, ₹22.7K MRR, 3 At-Risk |
| **Gym B** | **Urban Strength** | Coimbatore, TN | `arjun.kumar@urbanstrength.in` | `Urban@2026` | 10 Members, 3 Plans, ₹12.0K MRR, 1 At-Risk |

*(Tip: Both demo accounts can also be logged into with a single click directly from the `/login` screen via the **Demo Quick-Switch** buttons!)*

---

## The 7-Step Hackathon Demo Script

### Step 1: Register a Brand-New Gym (Demonstrating True Zero-State)
1. Open the browser to `http://localhost:3000/register`.
2. Enter:
   - **Gym Name**: `Olympus Elite Gym`
   - **Owner Full Name**: `Vikram Seth`
   - **Work Email**: `vikram@olympuselite.com`
   - **Password**: `Olympus@2026`
3. Click **Create Gym & Open Dashboard**.
4. **Judge Value Point**:
   - The dashboard opens showing **0 Active Members**, **₹0 MRR**, **0.0% Renewal Rate**, and **0 At-Risk Members**.
   - No mock data or fake numbers are rendered. It is a genuine, pristine newly-provisioned tenant.

---

### Step 2: Login to Seeded Gym A ("FitCore Fitness")
1. Log out, then on `/login`, click the one-click button: **"FitCore (Gym A)"**.
2. **Observe the Executive BI Dashboard**:
   - **Active Members**: 15 members (with **+6.7% vs last period** trend badge).
   - **MRR**: ₹21,800 or ₹0.22L (with **+8.4% vs last period** trend badge).
   - **Renewal Rate**: 87.4% (with **+3.2% pts vs last period** trend badge).
   - **At-Risk Members**: 3 members (highlighted with warning badge).
   - **30-Day Performance Trajectory**: Interactive Recharts area chart showing daily MRR and active members progression over the last 30 days.
   - **Plan Distribution**: Breakdown showing revenue contribution by plan (Monthly Standard, Quarterly Pro, Annual Elite).
   - **At-Risk Action Center**: Real table listing the 3 members needing attention:
     - *Deepa Subramanian* (Membership expiring in 3 days)
     - *Suresh Kumar* (Membership expiring in 5 days)
     - *Divya Balaji* (Failed payment of ₹1,500 overdue)

---

### Step 3: Add a New Member
1. Click **Members** in the sidebar.
2. Click **+ Add Member**.
3. Enter:
   - **Name**: `Deepak Natarajan`
   - **Email**: `deepak.natarajan@gmail.com`
   - **Phone**: `+91 98409 99888`
4. Click **Save Member**.
5. Deepak Natarajan immediately appears in the member table. Notice his status is `active` and current plan is `No active plan`.

---

### Step 4: Assign a Membership & Record Payment
1. Click **Memberships** in the sidebar.
2. Click **+ Assign New Membership**.
3. Select:
   - **Member**: `Deepak Natarajan`
   - **Membership Plan**: `Quarterly Pro — ₹4,000 (90 days)`
   - **Start Date**: Today's date
   - **Auto-record payment in full**: Checked
4. Click **Confirm Membership**.
5. Deepak's 90-day membership is created, and a successful ₹4,000 payment transaction is automatically created.
6. Navigate to **Payments** to show the judges the audited transaction of ₹4,000 for Deepak Natarajan.

---

### Step 5: Trigger Metric Recomputation
1. Return to the **Dashboard** (`/dashboard`).
2. Point out that the dashboard currently reads precomputed metrics from `summary_metrics`.
3. Click the **"Recompute Metrics"** button in the header (which executes `POST /admin/recompute-metrics` in the backend).
4. Watch the loading spinner and the instant Sonner toast notification.

---

### Step 6: Verify Dashboard Updates with Mathematically Precise KPIs
1. Observe the newly computed values:
   - **Active Members**: Automatically increments from 15 → **16 members**.
   - **MRR**: Automatically increments by the normalized 30-day value of Quarterly Pro:
     $$\Delta \text{MRR} = ₹4,000 \times \left(\frac{30}{90}\right) = +₹1,333.33$$
     MRR updates dynamically to reflect this change.
   - All charts and plan distribution bars update in real time.

---

### Step 7: Multi-Tenancy & Zero Data Leakage (Gym A vs. Gym B)
1. Click the logout icon in the bottom-left of the sidebar.
2. On the login screen, click **"Urban Strength (Gym B)"**.
3. Notice:
   - Header shows **Urban Strength Club (Coimbatore)**.
   - Dashboard shows completely different metrics (10 active members, ₹12,000 MRR).
   - Go to **Members**: Deepak Natarajan and the other 18 FitCore members **do not exist**.
   - Go to **Payments**: Zero FitCore payments are visible.
   - Go to **Trainers**: Only Urban Strength coaches (*Dinesh Karthikeyan*, *Lakshmi Narayanan*) appear.
4. **Security Proof**: Even if a user forged an API request to `GET /api/v1/members/{deepak_id}`, the backend enforces both PostgreSQL Row-Level Security (`app.current_gym_id`) and service-level checks, returning **403 Forbidden: TenantAccessDenied**.

---

## Deterministic Formulas Used in FitFlow

1. **Active Members**:
   $$\text{Active Members} = \text{COUNT}(\text{DISTINCT } \text{member\_id}) \text{ where } \text{status} = \text{'active'} \land \text{today} \in [\text{start\_date}, \text{end\_date}]$$

2. **Monthly Recurring Revenue (MRR)**:
   $$\text{MRR} = \sum_{m \in \text{active}} \left( \text{plan.price} \times \frac{30}{\text{plan.duration\_days}} \right)$$

3. **Renewal Rate**:
   $$\text{Renewal Rate} = \left( \frac{\text{Members renewed in 30-day window}}{\text{Memberships ended in 30-day window}} \right) \times 100\%$$

4. **At-Risk Members**:
   $$\text{At-Risk} = \{ m \mid \text{m.end\_date} \in [\text{today}, \text{today} + 7\text{d}] \} \cup \{ m \mid \exists \text{ failed payment in 30d without subsequent success} \}$$
