"""Spider Scrapy — Scraping des articles Bitcoin depuis CoinTelegraph."""

import re
from datetime import datetime, timedelta

import scrapy

from scraping.items import CryptoArticleItem


class CointelegraphSpider(scrapy.Spider):
    name = "cointelegraph"
    allowed_domains = ["cointelegraph.com"]
    start_urls = ["https://cointelegraph.com/tags/bitcoin"]

    custom_settings = {
        "FEEDS": {
            "data/scraped_articles.json": {
                "format": "json",
                "encoding": "utf-8",
                "overwrite": True,
            },
        },
    }

    def parse(self, response):
        for article in response.css("article"):
            link = article.css("a[data-title-link]")
            if not link:
                continue

            url = response.urljoin(link.attrib.get("href", ""))
            title = link.css("::text").get("").strip()

            if not title or len(title) < 20:
                continue

            raw_date = self._find_date_in_article(article)
            date_str = self._parse_date(raw_date)

            item = CryptoArticleItem()
            item["title"] = title
            item["date"] = date_str
            item["url"] = url
            item["category"] = self._extract_category(url)
            yield item

    def _find_date_in_article(self, article):
        """Parcourt les éléments .text-ct-ds-fg-muted et retourne celui qui ressemble à une date."""
        candidates = article.css(".text-ct-ds-fg-muted::text").getall()
        for text in candidates:
            text = text.strip()
            if re.search(r"(ago|yesterday|\b\w{3}\s+\d{1,2},\s*\d{4})", text, re.IGNORECASE):
                return text
        return ""

    def _parse_date(self, raw):
        """Convertit la date brute en format YYYY-MM-DD."""
        if not raw:
            return datetime.now().strftime("%Y-%m-%d")

        if re.search(r"\d+\s*(hour|min|sec)", raw, re.IGNORECASE):
            return datetime.now().strftime("%Y-%m-%d")

        if "yesterday" in raw.lower():
            return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        try:
            dt = datetime.strptime(raw, "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

        try:
            dt = datetime.strptime(raw, "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

        return datetime.now().strftime("%Y-%m-%d")

    def _extract_category(self, url):
        """Déduit la catégorie depuis l'URL."""
        if "/markets/" in url:
            return "Markets"
        elif "/news/" in url:
            return "News"
        elif "/analysis/" in url:
            return "Analysis"
        return "General"
