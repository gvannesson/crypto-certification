BOT_NAME = "scraping"

SPIDER_MODULES = ["scraping.spiders"]
NEWSPIDER_MODULE = "scraping.spiders"

USER_AGENT = "CryptoCertification-Bot/1.0 (+https://github.com/gvannesson-aiko/crypto-certification)"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 1

ITEM_PIPELINES = {
    "scraping.pipelines.DeduplicatePipeline": 100,
}

LOG_LEVEL = "INFO"
