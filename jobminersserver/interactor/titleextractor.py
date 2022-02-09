"""
This submodule consists of the required classes and it's methods in order to abstract the requirements of the title xpath extraction and extraction of the jobs from that xpath.

Decorators
----------
call_if_non_ajax_based()
Calls any function wrapped by the decorator if it is Non AJAX based, for now, it is assumed that every website is non AJAX based.

Classes
-------
TitleExtractor()
Responsible for extraction of the title xpath and jobs from that title xpath.
MockResponse()
Use of scrapy's link extractor requires a scrapy.Response. So, this is our mock (fake) scrapy response to fool scrapy in believing that it has received it's own Response.
MockSelector()
One of the elements or properties of the MockResponse object.
"""
import codecs

from scrapy.linkextractors import LinkExtractor

from checkers.models import JobWebsite
from jobdetailsextractor.models import Job

from backend.misc import log

from .site import Site, NonAJAX


def call_if_non_ajax_based(func):
    """
    This decorator calls a function only if it is non AJAX based.

    This accepts following keyworded arguments:
    * na_website: NonAJAX
        NonAJAX object.
    * links_in_page: list of scrapy.Links
        List of links in page
    * pages: boolean
        Specifies if the page is already checked and is paginated.
    """

    def is_non_ajax_based(self, **kwargs):
        na_website = kwargs.get("na_website", None)
        links_in_page = kwargs.get("links_in_page")
        job_titles = kwargs.get("job_titles")
        pages = kwargs.get("pages", False)

        # Check if Non AJAX based paginated website
        if not self._website and (pages or self._site.pages.has_pages(links_in_page)):
            # Create a non-ajax object out of the site.
            # pag_na_website refers to paginated non ajax variable.
            pag_na_website = (
                NonAJAX(self.response, links_in_page, self._site, job_titles)
                if not na_website
                else na_website
            )

            # Determine if the site is crawlable.
            if pages or pag_na_website.is_crawlable():
                if not na_website:
                    return func(na_website=pag_na_website, obj=self, **kwargs)
                return func(obj=self, **kwargs)
        # For non ajax based non paginated website
        elif not self._website:
            na_website = NonAJAX(
                self.response, links_in_page, self._site, job_titles, paginated=False
            )
        # If title xpath is not necessary to check, we already know it is non-ajax website.
        else:
            paginated = None
            if not na_website:
                paginated = True if self._site.pages.has_pages(links_in_page) else False
                if paginated:
                    self._site.pages.get_last_page(links_in_page)
                    self._site.pages.check_search_step(self._site, links_in_page)
                na_website = (
                    NonAJAX(
                        self.response,
                        links_in_page,
                        self._site,
                        job_titles,
                        paginated=paginated,
                    )
                )
                return func(na_website=na_website, obj=self, **kwargs)
            else:
                return func(obj=self, **kwargs)

        return func(na_website=na_website, obj=self, **kwargs)

    return is_non_ajax_based


class TitleExtractor:
    """
    A link extractor and site object is initialized with search page url
    coming from kwargs.

    Methods
    -------
    extract_title_xpath()
        Extracts the title xpath of the site and returns it.
    extract_job_title_url_from_title_xpath(title_xpath)
        Extracts jobs from title xpaths and places it in self._jobs().
    store_into_database()
        Stores the job titles and URLs extracted by the TitleExtractor into the database.

    Static Methods
    --------------
    mock_scrapy_response(search_url)
        Returns the Response object which is the mock of the scrapy response in order to use scrapy.LinkExtractor object.
    check_or_make_url_complete(url, homepage)
        Checks or makes the URL complete. i.e. populates the URL with the homepage if it's relative URL. For eg.: if /job-detail-296, homepage is goodjobs.com.np, then goodjobs.com.np/job-detail-296.
    """

    def __init__(self, search_url, website=None):
        """
        Parameters
        ----------
        search_page_url: str
            Search page url of the site to perform scraping on
        website: JobWebsite, optional
            JobWebsite object of the website to create TitleExtractor object of. Only set after we have the information about the website.

        Raises
        ------
        SearchURLNotFound
            The search URL is not found during object initialization
        """
        self._website = website
        from .exceptions import SearchURLNotFound

        if not search_url:
            raise SearchURLNotFound("No URL")

        log("interactor", "info", f"Title Extraction object created for {search_url}")
        log("main", "info", f"Title Extraction object created for {search_url}")
        # Scrapy's link extractor object
        self._link_extractor = LinkExtractor()

        # This is a master site object that remains in the JobURL object.
        self._site = Site(search_page_url=search_url)
        log("interactor", "info", "Site, Xpather object created")

        # We mock the scrapy response in order to use it with scrapy.link_extractor().
        self.response = TitleExtractor.mock_scrapy_response(search_url)
        log("interactor", "info", f"Mocked Scrapy Response: {self.response}")

        self._jobs = {}

    def extract_title_xpath(self):
        """
        Extracts title xpath and returns it.

        Title xpath is the xpath of the job title inside a search page.

        Returns
        -------
        str
            title_xpath: title xpath thus extracted.
        """
        # We extract links in page using the scrapy's link extractor function.
        links_in_page = self._link_extractor.extract_links(self.response)

        job_titles = []
        log("interactor", "info", "Reading 70,000 titles.")
        # titles_combined.txt: 70,000 titles to match xpaths from.
        with open("interactor/reqs/titles_combined.txt") as titles:
            job_titles = [title.strip("\n") for title in titles.readlines()]

        title_xpath = self._get_title_xpath(
            links_in_page=links_in_page, job_titles=job_titles
        )
        log("main", "info", f"Got title xpath: {title_xpath}")

        return title_xpath

    @call_if_non_ajax_based
    def _get_title_xpath(na_website, **kwargs):
        """
        The function is wrapped around call_if_non_ajax_based and gets called properly only if it is a non AJAX based website.

        Title xpath is the xpath of the job title inside a search page.

        Returns
        -------
        str
            xpath: title xpath thus extracted.
        """
        xpath = None
        if not na_website.title_xpath:
            links_in_page = kwargs.get("links_in_page")
            xpath = na_website.xpaths.get_xpath(links_in_page)
        else:
            xpath = na_website.title_xpath

        log("main", "info", f"Title Xpath: {xpath}")
        return xpath

    def extract_job_title_url_from_title_xpath(self, title_xpath):
        """
        Extracts job in the page if only one page and in all pages if a paginated website.

        Parameters
        ----------
        title_xpath: str
            The template title_xpath from which to extract jobs from.

        Raises
        ------
        JobTitleXpathNotFound
            If Job title xpath is not supplied in.
        """
        from jobdetailsextractor.exceptions import JobTitleXpathNotFound

        if not title_xpath:
            raise JobTitleXpathNotFound(self._site.search_page_url)

        # Extract links in page
        links_in_page = self._link_extractor.extract_links(self.response)
        job_titles = []
        log("interactor", "info", "Reading 70,000 titles.")
        # titles_combined.txt: 70,000 titles to match xpaths from.
        with open("interactor/reqs/titles_combined.txt") as titles:
            job_titles = [title.strip("\n") for title in titles.readlines()]
        self._scrape_job_urls(
            response=self.response,
            title_xpath=title_xpath,
            links_in_page=links_in_page,
            job_titles=job_titles,
        )
        log("interactor", "info", f"got jobs for {self._site.search_page_url}")

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
        title_xpath: str
            title_xpath to scrape out job URLs from
        response: MockResponse
            our mock (fake) scrapy response object
        obj: NonAJAX
            our Non AJAX object of the site.
        """
        na_website = kwargs.get("na_website")
        title_xpath = kwargs.get("title_xpath")
        response = kwargs.get("response")
        obj = kwargs.get("obj")

        log(
            "interactor",
            "info",
            f"Scraping jobs in page: {na_website.site.pages.page_url}",
        )
        log("main", "info", f"Scraping jobs in page: {na_website.site.pages.curr_page}")

        # if this is true, this means that the site has pages.
        if na_website.site.pages.last_page:
            # Until last page is not reached, keep on getting jobs.
            # On reaching the last page, move_to_next_page() returns
            # false.
            log("interactor", "info", f"Checking if further pages left.")
            # Moves our current site.pages to next page.
            pages_left = na_website.site.pages.move_to_next_page()
            if pages_left:
                # Jobs are actually scraped out using this.
                na_website.get_jobs_for_page(title_xpath, response)

                log(
                    "interactor",
                    "info",
                    f"Moving to page {na_website.site.pages.curr_page}",
                )
                # Create Mock Response for the page after.
                new_response = TitleExtractor.mock_scrapy_response(
                    na_website.site.pages.page_url
                )
                # Recursive calling in order to scrape in consecutive pages until the last page.
                obj._scrape_job_urls(
                    response=new_response,
                    na_website=na_website,
                    title_xpath=title_xpath,
                    pages=True,
                )

        else:
            # This is for non-paginated ajax based websites

            # TODO: jobsdynamics type website: there are multiple job titles mentioned
            # in the same ad, that contradicts with our architecture.
            # - Alljobnepal where links is placed inside the company's name, WHAT???
            # yes, they even do it!
            na_website.get_jobs_for_page(title_xpath, response)

        obj._jobs = na_website.jobs

    def store_into_database(self):
        """
        This handles all the operations for storing the collected jobs in self._jobs and stores it properly inside the database.
        """
        log("interactor", "info", f"Storing job titles and urls into database")
        log("main", "info", f"Storing job titles and urls into database")
        # get the django models JobWebsite object from the database
        website = JobWebsite.objects.get(search_url=self._site.search_page_url)

        for title, url in self._jobs.items():
            # Process the job URL so as to make situations like getting only the
            # partial url without homepage like on in merojob.com can be avoided.
            url = TitleExtractor.check_or_make_url_complete(url, website.url)

            # to save job url into the database
            job = Job(website=website, title=title, url=url)
            job.save()

    @staticmethod
    def mock_scrapy_response(search_url):
        """
        Mocks the scrapy response. Mocking means creating an object that matches scrapy's Response object. It is so as because scrapy's link_extractor only works for scrapy response.

        Creates a mock (fake) scrapy response as:
        Response:
            - url
            - encoding
            - text
            - Selector:
                - root
            - tree

        Parameters
        ----------
        search_url: str
            search URL of URL from which Scrapy mock response to create

        Returns
        -------
        MockResponse
            our custom mock (fake) Scrapy Response
        """
        from requestutils.request import Request

        request = Request(search_url)
        text = request.request_html()
        if not text:  # local .html file received (used for testing)
            html_file = codecs.open(search_url, "r")
            text = html_file.read()
            request.html = text

        request.filter_unnecessary_tags()

        tree = request.get_html_tree()
        root = tree.getroot()
        selector = MockSelector(root)

        return MockResponse(search_url, text, selector, tree)

    @staticmethod
    def check_or_make_url_complete(url, homepage):
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
        if url[0] == "/":
            url = url[1:]

        return homepage + url


class MockResponse:
    """
    Mock Response (fake) Response of the scrapy.Response object in order to use scrapy.link_extractor(). This only consists of the response attributes required for the link_extractor. This maybe only a partial copy of the response. But it works!

    Parameters
    ----------
    url: str
        URL of which response needed
    encoding: str
        encoding of the page whose response is in, default='utf-8'
    text: str
        html response of the page
    tree: lxml.etree
        lxml etree of the html response
    selector: MockSelector
        Mock (fake) selector object of the scrapy
    """

    def __init__(self, url, text, selector, tree, encoding="utf-8"):
        self.url = url
        self.encoding = encoding
        self.selector = selector
        self.text = text
        self.tree = tree


class MockSelector:
    """
    Fake (Mock) scrapy selector required by the MockResponse object. This is also only a partial copy of the scrapy.Selector object with only root parameter

    Parameters
    ----------
    root: lxml.HtmlElement
        root lxml HtmlElement of the current lxml.etree of the html response strings.
    """

    def __init__(self, root):
        self.root = root
