import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_BACKEND = "http://127.0.0.1:8000"
BASE_FRONTEND = "http://localhost:3000"


def log(step: str, detail: str):
    print(f"\n[STEP {step}] {detail}")


def run_verification():
    with httpx.Client(timeout=10.0) as client:
        # 1. Health check
        log("1", "Verifying Backend /health")
        resp = client.get(f"{BASE_BACKEND}/health")
        assert resp.status_code == 200, f"Health check failed: {resp.text}"
        print("Backend Health Status:", resp.json())

        # 2. Frontend check
        log("2", "Verifying Frontend HTTP Server on port 3000")
        fe_resp = client.get(f"{BASE_FRONTEND}/login")
        assert fe_resp.status_code == 200, f"Frontend check failed: {fe_resp.status_code}"
        print("Frontend Status: 200 OK (HTML served successfully)")

        # 3. Step 1 of Demo: Register Brand New Gym -> Verify 0-state
        import time
        ts = int(time.time())
        log("3", f"Demo Step 1: Registering Brand New Gym 'Olympus Elite {ts}'")
        reg_resp = client.post(
            f"{BASE_BACKEND}/api/v1/auth/register",
            json={
                "gym_name": f"Olympus Elite Gym {ts}",
                "owner_name": "Vikram Seth",
                "email": f"vikram_{ts}@olympuselite.com",
                "password": "Olympus@2026",
            },
        )
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        new_token = reg_resp.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        # Check dashboard summary for brand new gym
        new_dash = client.get(f"{BASE_BACKEND}/api/v1/dashboard/summary", headers=new_headers)
        assert new_dash.status_code == 200, f"Summary failed: {new_dash.text}"
        new_summary = new_dash.json()
        print(f"New Gym Active Members: {new_summary['active_members']['value']}")
        print(f"New Gym MRR: {new_summary['mrr']['formatted_value']}")
        print(f"New Gym At-Risk: {new_summary['at_risk_members']['value']}")
        assert new_summary["active_members"]["value"] == 0
        assert new_summary["mrr"]["value"] == 0.0
        assert new_summary["at_risk_members"]["value"] == 0

        # 4. Step 2 of Demo: Login to Seeded Gym A (FitCore Fitness)
        log("4", "Demo Step 2: Logging into Seeded Gym A (FitCore Fitness)")
        login_a = client.post(
            f"{BASE_BACKEND}/api/v1/auth/login",
            json={"email": "karthik.ramesh@fitcorefitness.com", "password": "FitCore@2026"},
        )
        assert login_a.status_code == 200, f"Gym A login failed: {login_a.text}"
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        dash_a = client.get(f"{BASE_BACKEND}/api/v1/dashboard/summary", headers=headers_a)
        assert dash_a.status_code == 200
        summary_a = dash_a.json()
        print(f"Gym A Name: {summary_a['gym_name']}")
        print(f"Gym A Active Members: {summary_a['active_members']['formatted_value']} ({summary_a['active_members']['comparison_label']})")
        print(f"Gym A MRR: {summary_a['mrr']['formatted_value']} ({summary_a['mrr']['comparison_label']})")
        print(f"Gym A Renewal Rate: {summary_a['renewal_rate']['formatted_value']} ({summary_a['renewal_rate']['comparison_label']})")
        print(f"Gym A At-Risk Members Count: {summary_a['at_risk_members']['formatted_value']}")
        print(f"Gym A At-Risk List Size: {len(summary_a['at_risk_list'])}")
        assert summary_a["active_members"]["value"] >= 12
        assert summary_a["mrr"]["value"] > 10000
        assert len(summary_a["at_risk_list"]) > 0

        # 5. Step 3 of Demo: Add a new member in Gym A
        log("5", "Demo Step 3: Adding new member 'Deepak Natarajan' to Gym A")
        new_mem_resp = client.post(
            f"{BASE_BACKEND}/api/v1/members",
            headers=headers_a,
            json={
                "name": "Deepak Natarajan",
                "email": "deepak.natarajan@gmail.com",
                "phone": "+91 98409 99888",
                "status": "active",
            },
        )
        assert new_mem_resp.status_code == 201, f"Member creation failed: {new_mem_resp.text}"
        deepak = new_mem_resp.json()
        deepak_id = deepak["id"]
        print(f"Created Member: {deepak['name']} (ID: {deepak_id})")

        # 6. Step 4 of Demo: Get Quarterly Plan & Assign Membership with payment
        log("6", "Demo Step 4: Assigning Quarterly Pro membership and recording payment")
        plans_resp = client.get(f"{BASE_BACKEND}/api/v1/membership-plans", headers=headers_a)
        assert plans_resp.status_code == 200
        plans = plans_resp.json()["items"]
        quarterly_plan = next(p for p in plans if "Quarterly" in p["name"] or p["duration_days"] == 90)
        print(f"Selected Plan: {quarterly_plan['name']} (Price: ₹{quarterly_plan['price']}, Duration: {quarterly_plan['duration_days']} days)")

        mship_resp = client.post(
            f"{BASE_BACKEND}/api/v1/memberships",
            headers=headers_a,
            json={
                "member_id": deepak_id,
                "plan_id": quarterly_plan["id"],
                "create_payment": True,
            },
        )
        assert mship_resp.status_code == 201, f"Membership creation failed: {mship_resp.text}"
        mship = mship_resp.json()
        print(f"Created Membership ID: {mship['id']}, Status: {mship['status']}, End Date: {mship['end_date']}")

        # 7. Step 5 & 6 of Demo: Trigger Metric Recompute and verify updated KPIs
        log("7", "Demo Step 5 & 6: Recomputing metrics and verifying live dashboard changes")
        old_active = summary_a["active_members"]["value"]
        old_mrr = summary_a["mrr"]["value"]

        recomp_resp = client.post(f"{BASE_BACKEND}/api/v1/admin/recompute-metrics", headers=headers_a)
        assert recomp_resp.status_code == 200, f"Recomputation failed: {recomp_resp.text}"
        updated_summary = recomp_resp.json()
        new_active = updated_summary["active_members"]["value"]
        new_mrr = updated_summary["mrr"]["value"]

        print(f"Active Members: {old_active} -> {new_active} (+{new_active - old_active})")
        print(f"MRR: ₹{old_mrr:,.2f} -> ₹{new_mrr:,.2f} (+₹{new_mrr - old_mrr:,.2f})")
        assert new_active == old_active + 1, "Active members count should increment by 1"
        expected_mrr_inc = round(quarterly_plan["price"] * (30.0 / quarterly_plan["duration_days"]), 2)
        assert round(new_mrr - old_mrr, 1) == round(expected_mrr_inc, 1), f"MRR increase should match 30-day normalized plan value ({expected_mrr_inc})"

        # 8. Step 7 of Demo: Multi-Tenancy & Zero Data Leakage with Gym B
        log("8", "Demo Step 7: Logging into Gym B (Urban Strength) to verify zero data leakage")
        login_b = client.post(
            f"{BASE_BACKEND}/api/v1/auth/login",
            json={"email": "arjun.kumar@urbanstrength.in", "password": "Urban@2026"},
        )
        assert login_b.status_code == 200, f"Gym B login failed: {login_b.text}"
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Check members in Gym B -> Deepak must not exist
        list_b = client.get(f"{BASE_BACKEND}/api/v1/members", headers=headers_b)
        assert list_b.status_code == 200
        b_member_ids = [m["id"] for m in list_b.json()["items"]]
        assert deepak_id not in b_member_ids, "Deepak must NOT appear in Gym B's member list!"
        print("Verified: Deepak does NOT appear in Gym B's member list.")

        # Attempt direct cross-tenant GET on Deepak from Gym B -> must return 403 Forbidden
        cross_get = client.get(f"{BASE_BACKEND}/api/v1/members/{deepak_id}", headers=headers_b)
        assert cross_get.status_code == 403, f"Expected 403 Forbidden, got {cross_get.status_code}"
        print("Verified: Direct cross-tenant GET returns HTTP 403 Forbidden (TenantAccessDenied).")

        # Attempt direct cross-tenant PATCH from Gym B -> must return 403 Forbidden
        cross_patch = client.patch(f"{BASE_BACKEND}/api/v1/members/{deepak_id}", headers=headers_b, json={"name": "Hacked"})
        assert cross_patch.status_code == 403, f"Expected 403 Forbidden, got {cross_patch.status_code}"
        print("Verified: Cross-tenant PATCH returns HTTP 403 Forbidden.")

        print("\n" + "=" * 60)
        print("🎉 ALL 7 DEMO STEPS VERIFIED 100% WORKING END-TO-END!")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    run_verification()
