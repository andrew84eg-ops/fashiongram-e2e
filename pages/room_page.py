import re

from playwright.sync_api import Page, expect


class RoomPage:
    """/room — the fitting room where pieces are combined into a look."""

    def __init__(self, page: Page):
        self.page = page
        self.empty_board = page.get_by_text("Empty board")
        self.look_name = page.get_by_label("Look name")
        self.occasion = page.get_by_label("Occasion")
        self.wear_date = page.get_by_label("Wear date")
        self.save_button = page.get_by_role("button", name="Save this look")

    def open(self) -> "RoomPage":
        self.page.goto("/room")
        expect(self.page.get_by_role("heading", name="Build a look")).to_be_visible()
        return self

    def slot(self, label: str):
        # A filled slot is labelled with a trailing " ·", e.g. "Top ·".
        return self.page.get_by_role("button", name=re.compile(rf"^{re.escape(label)}( ·)?$"))

    def choose_slot(self, label: str) -> None:
        self.slot(label).click()

    def pick(self, slot_label: str, title: str) -> None:
        self.choose_slot(slot_label)
        self.page.get_by_role("button", name=title, exact=True).first.click()
        expect(self.slot(slot_label)).to_have_accessible_name(f"{slot_label} ·")

    def save(self, name: str = "", occasion: str = "", wear_date: str = "") -> None:
        if name:
            self.look_name.fill(name)
        if occasion:
            self.occasion.select_option(occasion)
        if wear_date:
            self.wear_date.fill(wear_date)
        self.save_button.click()
