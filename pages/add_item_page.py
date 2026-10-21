from pathlib import Path

from playwright.sync_api import Page, expect


class AddItemPage:
    """/add — photograph a piece and hang it in the closet."""

    def __init__(self, page: Page):
        self.page = page
        self.photo_input = page.locator("input[type='file']")
        self.title = page.get_by_label("Title")
        self.notes = page.get_by_label("Notes")
        self.category = page.get_by_label("Category")
        self.brand = page.get_by_label("Brand")
        self.season = page.get_by_label("Season")
        self.size = page.get_by_label("Size")
        self.public_toggle = page.get_by_label("Public on the timeline")
        self.submit_button = page.get_by_role("button", name="Hang it up")
        self.duplicate_warning = page.get_by_text("You already have")

    def open(self) -> "AddItemPage":
        self.page.goto("/add")
        expect(self.page.get_by_role("heading", name="Add item")).to_be_visible()
        return self

    def upload_photo(self, path: Path) -> None:
        self.photo_input.set_input_files(str(path))
        # The app compresses the photo, then swaps the placeholder for a preview.
        expect(self.page.get_by_text("Tap to photograph or choose from the roll")).to_be_hidden()

    def choose_category(self, category_id: str) -> None:
        self.category.select_option(category_id)

    def choose_color(self, label: str) -> None:
        self.page.get_by_role("button", name=label, exact=True).click()

    def submit(self) -> None:
        self.submit_button.click()
