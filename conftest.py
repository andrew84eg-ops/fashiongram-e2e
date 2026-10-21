"""Shared fixtures.

Design choices:
- Every test gets a brand-new member, so tests never depend on each other.
- Members are created through the HTTP API (fast); the browser is signed in by
  sharing the session cookie, so only the tests *about* login go through the form.
- Waits are on real signals (a response, an element), never fixed sleeps.
"""

from collections.abc import Callable, Iterator

import pytest
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright, expect

from utils.server_fn import is_server_fn
from utils.test_data import Member, new_member

expect.set_options(timeout=15_000)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, base_url):
    return {**browser_context_args, "base_url": base_url, "viewport": {"width": 1280, "height": 900}}


@pytest.fixture
def api(playwright: Playwright, base_url: str) -> Iterator[APIRequestContext]:
    """HTTP client for the auth API. Better Auth checks the Origin header on POSTs."""
    ctx = playwright.request.new_context(base_url=base_url, extra_http_headers={"Origin": base_url})
    yield ctx
    ctx.dispose()


def register(api: APIRequestContext, member: Member) -> dict:
    response = api.post(
        "/api/auth/sign-up/email",
        data={"email": member.email, "password": member.password, "name": member.name},
    )
    assert response.ok, f"sign-up failed: {response.status} {response.text()}"
    return response.json()


def sign_in_context(context: BrowserContext, base_url: str, member: Member) -> None:
    """Sign in through the API; the session cookie lands in the browser context."""
    response = context.request.post(
        "/api/auth/sign-in/email",
        data={"email": member.email, "password": member.password},
        headers={"Origin": base_url},
    )
    assert response.ok, f"sign-in failed: {response.status} {response.text()}"


def open_as_new_member(page: Page) -> None:
    """Load the app once and wait for first-visit setup (starter closet + follows).

    The app shell fires `ensureProfile` on first load; waiting for it gives every
    test the same known starting state.
    """
    with page.expect_response(
        lambda r: r.request.method == "POST" and is_server_fn(r.url, "ensureProfile")
    ) as first_visit:
        page.goto("/feed")
    assert first_visit.value.ok


@pytest.fixture
def member(api: APIRequestContext) -> Member:
    m = new_member()
    register(api, m)
    return m


@pytest.fixture
def member_page(page: Page, context: BrowserContext, member: Member, base_url: str) -> Page:
    """A browser page signed in as a fresh member whose starter closet is ready."""
    sign_in_context(context, base_url, member)
    open_as_new_member(page)
    return page


@pytest.fixture
def signed_in_session(
    browser: Browser, api: APIRequestContext, base_url: str, browser_context_args: dict
) -> Iterator[Callable[[], tuple[Member, Page]]]:
    """Factory for extra, independent members (for multi-user tests)."""
    contexts: list[BrowserContext] = []

    def create() -> tuple[Member, Page]:
        m = new_member()
        register(api, m)
        ctx = browser.new_context(**browser_context_args)
        contexts.append(ctx)
        sign_in_context(ctx, base_url, m)
        pg = ctx.new_page()
        open_as_new_member(pg)
        return m, pg

    yield create
    for ctx in contexts:
        ctx.close()


@pytest.fixture
def photo(tmp_path):
    from utils.test_data import make_photo

    return make_photo(tmp_path / "piece.png")
