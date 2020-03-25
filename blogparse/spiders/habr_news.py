# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime


class HabrNewsSpider(scrapy.Spider):
    name = 'habr_news'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly']

    def parse(self, response):
        # for page in response.xpath("//a[contains(@class, 'toggle-menu__item-link_pagination')]/@href").extract():
        for page in response.xpath("//a[contains(@id, 'next_page')]/@href").extract():
            yield response.follow(page, callback=self.parse)

        for new in response.xpath("//a[contains(@class, 'post__title_link')]/@href").extract():
            yield response.follow(new, callback=self.news_parse)

    def news_parse(self, response):
        data = {
            'article_url': response.url,
            'title': response.xpath("//h1/span/text()").extract_first(),
            'author': {'author_name': response.xpath("//span[contains(@class, 'user-info__nickname')]/text()").extract_first(),
                       'author_url': response.xpath("//a[contains(@class, 'post__user-info')]/@href").extract_first()},
            'pub_date': datetime.strptime(response.xpath("//span[contains(@class, 'post__time')]/@data-time_published").extract_first(), "%Y-%m-%dT%H:%MZ"),
            'tags': response.xpath("//ul[contains(@class, 'js-post-tags')]/li/a/text()").extract(),
            'hubs': [t.strip() for t in response.xpath("//ul[contains(@class, 'js-post-hubs')]/li/a/text()").extract()],
            'com_quantity': int(response.xpath("//span[contains(@id, 'comments_count')]/text()").extract_first()),
            'parse_date': datetime.now()
        }
        yield data
