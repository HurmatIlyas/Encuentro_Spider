import scrapy


class EnuceuntroScraperItems(scrapy.Item):
    brand = scrapy.Field()
    care = scrapy.Field()
    category = scrapy.Field()
    currency = scrapy.Field()
    description = scrapy.Field()
    gender = scrapy.Field()
    image_urls = scrapy.Field()
    lang = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    retailer_sku = scrapy.Field()
    skus = scrapy.Field()
    trail = scrapy.Field()
    url = scrapy.Field()
    url_original = scrapy.Field()
    start_url = scrapy.Field()