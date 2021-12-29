from re import search
from scrapy.linkextractors import LinkExtractor

from .site import Site, NonAJAX
from requestutils.request import Request

from checkers.models import JobWebsite
from jobdetailsextractor.models import Job

import logging

logger = logging.getLogger('interactor')
mainlogger = logging.getLogger('main')

# Decorator & Generator
def call_if_non_ajax_based(func):
    def is_non_ajax_based(self, **kwargs):
        na_website = None
        links_in_page = kwargs.get('links_in_page')     
        # Check if Non AJAX based paginated website
        if self.site.pages.has_pages(links_in_page):
            # Create a non-ajax object out of the site.
            # pag_na_website refers to paginated non ajax variable.
            pag_na_website = NonAJAX(self.response, links_in_page, self.site)
            # Determine if the site is crawlable.
            if pag_na_website.is_crawlable():
                mainlogger.info(f'{self.site.search_page_url} is found to be crawlable.')
                na_website = pag_na_website
                return func(na_website=pag_na_website, obj=self, **kwargs)
        # For non ajax based non paginated website
        else:
            na_website = NonAJAX(self.response, links_in_page, self.site, paginated=False)

        return func(na_website=na_website, obj=self, **kwargs)
    return is_non_ajax_based
    
class TitleExtractor:
    def __init__(self, search_url):
        """
        A link extractor and site object is initialized with search page url
        coming from kwargs.

        Keyworded Arguments
        -------------------
        search_page_url: str
            Search page url of the site to perform scraping on
        """
        logger.info(f'Title Extraction object created for {search_url}')
        mainlogger.info(f'Title Extraction object created for {search_url}')
        # Scrapy's link extractor object
        self._link_extractor = LinkExtractor()
        
        # This is a master site object that remains in the JobURL object.
        self.site = Site(search_page_url=search_url)
        logger.info('Site, Xpather object created')

        self.response = self._mock_scrapy_response(search_url)
        logger.info(f'Mocked Scrapy Response: {self.response}')
        
        self.jobs = {}


    def extract_title_xpath(self):
        links_in_page = self._link_extractor.extract_links(self.response)

        title_xpath = self.get_title_xpath(links_in_page=links_in_page)

        return title_xpath


    @call_if_non_ajax_based
    def get_title_xpath(na_website, **kwargs):
        links_in_page = kwargs.get('links_in_page')
        xpath = na_website.xpaths.get_xpath(links_in_page)
        
        mainlogger.info(f'Title Xpath: {xpath}')
        return xpath
    
    def extract_jobs_from_title_xpath(self, title_xpath):
        links_in_page = self._link_extractor.extract_links(self.response)
        self._scrape_job_urls(
            response=self.response,
            title_xpath=title_xpath,
            links_in_page=links_in_page
        )

    def _mock_scrapy_response(self, search_url):
        request = Request(search_url)
        text = request.request_html()
        request.filter_unnecessary_tags()
        tree = request.get_html_tree()
        root = tree.getroot()
        selector = MockSelector(root)

        return MockResponse(search_url, text, selector, tree)

    def _check_or_make_url_complete(self, url, homepage):
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

    @call_if_non_ajax_based
    def _scrape_job_urls(**kwargs):
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
        title_xpath = kwargs.get('title_xpath')
        response = kwargs.get('response')
        obj = kwargs.get('obj')

        logger.info(f'Scraping jobs in page: {na_website.site.pages.page_url}')

        # if this is true, this means that the site has pages.
        if na_website.site.pages.last_page:
            pag_na_website = na_website
            # Until last page is not reached, keep on getting jobs.
            # On reaching the last page, move_to_next_page() returns
            # false.
            logger.info(f'Checking if further pages left.')
            pages_left = pag_na_website.site.pages.move_to_next_page()
            if pages_left:
                # Jobs are actually scraped out using this.
                pag_na_website.get_jobs_for_page(title_xpath, response)

                new_response = obj._mock_scrapy_response(pag_na_website.site.pages.page_url)
                obj._scrape_job_urls(response=new_response, na_website=pag_na_website, title_xpath=title_xpath)

        else:
            # This is for non-paginated ajax based websites

            # TODO: jobsdynamics type website: there are multiple job titles mentioned
            # in the same ad, that contradicts with our architecture.
            # - Alljobnepal where links is placed inside the company's name, WHAT???
            # yes, they even do it!
            na_website.get_jobs_for_page(title_xpath, response)
        
        obj.jobs = na_website.jobs
        logger.info(f'got jobs: {obj.jobs}')

    def store_into_database(self):
        """
        This function is executed after the scraping of the whole website is taken place.

        Currently, this is handled manually, and next time, it can be handled using item
        pipelines, which are the more powerful features of the scrapy for the same task.
        """

        # get the django models JobWebsite object from the database
        website = JobWebsite.objects.get(search_url=self.site.search_page_url)  # sync_to_async so as to call
        # an asynchronous function from inside a synchronous function

        for title, url in self.jobs.items():
            # Process the job URL so as to make situations like getting only the
            # partial url without homepage like on in merojob.com can be avoided.
            url = self._check_or_make_url_complete(url, website.url)

            # to save job ur into the database
            job = Job(website=website, title=title, url=url)
            job.save()


class MockResponse:
    def __init__(self, url, text, selector, tree, encoding='utf-8'):
        self.url = url
        self.encoding = encoding
        self.selector = selector
        self.text = text
        self.tree = tree

class MockSelector:
    def __init__(self, root) -> None:
        self.root = root