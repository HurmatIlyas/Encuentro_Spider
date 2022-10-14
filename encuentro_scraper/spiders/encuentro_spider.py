import scrapy
import json

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from encuentro_scraper.items import EnuceuntroScraperItems


class EncuentroParseSpider:
    def parse(self, response):
        item = EnuceuntroScraperItems()
        raw_product = self.parse_raw_product(response)

        item['brand'] = self.product_brand(response)
        item['care'] = self.product_care(response)
        item['category'] = self.product_category(response)
        item['currency'] = self.product_currency(raw_product)
        item['description'] = self.product_description(response)
        item['image_urls'] = self.product_image_urls(response)
        item['lang'] = self.product_language(response)
        item['name'] = self.product_name(response)
        item['price'] = self.product_price(raw_product)
        item['retailer_sku'] = self.product_retailer_sku(raw_product)
        item['skus'] = self.product_skus(response, item['name'], item['price'])
        item['url'] = self.product_url(response)
        item['trail'] = self.product_trail(response)

        yield item

    def parse_raw_product(self, response):
        raw_product_details = response.css('input[id="pdp-gtm-data"]::attr(value)').get()
        return json.loads(raw_product_details)

    def product_brand(self, response):
        return response.css('body::attr(class)').get()

    def product_care(self, response):
        care = response.css('div[id="lavado"] p::text').get()
        if care:
            care = care.encode('ascii', 'ignore').decode()

            return care

    def product_category(self, response):
        category = [i.strip() for i in response.css('.breadcrumb-item ::text').getall()]
        category = list(set(category))
        if "" in category:
            category.remove("")

        return [x.encode('ascii', 'ignore').decode() for x in category]

    def product_currency(self, raw_product):
        return raw_product['ecommerce']['currencyCode']

    def product_description(self, response):
        description = [i.strip() for i in response.css('div.value.content::text').getall()]
        return [x.encode('ascii', 'ignore').decode() for x in description]

    def product_retailer_sku(self, raw_product):
        return raw_product['ecommerce']['detail']['products'][0]['id']

    def product_name(self, response):
        return response.css('h1.product-name::text').get().encode('ascii', 'ignore').decode()

    def product_language(self, response):
        return response.css('html::attr(lang)').get()

    def product_price(self, raw_product):
        return raw_product['ecommerce']['detail']['products'][0]['price']

    def product_color(self, response):
        return response.css('button[class="color-attribute"]::attr(data-color-name)').get()

    def product_image_urls(self, response):
        color = self.product_color(response)
        return {color: response.css('div.px-2 ::attr(src)').getall()}

    def product_skus(self, response, name, price):
        color = self.product_color(response)

        size = [i.strip() for i in response.css('select.select-size option::text').getall()]
        out_of_stock = response.css('select.select-size ::attr(value)').getall()
        for i in out_of_stock:
            if i == "null":
                availability = True
            else:
                availability = False

            skus = {color + "_" + i: {"color": color,
                                      "name": name,
                                      "out_of_stock": availability,
                                      "price": price,
                                      "size": i} for i in size}

        return skus

    def product_url(self, response):
        return response.url

    def product_trail(self, response):
        return [response.request.headers.get('Referer', None).decode()]


class Mixin:
    name = 'encuentro'
    allowed_domains = ['encuentromoda.com']
    category_id = 109
    category_name = ['BIENESTAR', 'BÁSICOS', 'NOVEDADES']
    start_url_t = 'https://www.encuentromoda.com/on/demandware.store/Sites-emo_pen-Site/es/Search-UpdateGrid?cgid=0{0}&start=0&sz=500'


class EncuentroCrawlSpider(Mixin, CrawlSpider):
    encuentro_parse_spider = EncuentroParseSpider()
    listings_css = 'li.dropdown-item.dropdown a'
    products_css = '.carousel-item a'

    rules = (
        Rule(LinkExtractor(restrict_css=listings_css)),
        Rule(LinkExtractor(restrict_css=products_css), callback=encuentro_parse_spider.parse),
    )

    def start_requests(self):
        requests = []
        for i in range(1, self.category_id):
            requests.append(scrapy.Request(
                url=self.start_url_t.format(i)))

        for i in self.category_name:
            requests.append(scrapy.Request(
                url=self.start_url_t.format(i)))

        return requests
