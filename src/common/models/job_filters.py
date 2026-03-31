from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time


@dataclass
class JobFilters:
    keyword: str
    location: Optional[str] = None
    experience_years: Optional[int] = None
    freshness_days: Optional[int] = None
    extra_filters: Dict[str, Any] = field(default_factory=dict)

    def to_api_payload(self, page_no: int = 1) -> Dict[str, Any]:
        keyword = self.keyword.strip().lower()
        location = (self.location or "").strip().lower()

        payload: Dict[str, Any] = {
            "noOfResults": 20,
            "urlType": "search_by_key_loc",
            "searchType": "adv",
            "location": location,
            "keyword": keyword,
            "sort": "p",
            "pageNo": page_no,
            "k": keyword,
            "l": location,
            "nignbevent_src": "jobsearchDeskGNB",
            "seoKey": f"{keyword.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}",
            "src": "cluster",
            "latLong": "",
            "sid": str(int(time.time() * 1000)),
        }

        if self.experience_years is not None:
            payload["experience"] = self.experience_years

        if self.freshness_days is not None:
            payload["jobAge"] = self.freshness_days

        payload.update(self.extra_filters)

        return payload