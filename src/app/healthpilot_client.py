import os
import httpx
import logging
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("healthpilot")

HP_BASE = os.getenv("HEALTHPILOT_BASE", "https://healthpilot.local")
HP_API_KEY = os.getenv("HEALTHPILOT_API_KEY", "")
MOCK_HP = os.getenv("MOCK_HP", "true").lower() == "true"

class HealthpilotError(Exception):
    pass

class HealthpilotClient:
    def __init__(self, base_url: str = HP_BASE, api_key: str = HP_API_KEY, timeout: int = 10):
        self.base = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _mock_results(self, query: str, location: Optional[str], specialty: Optional[str]) -> List[dict]:
        # deterministic mocked set for local testing and CI
        return [
            {"id": "p1", "name": "Dr. Alice Smith", "score": 0.98, "distance_miles": 1.2, "specialty": specialty or "General"},
            {"id": "p2", "name": "Dr. Bob Lee", "score": 0.87, "distance_miles": 2.7, "specialty": specialty or "Cardiology"},
        ]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
           retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)))
    async def _call_search(self, q: str, location: Optional[str], specialty: Optional[str]):
        url = f"{self.base}/v1/providers/search"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        params = {"q": q}
        if location:
            params["loc"] = location
        if specialty:
            params["specialty"] = specialty
        logger.debug("Calling Healthpilot %s with params=%s", url, params)
        r = await self._client.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    async def search_providers(self, query: str, location: Optional[str] = None, specialty: Optional[str] = None) -> List[dict]:
        if MOCK_HP:
            logger.debug("Returning mock results for query=%s", query)
            return await self._mock_results(query, location, specialty)
        try:
            data = await self._call_search(query, location, specialty)
            return data.get("candidates", [])
        except Exception as e:
            logger.exception("Healthpilot call failed")
            raise HealthpilotError(str(e)) from e
