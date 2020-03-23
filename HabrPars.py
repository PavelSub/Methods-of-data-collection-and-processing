'''
Дом задание:
Источник https://habr.com/ru/

задача:
Обойти ленту популярного за неделю

сохранить данные в базы данных (Mongo, SQL)
необходимые данные:
- Загаловок статьи
- Url статьи
- количество комментариев в статье
- дата и время публикации
- автор (название и url)
- авторы комментариев (название и url)

для Mongo:
создать коллекцию и все можно хранить в одной коллекции

для SQL
создать дополнительную таблицу для автора и автора комментариев и наладить связи
'''
import requests
import bs4
from datetime import datetime
from time import sleep
from random import randint
import pymongo
import sqlsave


class HabrNewsWeekly:
    def __init__(self):
        self.__base_url = 'https://habr.com'
        self.__url_start = 'https://habr.com/ru/top/weekly/'
        self.__header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.news = []
        self.db_mongo_au = 'mongodb+srv://Admin:0000000cluster0-ujirt.mongodb.net/test?retryWrites=true&w=majority'

    def __get_posts_url(self) -> []:
        p_url = []
        [p_url.extend(self.__get_news_url(soap)) for soap in self.__get_page()]
        return p_url

    def __get_page(self):
        url = self.__url_start
        while url:
            soap = bs4.BeautifulSoup(requests.get(url, headers=self.__header).text, 'lxml')
            yield soap
            url = self.__get_next_page(soap)
            sleep(randint(1, 9)/10)

    def __get_next_page(self, soap: bs4.BeautifulSoup) -> str:
        a = soap.find("a", attrs={"id": "next_page"})
        return f'{self.__base_url}{a["href"]}' if a else None

    def __get_news_url(self, soap: bs4.BeautifulSoup) -> []:
        return [i["href"] for i in soap.select(".post__title_link")]

    def get_news_data(self):
        p_struct = {}
        for url in self.__get_posts_url():
            soap = bs4.BeautifulSoup(requests.get(url, headers=self.__header).text, 'lxml')
            p_struct['title'] = soap.select_one('.post__title-text').text
            p_struct['url'] = url
            p_struct['com_quantity'] = int(soap.select_one('.comments-section__head-counter').text)
            p_struct['pub_time'] = datetime.strptime(soap.select_one('.post__time')['data-time_published'], "%Y-%m-%dT%H:%MZ")
            p_struct['author'] = self.__find_author(soap)
            p_struct['com_authors'] = self.__find_com_authors(soap)
            self.news.append(p_struct.copy())
            sleep(randint(1, 9)/10)

    def __find_author(self, soap):
        au_info = soap.select_one('a.user-info__nickname')
        return {'name': au_info.text, 'url': au_info['href']}

    def __find_com_authors(self, soap):
        com_au = [{'name': i['data-user-login'], 'url': i['href']} for i in soap.select('.comment__head a.user-info_inline')]
        return list({v['name']: v for v in com_au}.values())

    # def __get_news_dt(self, soap):
    #     dt = soap.select_one('.post__time')['data-time_published'].split('T')
    #     return {'date': dt[0], 'time': dt[1].replace('Z', '')}

    def save_at_mongo_db(self):
        client = pymongo.MongoClient(self.db_mongo_au)
        db = client['habr_weekly_news']
        db['news'].insert_many(self.news)

    def save_at_sql_db(self):
        sqlsave.save_at_db(self.news)


if __name__ == '__main__':
    habr_news = HabrNewsWeekly()
    habr_news.get_news_data()
    habr_news.save_at_mongo_db()
    habr_news.save_at_sql_db()



