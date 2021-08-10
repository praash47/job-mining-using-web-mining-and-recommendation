import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy_tutorial.spiders.crawling_site import Site, NonAJAX

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

                yield self.scrape_job_urls(response, pag_na_website=pag_na_website, xpaths=xpaths)
            
            self.jobs = pag_na_website.jobs

    def scrape_job_urls(self, response, **kwargs):
        pag_na_website = kwargs.get('pag_na_website')
        xpaths = kwargs.get('xpaths')
        
        # Until last page is not reached, keep on getting jobs.
        pages_left = pag_na_website.site.pages.move_to_next_page()
        if pages_left:
            pag_na_website.get_jobs_from_xpath(xpaths, response)
            request = scrapy.Request(
                url=pag_na_website.site.pages.page_url,
                callback=self.scrape_job_urls,
            )
            request.cb_kwargs['pag_na_website'] = pag_na_website
            request.cb_kwargs['xpaths'] = xpaths

            return request

    def closed(self, reason):
        # Assign the jobs thus extracted.
        print(self.jobs)