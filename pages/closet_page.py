import re

from playwright.sync_api import Locator, Page, expect


class ClosetPage:
    """/closet — the member's wardrobe with category and colour filters."""

    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Closet", exact=True)
        self.summary = page.get_by_text(re.compile(r"^\d+ pieces\."))
        self.empty_state = page.get_by_text("Nothing in this drawer yet.")
        self.cards = page.locator("main a[href^='/item/']")
        self.add_button = page.get_by_role("button", name="Add")

    def open(self) -> "ClosetPage":
        self.page.goto("/closet")
        expect(self.heading).to_be_visible()
        expect(self.summary).to_be_visible()
        return self

    def filter_category(self, label: str) -> None:
        """Category chip: 'All', 'Tops', 'Bottoms', ..."""
        self.page.get_by_role("button", name=label, exact=True).click()

    def filter_color(self, label: str) -> None:
        """Colour swatch by its accessible name, or 'Any color' to reset."""
        self.page.get_by_role("button", name=label, exact=True).click()

    def card(self, title: str) -> Locator:
        return self.cards.filter(has=self.page.get_by_role("img", name=title, exact=True))

    def titles(self) -> set[str]:
        return {alt for alt in self.cards.locator("img").evaluate_all("els => els.map(e => e.alt)")}

    def expect_titles(self, expected: set[str]) -> None:
        """Wait for the grid to show exactly these pieces (or the empty state)."""
        if expected:
            expect(self.cards).to_have_count(len(expected))
            assert self.titles() == expected
        else:
            expect(self.empty_state).to_be_visible()
            expect(self.cards).to_have_count(0)
