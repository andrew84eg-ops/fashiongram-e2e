from playwright.sync_api import Locator, Page, expect


class LoginPage:
    """/login — email sign-in and sign-up (one form, two modes)."""

    def __init__(self, page: Page):
        self.page = page
        self.email = page.get_by_label("Email")
        self.password = page.get_by_label("Password")
        self.name = page.get_by_label("Name")
        self.sign_in_button = page.get_by_role("button", name="Sign in")
        self.create_button = page.get_by_role("button", name="Create account")
        self.switch_to_sign_up = page.get_by_role("button", name="New? Create an account")

    def open(self) -> "LoginPage":
        self.page.goto("/login")
        expect(self.page.get_by_role("heading", name="Enter your closet.")).to_be_visible()
        return self

    def sign_up(self, name: str, email: str, password: str) -> None:
        self.switch_to_sign_up.click()
        self.name.fill(name)
        self.email.fill(email)
        self.password.fill(password)
        self.create_button.click()

    def sign_in(self, email: str, password: str) -> None:
        self.email.fill(email)
        self.password.fill(password)
        self.sign_in_button.click()

    @property
    def error(self) -> Locator:
        return self.page.locator("form p.text-danger")
