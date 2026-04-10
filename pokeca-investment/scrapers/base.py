import time
import random
import requests
from abc import ABC, abstractmethod
from config.settings import USER_AGENTS


class BaseScraper(ABC):
    def __init__(self, rate_limit_seconds=2.0):
        self.session = requests.Session()
        self.rate_limit = rate_limit_seconds
        self.last_request_time = 0
        self._update_headers()

    def _update_headers(self):
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

    def _wait(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _get(self, url, **kwargs):
        self._wait()
        try:
            resp = self.session.get(url, timeout=15, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            print(f"[Scraper] GET error: {e}")
            return None

    def _post(self, url, **kwargs):
        self._wait()
        try:
            resp = self.session.post(url, timeout=15, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            print(f"[Scraper] POST error: {e}")
            return None

    @abstractmethod
    def search(self, keyword, category, max_results=20):
        """
        Returns list of dicts:
        {name, price, price_type, source_id, image_url, observed_at, category}
        """
        pass
