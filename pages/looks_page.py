from playwright.sync_api import Locator, Page, expect


class LooksPage:
    """/looks — saved outfits, with occasion and wear date."""

    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Looks", exact=True)
        self.empty_state = page.get_by_text("No looks yet. Build one in the fitting room.")

    def open(self) -> "LooksPage":
        self.page.goto("/looks")
        expect(self.heading).to_be_visible()
        return self

    def card(self, name: str) -> Locator:
        return self.page.locator("main li").filter(has=self.page.get_by_role("heading", name=name, exact=True))

    def drop(self, name: str) -> None:
        self.card(name).get_by_role("button", name="Drop").click()
