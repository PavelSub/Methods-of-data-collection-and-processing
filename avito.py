# -*- coding: utf-8 -*-

# Задание:
#
# Источник: https://www.avito.ru/ раздел недвижимость квартиры
#
# Извлекаем слуд параметры:
# - заголовок
# - url объявления
# - дата публикации
# - все фото
# - имя и ссылка на автора объявления
# - список параметров объявления из этого блока (https://www.dropbox.com/s/e1dho7iwom93fnb/%D0%A1%D0%BA%D1%80%D0%B8%D0%BD%D1%88%D0%BE%D1%82%202020-03-26%2022.11.42.png?dl=0)
# - телефон если получится
#
# обязательно использовать Item и ItemLoader

import scrapy
from scrapy.loader import ItemLoader
from blogparse.items import AvitoRealEstateItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/rossiya/kvartiry/']

    def parse(self, response):

        for page in range(1, int(response.xpath("//span[contains(@data-marker, 'page')]/text()").extract()[-1]) + 1):
            yield response.follow(f'{response.url}/prodam-ASgBAgICAUSSA8YQ?cd=1&p={page}', callback=self.parse)

        for flat in response.xpath("//a[contains(@class, 'snippet-link')]/@href").extract(): # обход ссылок объявлений
            yield response.follow(flat, callback=self.parse_flat)

    def parse_flat(self, response):
        item = ItemLoader(AvitoRealEstateItem(), response)
        item.add_value('url', response.url)
        item.add_xpath('title', "//span[contains(@class, 'title-info-title-text')]/text()")
        item.add_xpath('photos', "//div[contains(@class, 'gallery-img-frame')]/@data-url")
        item.add_xpath('pub_date', "//div[contains(@class, 'title-info-metadata-item-redesign')]/text()")
        item.add_xpath('author', "//div[contains(@class, 'seller-info-name')]/a")
        item.add_xpath('properties', "//li[contains(@class, 'item-params-list-item')]")
        item.add_value('tel', response.url)
        yield item.load_item()

