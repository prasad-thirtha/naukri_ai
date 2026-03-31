from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from src.common.utils.logger import log
from src.common.models.job_filters import JobFilters
from src.common.utils.job_exporter import JobExporter
from src.portals.naukri.api_client import NaukriApiClient
from src.portals.naukri.login import NaukriLogin
from src.portals.naukri.search_service import NaukriSearchService

load_dotenv()


with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="storage/browser_profile",
        headless=False,
        slow_mo=300,
    )

    page = context.new_page()

    # Existing login flow reused
    login = NaukriLogin(page)
    profile = login.login()

    api_client = NaukriApiClient(context)
    search_service = NaukriSearchService(api_client)

    filters = JobFilters(
        keyword="Automation Test Architect",
        location="Bangalore",
        experience_years=10,
        freshness_days=3
    )

    jobs = search_service.search(
        filters=filters,
        pages=2,
    )

    log(f"Found {len(jobs)} jobs")

    for job in jobs[:10]:
        log(
            f"{job['title']} | {job['company']} | "
            f"{job['location']} | {job['salary']}"
        )

    JobExporter.to_excel(
        jobs,
        "output/naukri_jobs.csv",
    )

    input("Press Enter to close...")
    context.close()