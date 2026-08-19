import asyncio
import ipaddress
import logging
import re
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from app.core.config import settings

logger = logging.getLogger(__name__)

# Forbidden SSRF IP ranges
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_ssrf_safe_url(url: str) -> bool:
    """
    Validates URL to protect against SSRF attacks.
    Blocks private IP ranges, localhost, and invalid schemes.
    """
    if not settings.SSRF_PROTECTION_ENABLED:
        return True

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname_lower = hostname.lower()
        if hostname_lower in ("localhost", "127.0.0.1", "::1", "metadata.google.internal") or hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
            return False

        # Try resolving IP address
        try:
            ip_strs = socket.getaddrinfo(hostname, None)
            for item in ip_strs:
                ip_addr = ipaddress.ip_address(item[4][0])
                for blocked_net in BLOCKED_NETWORKS:
                    if ip_addr in blocked_net:
                        logger.warning(f"SSRF Blocked: URL {url} resolves to private IP {ip_addr}")
                        return False
        except socket.gaierror:
            # If hostname resolution fails, let httpx handle timeout or error
            pass

        return True
    except Exception as e:
        logger.warning(f"Error checking SSRF safety for URL {url}: {e}")
        return False


class SafeWebCrawler:
    """
    Anti-SSRF HTTP web crawler with HTML extraction and strict safety limits.
    """

    def __init__(
        self,
        max_concurrency: int = 5,
        timeout: float = 10.0,
        max_bytes: int = 2 * 1024 * 1024,  # 2MB max
    ):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.headers = {"User-Agent": settings.CRAWLER_USER_AGENT}

    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        if not is_ssrf_safe_url(url):
            logger.warning(f"Crawling rejected by SSRF protection for URL: {url}")
            return None

        async with self.semaphore:
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    max_redirects=3,
                    headers=self.headers,
                ) as client:
                    response = await client.get(url)
                    if response.status_code >= 400:
                        logger.debug(f"Fetch failed with status {response.status_code} for URL: {url}")
                        return None

                    # Content length check
                    content = response.content
                    if len(content) > self.max_bytes:
                        content = content[: self.max_bytes]

                    html_text = response.text
                    extracted = self._extract_metadata_and_text(html_text, str(response.url))
                    return extracted

            except Exception as e:
                logger.debug(f"Crawler error fetching {url}: {e}")
                return None

    def _extract_metadata_and_text(self, html: str, final_url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")

        # Strip script and style tags
        for script in soup(["script", "style", "noscript"]):
            script.extract()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Extract meta tags
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if desc_tag and desc_tag.get("content"):
            meta_desc = str(desc_tag.get("content")).strip()

        # Extract contact emails & phones using regex
        text_content = soup.get_text(separator=" ", strip=True)
        emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text_content)))
        phones = list(set(re.findall(r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", text_content)))

        # Extract social profile links
        social_links = []
        for a in soup.find_all("a", href=True):
            href = str(a.get("href", ""))
            if any(domain in href.lower() for domain in ["instagram.com", "linkedin.com", "twitter.com", "youtube.com", "facebook.com"]):
                social_links.append(href)

        return {
            "url": final_url,
            "title": title,
            "description": meta_desc,
            "text": text_content[:5000],  # cap text at 5000 chars
            "emails": emails[:5],
            "phones": phones[:5],
            "social_links": list(set(social_links))[:10],
        }
