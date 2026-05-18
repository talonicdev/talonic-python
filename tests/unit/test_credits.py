"""Credits resource — get_balance. 1 op."""

import httpx
import respx

from talonic.resources.credits import AsyncCredits, Credits


@respx.mock
def test_get_balance_sync(sync_transport):
    respx.get("https://api.talonic.com/v1/credits/balance").mock(
        return_value=httpx.Response(
            200,
            json={
                "balance_credits": 1000,
                "balance_eur": 2.0,
                "burn_rate_30d_credits": 50,
                "projected_runway_days": 600,
                "tier": "standard",
                "tier_resets_at": "2026-06-01T00:00:00Z",
            },
        )
    )
    r = Credits(sync_transport).get_balance()
    assert r.data["balance_credits"] == 1000


@respx.mock
async def test_get_balance_async(async_transport):
    respx.get("https://api.talonic.com/v1/credits/balance").mock(
        return_value=httpx.Response(200, json={"balance_credits": 0})
    )
    r = await AsyncCredits(async_transport).get_balance()
    assert r.data["balance_credits"] == 0
