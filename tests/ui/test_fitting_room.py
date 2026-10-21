"""Fitting room: build a look, save it to a date, drop it."""

import re

import pytest
from playwright.sync_api import Page, expect

from pages import LooksPage, RoomPage
from utils.test_data import unique_title

pytestmark = pytest.mark.ui


def test_empty_board_cannot_be_saved(member_page: Page):
    room = RoomPage(member_page).open()
    expect(room.empty_board).to_be_visible()

    room.save()

    expect(member_page.get_by_text("Pull at least one piece onto the board")).to_be_visible()
    expect(member_page).to_have_url(re.compile(r"/room$"))


@pytest.mark.smoke
def test_saved_look_appears_on_its_date(member_page: Page):
    name = unique_title("Tuesday downtown")
    room = RoomPage(member_page).open()

    room.pick("Top", "Ivory Silk Blouse")
    room.pick("Bottom", "Black Trousers")
    room.pick("Shoes", "Court Sneaker")
    room.save(name=name, occasion="Work", wear_date="2026-11-05")

    expect(member_page.get_by_text("Look saved")).to_be_visible()
    expect(member_page).to_have_url(re.compile(r"/looks$"))
    card = LooksPage(member_page).card(name)
    expect(card).to_contain_text("Work")
    expect(card).to_contain_text("Thursday 5 November")
    expect(card.locator("img")).to_have_count(3)


def test_look_without_a_name_is_named_after_its_pieces(member_page: Page):
    room = RoomPage(member_page).open()

    room.pick("Top", "Black Turtleneck")
    room.pick("Bottom", "Light Straight Jean")
    room.save()

    expect(LooksPage(member_page).card("Black Turtleneck · Light Straight Jean")).to_be_visible()


def test_dropping_a_look_removes_it(member_page: Page):
    name = unique_title("To be dropped")
    room = RoomPage(member_page).open()
    room.pick("Dress", "Black Slip Dress")
    room.save(name=name)
    looks = LooksPage(member_page)
    expect(looks.card(name)).to_be_visible()

    looks.drop(name)

    expect(looks.card(name)).to_have_count(0)
    expect(looks.empty_state).to_be_visible()
