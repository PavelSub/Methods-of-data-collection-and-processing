# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class BlogparsePipeline(object):
    def __init__(self):
        client = MongoClient("mongodb+srv://Admin:000000@cluster0-ujirt.mongodb.net/test?retryWrites=true&w=majority")
        self.db = client['habr_news']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item
