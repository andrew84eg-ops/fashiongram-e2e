"""Confirmed defects, written as tests of the CORRECT behaviour.

Each test is marked `xfail(strict=True)`: today it fails, which CI reports as an
expected failure. When a fix lands the test starts passing, strict mode turns that
into a failure, and the marker must be removed — so a fix can never go unnoticed.
Full reports (steps, expected vs actual, root cause): BUG_REPORTS.md
"""

import pytest
from playwright.sync_api import Page, Route, expect

from conftest import sign_in_context
from pages import AddItemPage, FeedPage
from utils.server_fn import is_server_fn
from utils.test_data import Member

pytestmark = [pytest.mark.ui, pytest.mark.known_defect]


@pytest.mark.xfail(reason="FG-002: new member's feed stays empty after first-visit setup finishes")
def test_feed_fills_once_first_visit_setup_completes(page: Page, context, member: Member, base_url: str):
    """Deterministic reproduction of a race that shows up intermittently (2 of 5 runs).

    The first-visit setup call (`ensureProfile`) is held back until the feed has
    rendered, simulating a slow server. Correct behaviour: once setup finishes, the
    feed shows the followed members' public pieces without a manual reload.
    """
    sign_in_context(context, base_url, member)
    held: list[Route] = []

    def hold_setup(route: Route) -> None:
        if route.request.method == "POST":
            held.append(route)
        else:
            route.continue_()

    page.route(lambda url: is_server_fn(url, "ensureProfile"), hold_setup)
    feed = FeedPage(page).open()
    expect(feed.empty_state).to_be_visible()  # setup not done yet: empty is fine here

    with page.expect_response(lambda r: is_server_fn(r.url, "ensureProfile")):
        for route in held:
            route.continue_()

    expect(feed.posts.first).to_be_visible(timeout=10_000)


@pytest.mark.xfail(reason="FG-003: white-top warning stays on screen after switching to another category")
def test_duplicate_warning_clears_when_category_changes(member_page: Page):
    add = AddItemPage(member_page).open()
    add.choose_category("top")
    add.choose_color("White")
    expect(add.duplicate_warning).to_be_visible()

    add.choose_category("shoes")

    expect(add.duplicate_warning).to_be_hidden(timeout=5_000)


@pytest.mark.xfail(reason="FG-004: warning never appears if the colour is chosen before the category")
def test_duplicate_warning_does_not_depend_on_input_order(member_page: Page):
    add = AddItemPage(member_page).open()
    add.choose_category("dress")
    add.choose_color("White")
    expect(add.duplicate_warning).to_be_hidden()

    add.choose_category("top")

    expect(add.duplicate_warning).to_be_visible(timeout=5_000)


@pytest.mark.xfail(reason="FG-005: insights count cream tops as white, the duplicate warning does not")
def test_cream_top_rule_is_consistent(member_page: Page):
    """The closet summary counts Cream Cashmere as a white top; the add form should agree."""
    add = AddItemPage(member_page).open()
    add.choose_category("top")

    add.choose_color("Cream")

    expect(add.duplicate_warning).to_contain_text("Cream Cashmere", timeout=5_000)
