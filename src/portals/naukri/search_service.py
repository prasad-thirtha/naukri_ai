from typing import Dict, List

from src.common.models.job_filters import JobFilters
from src.portals.naukri.api_client import NaukriApiClient


class NaukriSearchService:
    def __init__(self, api_client: NaukriApiClient):
        self.api_client = api_client

    def search(
        self,
        filters: JobFilters,
        pages: int = 1,
    ) -> List[Dict]:
        all_jobs: List[Dict] = []

        for page in range(1, pages + 1):
            payload = filters.to_api_payload(page_no=page)

            response = self.api_client.search_jobs(payload)
            jobs = self.api_client.extract_jobs(response)

            all_jobs.extend(jobs)

        return all_jobs