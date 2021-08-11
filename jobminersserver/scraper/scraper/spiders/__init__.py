import scrapy
from scrapy.linkextractors import LinkExtractor
from scraper.spiders.crawling_site import Site, NonAJAX

import sys
sys.path.append('/home/aasis/Documents/jobminersserver')

import json

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

import websockets

from requestutils.request import Request
from checkers.models import JobURL, JobWebsiteURL

from asgiref.sync import sync_to_async

class JobURLSpider(scrapy.Spider):
    """
    This spider is used to crawl job URLs out of website urls.
    """
    name = "CrawlSite"

    # start_urls = [
    #     # 'https://merojob.com/search/?q=',
    #     # 'https://jobstalent.com.np/search-page/',
    #     # 'https://www.kumarijob.com/search?keywords=',
    #     # 'https://globaljob.com.np/Search/jobSearch',
    #     # 'https://froxjob.com/search/result?keywords=&cityzone=',
    #     # 'http://jobkhoji.com/job/search?query=+',
    #     # 'https://kathmandujobs.com/jobs/search/',
    #     # 'https://careersinnepal.com/?s='
    # ]

    def __init__(self, **kwargs):
        """
        A link extractor and site object is initialized with search page url
        coming from kwargs.
        """
        self.link_extractor = LinkExtractor()
        self.site = Site(
            search_page_url=kwargs.get('search_page_url')
        )
        self.initiator_ws = kwargs.get('ws')

        self.start_urls = [self.site.search_page_url]
        self.jobs = {}

    def parse(self, response):
        """
        Use to extract out job URLs that are present in a website.
        """
        # Extract out links present in the page
        links_in_page = self.link_extractor.extract_links(response)

        # Check if Non AJAX based paginated website
        if self.site.pages.has_pages(links_in_page):
            # Create a non-ajax object out of the site.
            pag_na_website = NonAJAX(response, links_in_page, self.site)
            # Determine if the site is crawlable.
            if pag_na_website.is_crawlable():
                # If determined as crawlable, then extracting out xpaths 
                # for job URL in the website.
                xpaths = pag_na_website.xpaths.get_xpaths(links_in_page)

                yield self.scrape_job_urls(response, na_website=pag_na_website, xpaths=xpaths)
            
            self.jobs = pag_na_website.jobs

        # For non ajax based non paginated website
        else:
            na_website = NonAJAX(response, links_in_page, self.site, paginated=False)
            xpaths = na_website.xpaths.get_xpaths(links_in_page)

            if xpaths: yield self.scrape_job_urls(response, na_website=na_website, xpaths=xpaths)

            self.jobs = na_website.jobs

    def scrape_job_urls(self, response, **kwargs):
        na_website = kwargs.get('na_website')
        xpaths = kwargs.get('xpaths')
        
        if na_website.site.pages.last_page:
            pag_na_website = na_website
            # Until last page is not reached, keep on getting jobs.
            pages_left = pag_na_website.site.pages.move_to_next_page()
            if pages_left:
                pag_na_website.get_jobs_from_xpath(xpaths, response)
                request = scrapy.Request(
                    url=pag_na_website.site.pages.page_url,
                    callback=self.scrape_job_urls,
                )
                request.cb_kwargs['na_website'] = pag_na_website
                request.cb_kwargs['xpaths'] = xpaths

                return request

        else:
            # TODO: jobsdynamics type website: there are multiple job titles mentioned
            # in the same ad, that contradicts with our architecture.
            # - Alljobnepal where links is placed inside the company's name, WHAT???
            # yes, they even do it!
            na_website.get_jobs_from_xpath(xpaths, response)

    async def closed(self, reason):
        # Put the jobs into database thus extracted.
        website = Request(self.site.search_page_url)
        homepage = website.get_only_homepage_based() + '/'
        print(homepage)
        website = await sync_to_async(JobWebsiteURL.objects.get)(url=homepage)

        ws_url = "ws://127.0.0.1:8000/ws/"
        websocket = await websockets.connect(ws_url)
        for title, url in self.jobs.items():
            # Process the job URL
            url = self.check_or_make_url_complete(url, homepage)

            job_url = JobURL(website=website, title=title, url=url)
            await sync_to_async(job_url.save)()
        await websocket.send(json.dumps({
            'action': 'one_website_scrape_completed',
            'jobs': self.jobs,
        }))

    def check_or_make_url_complete(self, url, homepage):
        if homepage in url:
            return url

        return homepage + url