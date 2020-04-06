'''
Задача:
Пройти по произвольному списку пользователей (Username list), извлеч следующие данные:
- Подписчики пользователя
- Подписки пользователя
Сохранить в mongo структуры пользователей,
1 подписчик или Подписка 1 запись в БД
Для успеха Необходимо пройти авторизацию, узнать Хэш запроса для получения подписчиков,
узнать хэш для получения списка подписок.
Дополнительно:
Спарсить ленту постов пользователя, составить в монго коллекцию Постов с полной структурой.
Дополнительно 2
К каждому посту указать список лайкнувших и прокоментировавших.
'''
from copy import deepcopy
import scrapy
import re
import json
from urllib.parse import urljoin, urlencode


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    start_urls = ['https://instagram.com/']
    parse_users = ['realdonaldtrump', 'pycoders']
    variables = {"id": '',
                 "include_reel": True,
                 "fetch_mutual": False,
                 "first": 100,
                 }

    def __init__(self, logpass: tuple, **kwargs):
        self.login, self.pwd = logpass
        self.query_hashs = {'edge_followed_by': 'c76146de99bb02f6415203be841dd25a', 'edge_follow': 'd04b0a864b4b54837c0d870b0e77e076'}
        super().__init__(**kwargs)

    def parse(self, response):
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            login_url,
            method='POST',
            callback=self.main_parse,
            formdata={'username': self.login, 'password': self.pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def main_parse(self, response):
        j_resp = json.loads(response.text)
        if j_resp.get('authenticated'):
            for u_name in self.parse_users:
                yield response.follow(
                    urljoin(self.start_urls[0], u_name),
                    callback=self.parse_user,
                    cb_kwargs={'user_name': u_name}
                )

    def parse_user(self, response, user_name: str):
        user_id = self.fetch_user_id(response.text, user_name)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})
        for type_q, q_hash in self.query_hashs.items():
            yield response.follow(
                self.make_grapthql_url(user_vars, q_hash),
                callback=self.parse_followers,
                cb_kwargs={'user_vars': user_vars, 'user_name': user_name, 'type_q': type_q}
            )

    def parse_followers(self, response, user_vars, user_name, type_q):
        j_response = json.loads(response.text)
        if j_response['data']['user'][type_q]['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user'][type_q]['page_info']['end_cursor']})
            yield response.follow(
                self.make_grapthql_url(user_vars, self.query_hashs[type_q]),
                callback=self.parse_followers,
                cb_kwargs={'user_vars': user_vars, 'user_name': user_name, 'type_q': type_q}
            )

        followers = j_response['data']['user'][type_q]['edges']

        for follower in followers:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'user':
                        {'type_f': type_q, 'id': follower['node']['id'], 'username': follower['node']['username'],  'full_name': follower['node']['full_name']}}


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_grapthql_url(self, user_vars, q_hash):
        return f'{self.graphql_url}query_hash={q_hash}&{urlencode(user_vars)}'
