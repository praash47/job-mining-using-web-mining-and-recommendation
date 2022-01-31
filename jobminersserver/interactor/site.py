"""
This submodule consists of all the classes required to abstract a job website as a 'site' and perform operations such as getting xpaths of the job title on search page and getting jobs from a page after supply of title xpath.

Classes
-------
Site()
    Our abstraction of any site (maybe non AJAX or AJAX based both, but non AJAX based as of now)
NonAJAX()
    NonAJAX is the abstraction of the procedures to get the job URL and title from the nonAJAX based websites.
"""
import logging

from lxml.html import HtmlElement

from .paginator import Paginator
from .xpather import Xpather

from .exceptions import NoTwoMatchingTitles

logger = logging.getLogger('interactor')
mainlogger = logging.getLogger('main')


class Site:
    def __init__(self, search_page_url):
        """
        A site object for storing top level crawling site related info. The top level
        crawling site related info here stands for the search page url of the site and
        the paginator object responsible for handling the pagination of the site.
        """
        # Search Page Initializations
        self.search_page_url = search_page_url

        # Paginator Initialization
        self.pages = Paginator()


class NonAJAX:
    def __init__(self, response, links, site, paginated=True):
        """
        A representation of a Non-AJAX website. This object is designed to perform
        job scraping for specifically non ajax based scenarios.

        Parameters
        ----------
        response: str
            response html of the non ajax page
        links: LinkExtractor
            scrapy link extractor object
        site: Site
            site object of the site that holds the search page url
        paginated: boolean, default=True
            specifies whether the NonAJAX

        Methods
        -------
        is_crawlable(): determines whether the site is crawlable or not on the basis of
        it's xpaths
        get_jobs_from_xpaths: populates the self.jobs object on the basis of xpaths that
        are extracted from the page.
        """
        self.response = response
        self.links = links
        self.site = site
        self.paginated = paginated


        # This estimates the number of jobs per page. This is
        # just an arbitrary number and maynot be also not enough
        # in certain scenarios.
        self._ESTD_JOBS_IN_PAGE = 150

        # xpath initialization
        self.xpaths = Xpather(response, site, paginated)

        self.jobs = {}

    def is_crawlable(self):
        """
        Returns true if xpaths can be got from the links of the first page.

        Returns
        -------
        boolean
            True if crawlable else raises Exceptions
        
        Raises
        ------
        NoTwoMatchingTitles
            No two matching titles found
        """
        # Try to get xpath
        if self.xpaths.get_xpath(
                self.links):
            logger.info(
                f'Xpath got in first page in {self.site.search_page_url}')
            return True  # If getting xpath is succesful, then it is crawlable.

        logger.error(
            f'Xpath not got in first page in {self.site.search_page_url}')

        raise NoTwoMatchingTitles(self.site.search_page_url)

    def get_jobs_for_page(self, xpath, response):
        """
        This function extracts jobs on the basis of xpaths by finding the variable div. It
        works on the basis of principle that there is a varying same structured div in the
        page that has the same structure as others that holds the job related information
        and job url.

        Parameters
        ----------
        xpaths: list of str
            list of xpaths of the two jobs in the page
        response: str
            html response of the site
        """
        logger.info('Getting jobs for the page')
        xpath_init, xpath_end = xpath.split('|')[0], xpath.split('|')[1]
        
        for i in range(1, self._ESTD_JOBS_IN_PAGE):
            try:
                xpath = xpath_init + str(i) + xpath_end
                element = response.tree.xpath(xpath)[0]
                if type(element) is not HtmlElement:
                    continue
                # Get the text and href i.e. url and save into the self.jobs
                element_text = element.text_content()
                element_href = element.get('href')
                if element_text and element_href:
                    if not self._check_if_job_already_in_database(
                        element_text,
                        element_href
                    ):
                        self.jobs[element_text] = element_href
            except: pass
            
    def _check_if_job_already_in_database(self, title, url):
        """
        Checks if the job that is extracted is already stored in the database. This function is so as to not double create job advertisements. It also facilitates new job URLs posted in the website.

        Parameters
        ----------
        title: str
            title of the job to check in the database
        url: str
            url of the job to check in the database

        Returns
        -------
        boolean
            True if job exists else False
        """
        from jobdetailsextractor.models import Job

        if Job.objects.filter(title=title, url=url).first():
            return True

        return False
