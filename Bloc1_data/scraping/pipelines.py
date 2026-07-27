from scrapy.exceptions import DropItem


class DeduplicatePipeline:
    """Supprime les articles en doublon (même URL)."""

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        if item["url"] in self.seen_urls:
            raise DropItem(f"Doublon: {item['url']}")
        self.seen_urls.add(item["url"])
        return item
