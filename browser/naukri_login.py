from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL = os.getenv("NAUKRI_EMAIL")
PASSWORD = os.getenv("NAUKRI_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="storage/browser_profile",
        headless=False,
        slow_mo=500
    )

    page = browser.new_page()

    try:
        # Open login page
        page.goto("https://www.naukri.com/nlogin/login")
        page.wait_for_timeout(3000)

        # Login only if session is not already active
        if "login" in page.url.lower():
            page.get_by_placeholder("Enter Email ID / Username").fill(EMAIL)
            page.get_by_placeholder("Enter Password").fill(PASSWORD)

            page.get_by_role("button", name="Login", exact=True).click()

            # Wait for login/navigation to complete
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

        # Open profile page
        # page.goto("https://www.naukri.com/mnjuser/profile")
        page.wait_for_timeout(5000)

        # Capture screenshot
        page.screenshot(path="screenshots/profile_page.png", full_page=True)

        # Read name and designation from profile
        name = page.locator("div.info__heading").get_attribute("title")

        role = (
            page.locator("div.info__sub-heading span[title]")
            .first
            .get_attribute("title")
        )

        # Validate profile loaded correctly
        if not name or not role:
            raise Exception("Could not fetch profile name or role")

        print(f"Logged in successfully into {name}, {role}")

    except Exception as e:
        print(f"Error during login/profile verification: {e}")
        page.screenshot(path="screenshots/login_failure.png", full_page=True)

    input("Press Enter to close browser...")
    browser.close()