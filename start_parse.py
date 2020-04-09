from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
# from blogparse.spiders.habr_news import HabrNewsSpider
# from blogparse.spiders.avito import AvitoSpider
# from blogparse.spiders.instagram import InstagramSpider
from blogparse.spiders.zillow import ZillowSpider
import log_pass


if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    cr_process = CrawlerProcess(settings=craw_settings)
    # cr_process.crawl(HabrNewsSpider)
    # cr_process.crawl(AvitoSpider)
    # cr_process.crawl(InstagramSpider, logpass=(log_pass.INSTA_LOGIN, log_pass.INSTA_PWD))
    cr_process.crawl(ZillowSpider)
    cr_process.start()
