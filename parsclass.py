import requests
import json
import time
import re


class X5pars():
    def __init__(self, url):
        self.url = url
        self.cat_url = 'https://5ka.ru/api/v2/categories/'
        self.head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.cat = self.pars(self.cat_url)
        self.goods = []

    def pars(self, url, par=None):
        res = []
        while url:
            resp = requests.get(url, headers=self.head, params=par) if par else requests.get(url, headers=self.head)
            par = None
            data = resp.json()
            if isinstance(data, dict):
                res.extend(data.get('results'))
                url = data.get('next')
            elif isinstance(data, list):
                return data
            else:
                print('Ошибка получения данных')
                return None
            time.sleep(1)
        return res

    def get_goods_by_cat(self, par=None):
        for c in self.cat:
            par = {'records_per_page': 20, 'categories': c['parent_group_code']}
            goods = self.pars(self.url, par)
            re_name = re.sub(r'[#%!@*/\"\n]', '', c['parent_group_name'])
            self.goods.extend([{re_name: goods}])

    def save_data(self, path):
        for g in self.goods:
            with open(f'{path}/{list(g.keys())[0]}.json', 'w') as file:
                file.write(json.dumps(g))


if __name__ == '__main__':
    Pars = X5pars('https://5ka.ru/api/v2/special_offers/')
    Pars.get_goods_by_cat()
    Pars.save_data('D:/Methods of data collection and processing/les1')


