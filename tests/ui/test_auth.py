"""Sign-up, sign-in and route protection through the real login form."""

import re

import pytest
from playwright.sync_api import Page, expect

from pages import LoginPage
from utils.test_data import Member, new_member

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_landing_page_introduces_the_product(page: Page):
    page.goto("/")

    expect(page).to_have_title("FashionGram")
    expect(page.get_by_role("heading", name="Stop buying the white blouse you already own.")).to_be_visible()
    expect(page.get_by_role("link", name="Open your closet")).to_be_visible()


@pytest.mark.parametrize("path", ["/feed", "/closet", "/add", "/room", "/looks", "/me"])
def test_private_pages_redirect_anonymous_visitors_to_login(page: Page, path: str):
    page.goto(path)

    expect(page).to_have_url(re.compile(r"/login"))


@pytest.mark.smoke
def test_new_member_can_sign_up_through_the_form(page: Page):
    m = new_member(name="Form Member")
    login = LoginPage(page).open()

    login.sign_up(m.name, m.email, m.password)

    expect(page).to_have_url(re.compile(r"/feed$"))
    expect(page.get_by_role("heading", name="Following", exact=True)).to_be_visible()


def test_existing_member_can_sign_in_through_the_form(page: Page, member: Member):
    login = LoginPage(page).open()

    login.sign_in(member.email, member.password)

    expect(page).to_have_url(re.compile(r"/feed$"))


def test_wrong_password_shows_an_error_and_stays_on_login(page: Page, member: Member):
    login = LoginPage(page).open()

    login.sign_in(member.email, "Wrong-pass-999")

    expect(login.error).to_have_text("Invalid email or password")
    expect(page).to_have_url(re.compile(r"/login$"))


def test_password_field_enforces_minimum_length(page: Page):
    login = LoginPage(page).open()
    login.switch_to_sign_up.click()

    login.email.fill(new_member().email)
    login.password.fill("short")
    login.create_button.click()

    # Blocked by the browser's own validation (minLength=8) before any request is sent.
    is_valid = login.password.evaluate("el => el.checkValidity()")
    assert is_valid is False
    expect(page).to_have_url(re.compile(r"/login$"))
