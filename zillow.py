# -*- coding: utf-8 -*-
'''
Источник данных https://www.zillow.com

выбираем любой город по вкусу.

Задача обойти все объявления в городе, извлеч из объявлений след поля:

photos (список всех изображений, + их все надо скачивать в Piplines)
Title
url
price (цена в долларах)
адрес (находится в подзаголовке)
sqft (это что то вроде квадратных метров только квадратных футов, площадь)
Для работы вам потребуется связка selenium + scrapy

'''
import scrapy
from blogparse.items import ZillowItem
from scrapy.loader import ItemLoader

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/homes/NY_rb/']
    browser = webdriver.Chrome()

    def parse(self, response):

        for page in response.xpath("//nav[contains(@aria-label, 'Pagination')]/ul/li/a/@href"):
            yield response.follow(page, callback=self.parse)

        for flat in response.xpath("//ul[contains(@class, 'photo-cards')]/li/article/div[contains(@class, 'list-card-info')]/a/@href"):
            yield response.follow(flat, callback=self.parse_flat)

    def parse_flat(self, response):
        self.browser.get(response.url)
        photos_pl = self.browser.find_element_by_xpath("//div[contains(@class, 'ds-media-col')]")
        photos_len = len(self.get_photo_list())
        while True:
            for i in range(7):
                photos_pl.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
            tmp_len = len(self.get_photo_list())
            if tmp_len == photos_len:
                break
            photos_len = tmp_len

        item = ItemLoader(ZillowItem(), response)
        item.add_value('url', response.url)
        #item.add_xpath('title', "//span[contains(@class, 'title-info-title-text')]/text()")
        item.add_value('photos', [i.get_attrebute('srcset').split(' ')[-2] for i in self.get_photo_list()])
        item.add_value('price', response.xpath("//span[contains(@class, 'ds-value')]/text()").extract_first())
        item.add_xpath('address', "//h1[contains(@class, 'ds-address-container')]/span/text()")
        item.add_value('sqft', response.xpath("//span[contains(@class, 'ds-bed-bath-living-area')]/span/text()").extract()[-3])
        yield item.load_item()

    def get_photo_list(self):
        return self.browser.find_elements_by_xpath('//ul[contains(@class, "media-stream")]/li/picture/source[contains(@type, "image/jpeg")]')

