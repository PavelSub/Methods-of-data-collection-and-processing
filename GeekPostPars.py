'''
Обойти список статей, с использованием библиотеки BS4
Сохранить полученые данные в виде json файлов:
Отдельный файл для тегов, в котором хранится сам тег, ссылка на тег, и список ссылок на записи в блоге с этип тегом. Пример:

# file tags.json
{
    "tag_name": {'url': "", 'posts': ['url_post', ]}
}

Отдельно для каждой записи в блоге создать json файл с именем равным url данной записи, и полями заголовка, ссылки на изображение, url, данных на автора статьи, и списко тегов пример структуры:
# file url_post.json
{
    'url': 'post_url',
    'image': 'image_url',
    'title': 'Заголовок',
    'writer': {'name': 'writer_name',
               'url': 'full_writer_url'
               },
    'tags': [{'tag_name':'tag_url'}, ]
}
'''

import requests
import bs4
from json import dumps
from time import sleep
from random import randint


class GeekHtmlPosts:
    def __init__(self):
        self.__base_url = 'https://geekbrains.ru'
        self.__url_start = 'https://geekbrains.ru/posts'
        self.__header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.posts = []

    def __get_posts_url(self) -> []:
        p_url = []
        [p_url.extend(self.__get_post_url(soap)) for soap in self.__get_page()]
        return p_url

    def __get_page(self):
        url = self.__url_start
        while url:
            soap = bs4.BeautifulSoup(requests.get(url, headers=self.__header).text, 'lxml')
            yield soap
            url = self.__get_next_page(soap)
            sleep(randint(1, 9)/10)

    def __get_next_page(self, soap: bs4.BeautifulSoup) -> str:
        a = soap.find("a", text="›")
        return f'{self.__base_url}{a["href"]}' if a else None

    def __get_post_url(self, soap: bs4.BeautifulSoup) -> []:
        return [f'{self.__base_url}{i["href"]}' for i in soap.select(".post-item__title")]

    def get_posts_data(self):
        p_struct = {}
        for url in self.__get_posts_url():
            soap = bs4.BeautifulSoup(requests.get(url, headers=self.__header).text, 'lxml')
            p_struct['url'] = url
            p_struct['image'] = soap.select_one('img')['src']
            p_struct['title'] = soap.select_one('.blogpost-title').text
            p_struct['writer'] = {'name': soap.find(attrs={"itemprop": "author"}).text, 'url': f'{self.__base_url}{soap.select_one(".col-md-5 a")["href"]}'}
            p_struct['tags'] = {itm.text: f'{self.__base_url}{itm["href"]}' for itm in soap.select('a.small')}
            self.posts.append(p_struct.copy())
            sleep(randint(1, 9)/10)

    def save_posts(self):
        for p in self.posts:
            with open(f'D:/Methods of data collection and processing/les2/{p["url"].replace("/","_").replace("https:__", "").replace(".", "")}.json', 'w') as file:
                file.write(dumps(p))

    def save_tags(self):
        tags = {}
        for p in self.posts:
            for k, v in p['tags'].items():
                if not tags.get(k):
                    tags[k] = {'url': v, 'posts': [p['url']]}
                else:
                    tags[k]['posts'].append(p['url'])
        with open(f'D:/Methods of data collection and processing/les2/tags.json', 'w') as file:
            file.write(dumps(tags))


if __name__ == '__main__':
    geek_post = GeekHtmlPosts()
    geek_post.get_posts_data()
    geek_post.save_posts()
    geek_post.save_tags()



