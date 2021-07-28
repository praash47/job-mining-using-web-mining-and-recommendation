from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from msedge.selenium_tools import Edge, EdgeOptions
import scrapy
from scrapy.linkextractors import LinkExtractor
import json
from scrapy_tutorial.spiders.crawling_site import Site

class SiteSpider(scrapy.Spider):
    name = "CrawlSite"
    ESTD_TOTAL_JOBS_IN_PAGE = 150
    FILE_NAME_TO_EXTRACT_JOBS_TO = "jobURLskathmandujobs2.txt"

    start_urls = [
        # 'https://merojob.com/search/?q=',
        # 'https://jobstalent.com.np/search-page/',
        # 'https://globaljob.com.np/Search/jobSearch',
        # 'https://froxjob.com/search/result?keywords=&cityzone=',
        # 'https://kathmandujobs.com/jobs/search/'
    ]

    def __init__(self, **kwargs):
        self.link_extractor = LinkExtractor()
        self.site = Site(
            search_page_url=kwargs.get('search_page_url')
        )
        self.start_urls = [self.site.search_page_url]
        self.jobs = {}

    def parse(self, response):
        links_in_page = self.link_extractor.extract_links(response)

        # Xpath is got, everything proceeds normally as expected, if False
        # then, there is some request by the xpath module.
        xpath_got, xpath_request = self.site.get_xpaths(response, links_in_page)

        if not xpath_got:
            if xpath_request == "NOT_POSSIBLE": return
            elif xpath_request == "PAGE_TRAVERSAL_REQUEST":
                self.request_next_page()
                xpath_got, xpath_request = self.site.get_xpaths(response, links_in_page)
        
        try: self.get_jobs_from_xpath(response)
        except: pass

    
    def get_jobs_from_xpath(self, response):
        path = self.site.xpath.copy()
        init = path[self.var_index][:-2]
        for i in range(1, ESTD_TOTAL_JOBS_IN_PAGE):
            path[self.var_index] = init + str(i) + ']'
            element_text = response.xpath('/' + "/".join(path) + '//text()').get()
            element_href = response.xpath('/' + "/".join(path[:-1]) + '//@href').get()
            if element_text and element_href:
                self.jobs[element_text] = element_href

    def request_next_page(self):
        if self.sites.search_step: self.site.pages.curr_page += self.site.search_step
        else: self.site.pages.curr_page += 1

        if self.site.pages.curr_page <= self.site.pages.max_page:
            yield scrapy.Request(
                url=self.search_page_url + str(self.site.pages.curr_page),
                callback=self.parse
            )

        url = self.site.search_page_url + str(self.site.pages.curr_page)
        yield scrapy.Request(
            url=url,
            callback=self.parse
        )

    def closed(self, reason):
        pass
        # with open(FILE_NAME_TO_EXTRACT_JOBS_TO, 'w') as file_to_write_to:
        #     json.dump(self.jobs, file_to_write_to)