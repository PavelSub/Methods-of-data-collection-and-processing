'''
Источник: https://habr.com/ru/top/weekly/

с использованием Scrapy и MongoDB

Необходимо обойти все странички популярного за неделю, ( delay рекомендую ставить около 600mc не меньше а лучше 1 секунду)

Извлекаем следующие данные:
- заголовок
- имя автора
- ссылка на страницу автора
- дата публикации
- список тегов
- список хабов
- количество комментариев
- дата парсинга (когда совершен парсинг)

после чего сохраняем данные в Монго.

Желательно потренировать использвоание xpath селекторов
'''

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
from blogparse.spiders.habr_news import HabrNewsSpider

if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    cr_process = CrawlerProcess(settings=craw_settings)
    cr_process.crawl(HabrNewsSpider)
    cr_process.start()
