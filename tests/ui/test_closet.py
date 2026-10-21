"""Closet: the starter wardrobe, the insight line, and the filters."""

import pytest
from playwright.sync_api import Page, expect

from pages import ClosetPage
from utils.test_data import CATEGORY_LABELS, STARTER_CLOSET, starter_titles

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_new_member_receives_the_starter_closet(member_page: Page):
    closet = ClosetPage(member_page).open()

    expect(closet.summary).to_contain_text(f"{len(STARTER_CLOSET)} pieces.")
    closet.expect_titles(starter_titles())


def test_insight_line_reports_white_tops_and_missing_categories(member_page: Page):
    closet = ClosetPage(member_page).open()

    # Starter closet: an ivory and a cream top (the app counts both), and no bag.
    expect(closet.summary).to_contain_text("You already have 2 ivory/white tops")
    expect(closet.summary).to_contain_text("Missing bag.")


@pytest.mark.parametrize("category", list(CATEGORY_LABELS))
def test_category_filter_shows_only_that_category(member_page: Page, category: str):
    closet = ClosetPage(member_page).open()

    closet.filter_category(CATEGORY_LABELS[category])

    closet.expect_titles(starter_titles(category=category))


def test_category_and_colour_filters_combine(member_page: Page):
    closet = ClosetPage(member_page).open()

    closet.filter_category("Tops")
    closet.filter_color("Black")

    closet.expect_titles(starter_titles(category="top", color="black"))


def test_resetting_filters_restores_the_whole_closet(member_page: Page):
    closet = ClosetPage(member_page).open()
    closet.filter_category("Shoes")
    closet.filter_color("Navy")
    closet.expect_titles(set())

    closet.filter_category("All")
    closet.filter_color("Any color")

    closet.expect_titles(starter_titles())
