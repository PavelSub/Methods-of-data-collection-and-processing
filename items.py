# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Compose
from scrapy.selector import Selector
from datetime import datetime, timedelta
import locale
import requests
from json import loads

locale.setlocale(locale.LC_ALL, '')

class BlogparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def clean_photos(val):
    if val[:2] == '//':
        return f'http:{val}'
    return val


def form_au(val=None):
    if val:
        soup = Selector(text=val[0])
        return {'name': soup.xpath('//a/text()').get().replace('\n', '').strip(),
                'url': f'https://www.avito.ru{soup.xpath("//a/@href").get()}'}
    return val


def form_prop(val=None):
    if val:
        soup = Selector(text=val)
        return {soup.xpath('//li/span/text()').get().replace(':', '').strip(): soup.xpath('//li/text()')[1].get().strip()}
    return val


def comp_props(val=None):
    if val:
        return {list(i.keys())[0]: list(i.values())[0] for i in val}
    return val


def form_date(val=None):
    if val:
        d = datetime.now()
        if val[0].find('сегодня') > 0:
            return str(d.date())
        elif val[0].find('вчера') > 0:
            return str(d.date() - timedelta(days=1))
        else:
            return str(datetime.strptime(f'{d.timetuple()[0]} {val[0][:val[0].find(" в ")].strip()}', "%Y %d %B"))
    return val


def get_phone(val=None):
    if val:
       urinum = loads(requests.get(f'https://m.avito.ru/api/1/items/{val[0].split("_")[-1]}/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir',
                        headers={'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1'}
                        ).text)['result']['action']['uri']
       return urinum[urinum.find('B') + 1:]
    return val


class AvitoRealEstateItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    pub_date = scrapy.Field(input_processor=Compose(form_date), output_processor=TakeFirst())
    author = scrapy.Field(input_processor=Compose(form_au), output_processor=TakeFirst())  # name and url
    properties = scrapy.Field(input_processor=MapCompose(form_prop), output_processor=Compose(comp_props))
    photos = scrapy.Field(input_processor=MapCompose(clean_photos))
    tel = scrapy.Field(input_processor=Compose(get_phone), output_processor=TakeFirst())
