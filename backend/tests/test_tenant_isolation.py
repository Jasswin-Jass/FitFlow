import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cross_tenant_isolation_reads_and_writes(client: AsyncClient):
    # Register Gym Alpha
    resp_a = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Gym Alpha",
            "owner_name": "Alpha Owner",
            "email": "owner@gymalpha.com",
            "password": "AlphaPassword123!",
        },
    )
    assert resp_a.status_code == 200
    token_a = resp_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Gym Beta
    resp_b = await client.post(
        "/api/v1/auth/register",
        json={
            "gym_name": "Gym Beta",
            "owner_name": "Beta Owner",
            "email": "owner@gymbeta.com",
            "password": "BetaPassword123!",
        },
    )
    assert resp_b.status_code == 200
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Gym A creates a member
    mem_a_resp = await client.post(
        "/api/v1/members",
        headers=headers_a,
        json={
            "name": "Alpha Member One",
            "email": "m1@alpha.com",
            "phone": "+91 99999 00001",
            "status": "active",
        },
    )
    assert mem_a_resp.status_code == 201
    member_a_id = mem_a_resp.json()["id"]

    # 2. Gym B lists members -> MUST NOT see Gym A's member
    list_b = await client.get("/api/v1/members", headers=headers_b)
    assert list_b.status_code == 200
    b_members = list_b.json()["items"]
    assert all(m["id"] != member_a_id for m in b_members)

    # 3. Gym B attempts to read Gym A's member directly -> 403 Forbidden
    get_cross = await client.get(f"/api/v1/members/{member_a_id}", headers=headers_b)
    assert get_cross.status_code == 403
    assert get_cross.json()["error"] == "TenantAccessDenied"

    # 4. Gym B attempts to update Gym A's member -> 403 Forbidden
    patch_cross = await client.patch(
        f"/api/v1/members/{member_a_id}",
        headers=headers_b,
        json={"name": "Hacked Name"},
    )
    assert patch_cross.status_code == 403
    assert patch_cross.json()["error"] == "TenantAccessDenied"

    # 5. Gym B attempts to delete Gym A's member -> 403 Forbidden
    del_cross = await client.delete(f"/api/v1/members/{member_a_id}", headers=headers_b)
    assert del_cross.status_code == 403
    assert del_cross.json()["error"] == "TenantAccessDenied"

    # 6. Gym A can read their own member cleanly
    get_own = await client.get(f"/api/v1/members/{member_a_id}", headers=headers_a)
    assert get_own.status_code == 200
    assert get_own.json()["name"] == "Alpha Member One"
