from typing import Optional

import requests

from event_pipeline.models import FetchedDocument, ProjectConfig, SourceConfig


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


class Fetcher:
    def __init__(self, project: ProjectConfig):
        self.project = project
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def fetch(self, source: SourceConfig) -> FetchedDocument:
        if source.requires_browser:
            browser_result = self._fetch_with_browser(source)
            if browser_result is not None:
                return browser_result
        return self._fetch_with_requests(source)

    def _fetch_with_requests(self, source: SourceConfig) -> FetchedDocument:
        response = self.session.get(source.url, timeout=25)
        response.raise_for_status()
        return FetchedDocument(
            source=source,
            url=source.url,
            final_url=response.url,
            html=response.text,
            content_type=response.headers.get("content-type", "text/html"),
            status_code=response.status_code,
        )

    def _fetch_with_browser(self, source: SourceConfig) -> Optional[FetchedDocument]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return None

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(source.url, wait_until="networkidle", timeout=self.project.browser_timeout_seconds * 1000)
            html = page.content()
            final_url = page.url
            browser.close()

        return FetchedDocument(
            source=source,
            url=source.url,
            final_url=final_url,
            html=html,
            content_type="text/html",
            status_code=200,
        )
