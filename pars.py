import requests
import json
import time
import re

url = 'https://5ka.ru/api/v2/special_offers/'
head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
cat_url = 'https://5ka.ru/api/v2/categories/'


def pars(url, par=None):
    res = []
    while url:
        resp = requests.get(url, headers=head, params=par) if par else requests.get(url, headers=head)
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


if __name__ == '__main__':
    cat = pars(cat_url)
    for c in cat:
        par = {'records_per_page': 20, 'categories': c['parent_group_code']}
        goods = pars(url, par)
        re_name = re.sub(r'[#%!@*/\"\n]', '', c['parent_group_name'])
        if len(goods) > 0: # не плодим лишние файлы для пустых категорий
            with open(f'D:/Methods of data collection and processing/les1/{re_name}.json', 'w') as file:
                file.write(json.dumps(goods))


