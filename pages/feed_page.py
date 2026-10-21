from playwright.sync_api import Page, expect


class FeedPage:
    """/feed — public pieces from the members you follow."""

    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Following", exact=True)
        self.posts = page.locator("main article")
        self.empty_state = page.get_by_text("Follow members from Explore to fill this timeline.")

    def open(self) -> "FeedPage":
        self.page.goto("/feed")
        expect(self.heading).to_be_visible()
        return self
