from playwright.sync_api import Page, TimeoutError

from config.settings import NAUKRI_EMAIL, NAUKRI_PASSWORD
from src.common.utils.logger import log


class NaukriLogin:
    def __init__(self, page: Page):
        self.page = page

    def login(self):
        log("Opening Naukri login page")

        self.page.goto("https://www.naukri.com/nlogin/login")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3000)

        # Only perform login if still on login page
        if "login" in self.page.url.lower():
            # Some versions of the page use slightly different placeholders
            email_locator = self.page.locator(
                'input[placeholder*="Email ID"], input[placeholder*="Username"]'
            ).first

            password_locator = self.page.locator(
                'input[placeholder*="Password"]'
            ).first

            email_locator.wait_for(timeout=10000)
            email_locator.fill(NAUKRI_EMAIL)

            password_locator.fill(NAUKRI_PASSWORD)

            self.page.get_by_role("button", name="Login", exact=True).click()

            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(5000)

        # Open profile page to verify login
        # self.page.goto("https://www.naukri.com/mnjuser/profile")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(5000)

        try:
            name = self.page.locator("div.info__heading").get_attribute("title")

            role = (
                self.page.locator("div.info__sub-heading span[title]")
                .first
                .get_attribute("title")
            )
        except TimeoutError:
            raise Exception("Failed to verify Naukri profile after login")

        if not name or not role:
            raise Exception("Failed to verify Naukri profile")

        log(f"Logged in successfully into {name}, {role}")

        return {
            "name": name,
            "role": role
        }