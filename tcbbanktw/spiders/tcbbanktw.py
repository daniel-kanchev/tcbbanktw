import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tcbbanktw.items import Article


class tcbbanktwSpider(scrapy.Spider):
    name = 'tcbbanktw'
    start_urls = ['https://www.tcb-bank.com.tw/Pages/ViewMoreNews.aspx']
    allowed_domains = ['tcb-bank.com.tw']

    def parse(self, response):
        articles = response.xpath('//table[@id="viewmorenewsid_gvResult"]//td')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//strong//text()').getall()
        if not title:
            return
        else:
            title = " ".join(title)

        content = response.xpath('//div[@id="content"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
