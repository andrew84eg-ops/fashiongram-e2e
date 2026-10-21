"""Adding a photographed piece to the closet."""

import re

import pytest
from playwright.sync_api import Page, expect

from pages import AddItemPage, ClosetPage
from utils.test_data import STARTER_CLOSET, unique_title

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_member_can_add_a_photographed_piece(member_page: Page, photo):
    title = unique_title("Olive Linen Shirt")
    add = AddItemPage(member_page).open()

    add.upload_photo(photo)
    add.title.fill(title)
    add.choose_category("top")
    add.choose_color("Olive")
    add.size.fill("M")
    add.submit()

    expect(member_page.get_by_text("Hung in the closet")).to_be_visible()
    expect(member_page).to_have_url(re.compile(r"/closet$"))
    closet = ClosetPage(member_page)
    expect(closet.summary).to_contain_text(f"{len(STARTER_CLOSET) + 1} pieces.")
    expect(closet.card(title)).to_be_visible()


def test_piece_without_a_photo_is_not_saved(member_page: Page):
    add = AddItemPage(member_page).open()

    add.title.fill(unique_title("No Photo"))
    add.submit()

    expect(member_page.get_by_text("Add a photograph first")).to_be_visible()
    expect(member_page).to_have_url(re.compile(r"/add$"))
    expect(ClosetPage(member_page).open().summary).to_contain_text(f"{len(STARTER_CLOSET)} pieces.")


def test_title_is_required(member_page: Page, photo):
    add = AddItemPage(member_page).open()
    add.upload_photo(photo)

    add.submit()

    assert add.title.evaluate("el => el.validity.valueMissing") is True
    expect(member_page).to_have_url(re.compile(r"/add$"))


def test_warns_before_buying_another_white_top(member_page: Page):
    """The product's core promise: the closet remembers the white blouse you own."""
    add = AddItemPage(member_page).open()

    add.choose_category("top")
    add.choose_color("White")

    expect(add.duplicate_warning).to_contain_text("Ivory Silk Blouse")


def test_no_duplicate_warning_for_a_colour_you_do_not_own(member_page: Page):
    add = AddItemPage(member_page).open()

    add.choose_category("top")
    add.choose_color("White")
    expect(add.duplicate_warning).to_be_visible()
    add.choose_color("Terracotta")

    expect(add.duplicate_warning).to_be_hidden()
