import json
from typing import Dict, List, Optional

from playwright.sync_api import BrowserContext, Page


class NaukriApiClient:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.page: Page = context.new_page()

        self.app_id: Optional[str] = None
        self.system_id: Optional[str] = None
        self.client_id: str = "d3skt0p"

        self.authorization: Optional[str] = None
        self.gid: Optional[str] = None
        self.nkparam: Optional[str] = None

    def bootstrap_headers(self):
        """
        Perform one real search on Naukri and capture all request headers
        needed for later API searches.
        """
        captured: Dict[str, Optional[str]] = {}

        def handle_request(request):
            if "/jobapi/v3/search" not in request.url:
                return

            headers = request.headers

            captured["appid"] = headers.get("appid")
            captured["systemid"] = headers.get("systemid")
            captured["clientid"] = headers.get("clientid", "d3skt0p")
            captured["authorization"] = headers.get("authorization")
            captured["gid"] = headers.get("gid")
            captured["nkparam"] = headers.get("nkparam")

        self.page.on("request", handle_request)

        self.page.goto("https://www.naukri.com/jobs-in-india")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)

        # Open search panel if needed
        try:
            self.page.locator("#ni-gnb-searchbar").click(timeout=3000)
        except Exception:
            pass

        keyword_input = self.page.locator(
            'input[placeholder="Enter keyword / designation / companies"]'
        ).first

        location_input = self.page.locator(
            'input[placeholder="Enter location"]'
        ).first

        keyword_input.fill("qa lead")
        location_input.fill("bangalore")

        location_input.press("Enter")

        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(5000)

        self.app_id = captured.get("appid")
        self.system_id = captured.get("systemid")
        self.client_id = captured.get("clientid", "d3skt0p")
        self.authorization = captured.get("authorization")
        self.gid = captured.get("gid")
        self.nkparam = captured.get("nkparam")

        missing = []

        if not self.app_id:
            missing.append("appid")
        if not self.system_id:
            missing.append("systemid")
        if not self.authorization:
            missing.append("authorization")
        if not self.gid:
            missing.append("gid")
        if not self.nkparam:
            missing.append("nkparam")

        if missing:
            raise Exception(
                "Failed to capture required Naukri headers.\n"
                f"Missing: {missing}\n"
                f"Captured: {captured}"
            )

    def search_jobs(self, payload: Dict) -> Dict:
        """
        Execute Naukri search using the real logged-in browser session.
        """
        if (
            not self.app_id
            or not self.system_id
            or not self.authorization
            or not self.gid
            or not self.nkparam
        ):
            self.bootstrap_headers()

        result = self.page.evaluate(
            """
            async ({
                payload,
                appId,
                systemId,
                clientId,
                authorization,
                gid,
                nkparam
            }) => {
                const query = new URLSearchParams();

                for (const [key, value] of Object.entries(payload)) {
                    if (
                        value !== undefined &&
                        value !== null &&
                        value !== ""
                    ) {
                        query.append(key, String(value));
                    }
                }

                const url =
                    "https://www.naukri.com/jobapi/v3/search?" +
                    query.toString();

                const response = await fetch(url, {
                    method: "GET",
                    credentials: "include",
                    headers: {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "appid": appId,
                        "systemid": systemId,
                        "clientid": clientId,
                        "authorization": authorization,
                        "gid": gid,
                        "nkparam": nkparam
                    }
                });

                const text = await response.text();

                return {
                    ok: response.ok,
                    status: response.status,
                    body: text,
                    url: url
                };
            }
            """,
            {
                "payload": payload,
                "appId": self.app_id,
                "systemId": self.system_id,
                "clientId": self.client_id,
                "authorization": self.authorization,
                "gid": self.gid,
                "nkparam": self.nkparam,
            },
        )

        if not result["ok"]:
            raise Exception(
                f"Naukri API search failed: {result['status']}\n"
                f"URL: {result['url']}\n"
                f"Response:\n{result['body']}"
            )

        try:
            return json.loads(result["body"])
        except Exception:
            raise Exception(
                "Unable to parse Naukri API response.\n"
                f"URL: {result['url']}\n"
                f"Body:\n{result['body']}"
            )

    def extract_jobs(self, response_json: Dict) -> List[Dict]:
        jobs: List[Dict] = []

        for job in response_json.get("jobDetails", []):
            placeholders = job.get("placeholders", [])

            jobs.append(
                {
                    "title": job.get("title", ""),
                    "company": job.get("companyName", ""),
                    "experience": (
                        placeholders[0].get("label", "")
                        if len(placeholders) > 0
                        else ""
                    ),
                    "location": (
                        placeholders[1].get("label", "")
                        if len(placeholders) > 1
                        else ""
                    ),
                    "salary": (
                        placeholders[2].get("label", "")
                        if len(placeholders) > 2
                        else ""
                    ),
                    "posted": job.get("footerPlaceholderLabel", ""),
                    "job_id": job.get("jobId", ""),
                    "url": job.get("jdURL", ""),
                    "description": job.get("jobDescription", ""),
                }
            )

        return jobs