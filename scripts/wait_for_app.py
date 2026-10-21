"""Wait until the app answers, then warm it up so the test run starts stable.

In dev mode Vite optimises dependencies the first time each page is opened and may
force a full reload mid-navigation. Visiting every route once, signed in, before the
suite runs keeps that one-off reload out of the real tests.

Usage: python scripts/wait_for_app.py [base_url]
"""

import sys
import time
import urllib.request
import uuid

from playwright.sync_api import sync_playwright

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
ROUTES = ["/feed", "/closet", "/add", "/room", "/looks", "/explore", "/shop", "/me"]


def wait_until_up(timeout_s: int = 180) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(BASE_URL, timeout=5) as response:
                if response.status == 200:
                    print(f"app is up at {BASE_URL}")
                    return
        except OSError:
            pass
        time.sleep(2)
    raise SystemExit(f"app did not come up at {BASE_URL} within {timeout_s}s")


def warm_up() -> None:
    email = f"warmup.{uuid.uuid4().hex[:10]}@example.test"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(base_url=BASE_URL)
        signup = context.request.post(
            "/api/auth/sign-up/email",
            data={"email": email, "password": "Test-pass-123", "name": "Warm Up"},
            headers={"Origin": BASE_URL},
        )
        assert signup.ok, signup.text()
        page = context.new_page()
        for _ in range(2):
            for route in ROUTES:
                try:
                    page.goto(route, wait_until="networkidle", timeout=60_000)
                except Exception as exc:  # a dev-server reload mid-visit is expected here
                    print(f"warm-up {route}: {exc.__class__.__name__}, retrying later")
        browser.close()
    print("warm-up done")


if __name__ == "__main__":
    wait_until_up()
    warm_up()
