"""Tests for Capital.com rate limiter."""
import asyncio
import pytest

from app.execution.broker.capital.rate_limiter import CapitalRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_first_requests():
    limiter = CapitalRateLimiter()
    # Should not block for the first MAX_PER_SECOND requests.
    for _ in range(int(CapitalRateLimiter.MAX_PER_SECOND)):
        await limiter.wait()


@pytest.mark.asyncio
async def test_rate_limiter_throttles_excess_requests():
    limiter = CapitalRateLimiter()
    # Exhaust the per-second budget.
    for _ in range(int(CapitalRateLimiter.MAX_PER_SECOND)):
        await limiter.wait()

    start = asyncio.get_event_loop().time()
    # The next request must wait until the 1-second window frees a slot.
    await limiter.wait()
    elapsed = asyncio.get_event_loop().time() - start

    assert elapsed >= 0.8, "Rate limiter should throttle requests exceeding per-second budget"


@pytest.mark.asyncio
async def test_rate_limiter_records_requests_in_all_windows():
    limiter = CapitalRateLimiter()
    await limiter.wait()

    assert len(limiter._second_window) == 1
    assert len(limiter._minute_window) == 1
    assert len(limiter._five_minute_window) == 1
