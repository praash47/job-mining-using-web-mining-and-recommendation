"""
This file abstracts the complexities of the website object by the means of it's
provided site class which is a very high level extraction of the websites that
is in the process of being scraped and non ajax object which even provides a lower
level abstraction of the website being scraped.
"""
from .locators import Paginator, Xpather

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
        self.ESTD_JOBS_IN_PAGE = 150

        # xpath initialization
        self.xpaths = Xpather(response, site, paginated)
        self.var_index = None  # var index variable is the index of the
        # variable div of the site in case of jobs div.

        self.jobs = {}

    def is_crawlable(self):
        """
        Returns true if xpaths can be got from the links of the first page.
        """
        # Try to get two matching xpaths
        if self.xpaths.get_xpaths(
            self.links):
            return True  # If getting two xpaths is succesful, then it is crawlable.
        return False

        
    def get_jobs_from_xpath(self, xpaths, response):
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
        # Filter out the xpaths because of the case that useless xpaths or false xpaths
        # from the divs that have the job title but still not legitimate job box are the
        # types. For example, recommended jobs, featured jobs etc.
        xpaths = self.get_eligible_xpaths(xpaths)

        # Get the varying index, so splitting so that one by one xpath can be checked so that
        # the unequal or changing div can be found.
        xpaths[0] = xpaths[0].split('/')
        xpaths[1] = xpaths[1].split('/')
        for index, path in enumerate(xpaths[0]):
            if path != xpaths[1][index]:  # Unequal path is the changing div
                self.var_index = index  # Save the index of that div

        # Make the copy of the first xpath
        paths = xpaths[0].copy()
        # Take the first half of the changing div, first half refers to like this div[,
        # so that other numbers can be placed in it so that ith place can be extracted.
        init = xpaths[0][self.var_index][:-2]
        for i in range(1, self.ESTD_JOBS_IN_PAGE):
            paths[self.var_index] = init + str(i) + ']'
            # Get the text and href i.e. url and save into the self.jobs
            element_text = response.xpath('/' + "/".join(paths) + '//text()').get()
            element_href = response.xpath('/' + "/".join(paths[:-1]) + '//@href').get()
            if element_text and element_href:
                self.jobs[element_text] = element_href

        # Reset back the xpath to it's original state.
        xpaths[0] = '/'.join(xpaths[0])
        xpaths[1] = '/'.join(xpaths[1])

    def get_eligible_xpaths(self, xpaths):
        """
        There are many non eligible or false xpaths that are present in the page
        that have the job title but still not legitimate job box are the types.
        For example, recommended jobs, featured jobs etc.

        This function prepares and returns the eligible xpaths. This function is
        imagined to be accurately enough and assumes that not more than one job
        is detected from the false jobs boxes or example featured boxes.
        
        Parameters
        ----------
        xpaths: list of str
            list of xpath strings

        Returns
        -------
        eligible_xpaths: list of str
            list of xpaths that are eligible for finding xpaths from within the job.
        """
        # compute the length of all the n xpaths in the xpaths.
        lengths = [len(xpath) for xpath in xpaths]
        
        # find the length of the xpath of which two instances are present in the
        # xpaths list.
        similar_xpaths_length = 0
        for length in lengths: 
            if(lengths.count(length) > 1): similar_xpaths_length = length

        # Get the eligible xpaths that have only similar xpaths length.
        eligible_xpaths = [xpath for xpath in xpaths \
            if len(xpath) == similar_xpaths_length or len(xpath) == similar_xpaths_length + 1]
        # + 1 because [1] or [26] may be equal if there are many job ads in same page.

        return eligible_xpaths