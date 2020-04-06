# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from log_pass import MONGO_LOGIN, MONGO_PWD


class BlogparsePipeline(object):
    def __init__(self):
        client = MongoClient(f"mongodb+srv://{MONGO_LOGIN}:{MONGO_PWD}@cluster0-ujirt.mongodb.net/test?retryWrites=true&w=majority")
        self.db = client['parse']

    def process_item(self, item, spider):
        if spider.name == 'instagram':
            collection = self.db[item['type_d']]
        else:
            collection = self.db[spider.name]
        collection.insert_one(item)
        return item


# class ImgPipeLine(ImagesPipeline):
#     def get_media_requests(self, item, info):
#
#         if item.get('photos'):
#             for img_url in item['photos']:
#                 try:
#                     yield scrapy.Request(img_url)
#                 except Exception as e:
#                     pass
#
#     def item_completed(self, results, item, info):
#
#         if results:
#             item['photos'] = [itm[1] for itm in results]
#         return item


