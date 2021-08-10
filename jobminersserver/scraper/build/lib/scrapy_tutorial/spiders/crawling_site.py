from .locators import Paginator, Xpather
from scrapy import Request

class Site:
    def __init__(self, search_page_url):
        """
        A site object for storing top level crawling site site related info.
        """
        # Search Page Initializations
        self.search_page_url = search_page_url
        
        # Paginator Initialization
        self.pages = Paginator()

class NonAJAX:
    def __init__(self, response, links, site, paginated=True):
        """
        A representation of a Non-AJAX website.
        """
        self.response = response
        self.links = links
        self.site = site
        self.paginated = paginated

        self.ESTD_JOBS_IN_PAGE = 150

        # xpath initialization
        self.xpaths = Xpather(response, site, paginated)
        self.var_index = None

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
        xpaths = self.get_eligible_xpaths(xpaths)
        # Get the varying index
        xpaths[0] = xpaths[0].split('/')
        xpaths[1] = xpaths[1].split('/')
        for index, path in enumerate(xpaths[0]):
            if path != xpaths[1][index]:
                self.var_index = index

        paths = xpaths[0].copy()
        init = xpaths[0][self.var_index][:-2]
        for i in range(1, self.ESTD_JOBS_IN_PAGE):
            paths[self.var_index] = init + str(i) + ']'
            element_text = response.xpath('/' + "/".join(paths) + '//text()').get()
            element_href = response.xpath('/' + "/".join(paths[:-1]) + '//@href').get()
            if element_text and element_href:
                self.jobs[element_text] = element_href

        xpaths[0] = '/'.join(xpaths[0])
        xpaths[1] = '/'.join(xpaths[1])

    def get_eligible_xpaths(self, xpaths):
        lengths = [len(xpath) for xpath in xpaths]
        
        similar_xpaths_length = 0
        for length in lengths: 
            if(lengths.count(length) > 1): similar_xpaths_length = length

        eligible_xpaths = [xpath for xpath in xpaths \
            if len(xpath) == similar_xpaths_length or len(xpath) == similar_xpaths_length + 1]
        # + 1 because [1] or [26] may be equal if there are many job ads in same page.

        return eligible_xpaths