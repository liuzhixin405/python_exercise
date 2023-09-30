import scrapy
from scrapy import Request, Selector
from spider2310.items import MovieItem
from scrapy.http import HtmlResponse

class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["movie.douban.com"]
    """start_urls = ["https://movie.douban.com/top250?start=0&filter="]"""

    def start_requests(self):
        for page in range(10):
            yield Request(url=f'https://movie.douban.com/top250?start={page *25}&filter=')
    def parse(self, response:HtmlResponse):
        select = Selector(response)
        list_items = select.css('#content > div > div.article > ol > li')
        for list_item in list_items:
            detail_url = list_item.css('div.info > div.hd > a::attr(href)').extract_first()
            movie_item = MovieItem()
            movie_item['title']=list_item.css('span.title::text').extract_first()
            movie_item['rank']=list_item.css('span.rating_num::text').extract_first()
            movie_item['subject']=list_item.css('span.inq::text').extract_first()


        hrefs_list =select.css('div.paginator > a::attr(href)')
        for href in hrefs_list:
            url = response.urljoin(href.extract())
            yield Request(url=url)
            