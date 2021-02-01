import scrapy
from scrapy.spiders import CrawlSpider, Request
from scrapy.loader import ItemLoader
from googlesearch import search
import re
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC 

from email_collection.items import EmailCollectorItem

class email_collector(CrawlSpider):

    name = 'email_collector'

    def __init__(self, *args, **kwargs):
        super(email_collector, self).__init__(*args, **kwargs)
        self.email_list = []
        self.query = 'realestate agent newcastle'

    def start_requests(self):
        for results in search(self.query, num=3, pause=2):
            yield SeleniumRequest(
                url=results,
                callback=self.parse_item,
                wait_until=EC.presence_of_element_located(
                    (By.TAG_NAME, "html")
                ),
                dont_filter=False
            )

    def parse_item(self, response):
        
        l = ItemLoader(item=EmailCollectorItem(), response=response)

        EMAIL_REGEX = r'[A-Za-z0-9._+]+@[A-Za-z]+.(com|org|edu|net)'

        if re.search(EMAIL_REGEX, str(response.text)) is None:
            return
        else:
            emails = re.finditer(EMAIL_REGEX, str(response.text))
            
            for email in emails:
                self.email_list.append(email.group())

            unique_emails = set(self.email_list)
            self.email_list.clear()

            for email in unique_emails:
                l.add_value('email', email)
                l.add_value('url', response.url)
                return l.load_item()

            
        
