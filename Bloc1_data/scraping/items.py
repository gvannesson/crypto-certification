import scrapy


class CryptoArticleItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
