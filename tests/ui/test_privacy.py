"""Two members, one app: private pieces must stay private."""

import re

import pytest
from playwright.sync_api import Page, expect

from pages import AddItemPage
from utils.test_data import unique_title

pytestmark = pytest.mark.ui


def _add_piece(page: Page, photo, title: str, public: bool) -> str:
    """Add a piece and return its item id."""
    add = AddItemPage(page).open()
    add.upload_photo(photo)
    add.title.fill(title)
    add.choose_category("accessory")
    add.choose_color("Burgundy")
    if public:
        add.public_toggle.check()
    add.submit()
    expect(page).to_have_url(re.compile(r"/closet$"))
    href = page.locator("main a[href^='/item/']").filter(
        has=page.get_by_role("img", name=title, exact=True)
    ).get_attribute("href")
    return href.rsplit("/", 1)[-1]


def test_private_piece_is_hidden_from_other_members(signed_in_session, photo):
    _, owner = signed_in_session()
    _, visitor = signed_in_session()
    title = unique_title("Private Scarf")
    item_id = _add_piece(owner, photo, title, public=False)

    visitor.goto("/explore")
    expect(visitor.get_by_role("heading", name="Explore")).to_be_visible()
    expect(visitor.get_by_role("img", name=title)).to_have_count(0)

    visitor.goto(f"/item/{item_id}")
    expect(visitor.get_by_text("This piece is private or gone.")).to_be_visible()


def test_public_piece_is_visible_to_other_members(signed_in_session, photo):
    _, owner = signed_in_session()
    _, visitor = signed_in_session()
    title = unique_title("Public Scarf")
    item_id = _add_piece(owner, photo, title, public=True)

    visitor.goto("/explore")
    expect(visitor.get_by_role("img", name=title)).to_be_visible()

    visitor.goto(f"/item/{item_id}")
    expect(visitor.get_by_role("heading", name=title)).to_be_visible()
