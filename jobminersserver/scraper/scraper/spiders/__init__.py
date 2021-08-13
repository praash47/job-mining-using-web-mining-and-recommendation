"""
This file initializes the scrapy scraper. The flow of scraper starts
with the parse function that is present below.
"""
import scrapy
from scrapy.linkextractors import LinkExtractor
import sys
sys.path.append('/home/aasis/Documents/jobminersserver')
import json
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
import websockets
from asgiref.sync import sync_to_async

from scraper.spiders.crawling_site import Site, NonAJAX
from requestutils.request import Request
from checkers.models import JobURL, JobWebsiteURL


class JobURLSpider(scrapy.Spider):
    """
    This spider is used to crawl job URLs out of website urls. This is a subclass Spider
    object.
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

        Keyworded Arguments
        -------------------
        search_page_url: str
            Search page url of the site to perform scraping on
        """
        # Scrapy's link extractor object
        self.link_extractor = LinkExtractor()
        
        # This is a master site object that remains in the JobURL object.
        self.site = Site(
            search_page_url=kwargs.get('search_page_url')
        )
        
        self.start_urls = [self.site.search_page_url]
        self.jobs = {}

    def parse(self, response):
        """
        Use to extract out job URLs that are present in a website that is assign
        to the self.jobs object. The response argument in this function is automatically
        provided with HTML response by the spider object.

        After this function is invoked and until it's completion, self.jobs is populated
        with jobs dictionary of format.
        { "job_name": job_url }
        """
        # Extract out links present in the page
        links_in_page = self.link_extractor.extract_links(response)

        # Check if Non AJAX based paginated website
        if self.site.pages.has_pages(links_in_page):
            # Create a non-ajax object out of the site.
            # pag_na_website refers to paginated non ajax variable.
            pag_na_website = NonAJAX(response, links_in_page, self.site)
            # Determine if the site is crawlable.
            if pag_na_website.is_crawlable():
                # If determined as crawlable, then extracting out xpaths 
                # for job URL in the website.
                xpaths = pag_na_website.xpaths.get_xpaths(links_in_page)
                
                # Yield the scrape_job_urls so as to extend request from this function to the
                # web.
                yield self.scrape_job_urls(response, na_website=pag_na_website, xpaths=xpaths)
            
            self.jobs = pag_na_website.jobs

        # For non ajax based non paginated website
        else:
            na_website = NonAJAX(response, links_in_page, self.site, paginated=False)
            xpaths = na_website.xpaths.get_xpaths(links_in_page)

            if xpaths: self.scrape_job_urls(response, na_website=na_website, xpaths=xpaths)

            self.jobs = na_website.jobs

    def scrape_job_urls(self, response, **kwargs):
        """
        Scrape job urls does as specified by the name. It scrapes out the job urls on the basis
        of xpaths that are provided to it.

        In case of paginated non ajax based websites, it also traverses to next page and also
        yields the request. This is also a callback function in case of such situation.

        This function acts as a wrapper for extracting the jobs. This handles the request and 
        paginated traversal.

        Keyworded Arguments
        -------------------
        na_website: NonAJAX object
            the instance of non ajax object to scrape out job urls from
        xpaths: list of str
            list of xpath strings of two job websites that are got from the website.

        Returns
        -------
        request: scrapy.Request
            Scrapy request is returned in case of paginated non ajax websites.
        """
        na_website = kwargs.get('na_website')
        xpaths = kwargs.get('xpaths')
        
        # if this is true, this means that the site has pages.
        if na_website.site.pages.last_page:
            pag_na_website = na_website
            # Until last page is not reached, keep on getting jobs.
            # On reaching the last page, move_to_next_page() returns
            # false.
            pages_left = pag_na_website.site.pages.move_to_next_page()
            if pages_left:
                # Jobs are actually scraped out using this.
                pag_na_website.get_jobs_from_xpath(xpaths, response)

                # Next page's request so that next page is requested.
                request = scrapy.Request(
                    url=pag_na_website.site.pages.page_url,
                    callback=self.scrape_job_urls,
                )
                # pass call back keyworded arguments to the callback
                # function
                request.cb_kwargs['na_website'] = pag_na_website
                request.cb_kwargs['xpaths'] = xpaths

                # after this is returned, the yield on the outside the
                # performs the actual request to the site.
                return request

        else:
            # This is for non-paginated ajax based websites

            # TODO: jobsdynamics type website: there are multiple job titles mentioned
            # in the same ad, that contradicts with our architecture.
            # - Alljobnepal where links is placed inside the company's name, WHAT???
            # yes, they even do it!
            na_website.get_jobs_from_xpath(xpaths, response)

    async def closed(self, reason):
        """
        This function is executed after the scraping of the whole website is taken place.

        Currently, this is handled manually, and next time, it can be handled using item
        pipelines, which are the more powerful features of the scrapy for the same task.
        """
        # Put the jobs into database thus extracted.
        website = Request(self.site.search_page_url)
        # frankly, the request is not initialized here for the request, rather it is initialized
        # here for getting the homepage.
        homepage = website.get_only_homepage_based() + '/'
        print(homepage)
        # get the django models JobWebsite object from the database
        website = await sync_to_async(JobWebsiteURL.objects.get)(url=homepage)  # sync_to_async so as to call
        # an asynchronous function from inside a synchronous function

        # Connecting to the websocket.
        ws_url = "ws://127.0.0.1:8000/ws/"
        websocket = await websockets.connect(ws_url)
        for title, url in self.jobs.items():
            # Process the job URL so as to make situations like getting only the
            # partial url without homepage like on in merojob.com can be avoided.
            url = self.check_or_make_url_complete(url, homepage)

            # to save job ur into the database
            job_url = JobURL(website=website, title=title, url=url)
            await sync_to_async(job_url.save)()
        await websocket.send(json.dumps({
            'action': 'one_website_scrape_completed',
            'jobs': self.jobs,
            'site': homepage
        }))

    def check_or_make_url_complete(self, url, homepage):
        """
        This function checks the job url and makes the url complete or
        with the homepage if it is not present in the homepage. The example
        of this case is merojob.com.

        Parameters
        ----------
        url: str
            job url to check or make url complete
        homepage: str
            homepage url of that job url

        Returns
        -------
        url: str
            homepage + url if the url doesn't contain homepage otherwise only the url
            itself.
        """
        if homepage in url:
            return url

        # If url is like this /homepage-manager/ , make it homepage-manager/
        if url[0] == '/': url = url[1:]
        
        return homepage + url