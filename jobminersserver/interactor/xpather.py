"""
This submodule is responsibe for locating thus named locators. This file handles the location
within the websites i.e. pages through the paginator object and also handles the locations
that are within the page with the help of xpather object that is responsible for processing
of the xpaths.

Classes
-------
Xpather()
    Responsible for the extraction of the title xpath and handle all it's complexities.
"""
import logging

from .exceptions import NoTwoMatchingTitles

from backend.misc import common_start


logger = logging.getLogger('interactor')
mainlogger = logging.getLogger('main')


class Xpather:
    def __init__(self, response, site, paginated):
        """
        This class is responsible for handling and computing the xpaths. It is
        extracting the xpaths from the site and abstracts the complexities of
        handling the xpaths.

        Parameters
        ----------
        response: str
            HTML response of the site
        site: Site
            site object of the website
        paginated: boolean
            True if pagination is there

        Methods
        -------
        get_xpath: Use to extract xpaths from the website.
        """
        # Xpath #1 and #2
        self._first = None
        self._second = None

        # Matching texts and urls of job titles
        self._job_titles = []
        logger.info('Reading 70,000 titles.')
        mainlogger.info('Reading 70,000 titles.')
        # titles_combined.txt: 70,000 titles to match xpaths from.
        with open('interactor/reqs/titles_combined.txt') as titles:
            self._job_titles = [title.strip('\n')
                               for title in titles.readlines()]

        # Link Text and URLs
        self._link_texts = []
        self._link_urls = []

        # HTML tree for getting xpaths of the links
        self._tree = response.tree

        # Site object and Paginated, that is pagination is present in website.
        self._site = site
        self._paginated = paginated

    def get_xpath(self, links):
        """
        Gets xpaths from paginated and non paginated websites. It is a thin wrapper from
        around the _find_xpaths(). It basically handles pagination and calls it on the basis
        of pagination present or not.

        Parameters
        ----------
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.

        Returns
        -------
        xpath: str
            title_xpath

        Raises
        ------
        NoTwoMatchingTitles
            No Two Matching Titles were found.
        """
        # Extract out link texts of job titles present in site and the job titles file.
        self._link_texts = [link.text.strip(
            '\n') for link in links if link.text.strip('\n') in self._job_titles]
        if not self._link_texts:
            raise NoTwoMatchingTitles(self._site.search_page_url)

        logger.info(f'Found matching titles: {self._link_texts}')
        mainlogger.info(f'Found matching titles: {self._link_texts}')

        mainlogger.info(f'Finding xpaths')
        if self._paginated:
            # Check last page and checking and assigning the search step.
            self._site.pages.get_last_page(links)
            self._site.pages.check_search_step(self._site, links)

            xpath = self._find_xpath(links)

            return xpath
        else:
            xpath = self._find_xpath(links)

            if xpath:
                return xpath

            logger.error(f"Couldn't find the xpath.")

            raise NoTwoMatchingTitles(self._site.search_page_url)

    def _find_xpath(self, links):
        """
        Finds the xpaths from the links. Also, it handles the nested links as well
        as the situations where the xpaths are not present.

        Parameters
        ----------
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.

        Returns
        -------
        xpaths: list of str
            list of xpath
        """
        logger.info(f"Finding the xpath...")
        self._first = self._find_nth_xpath(self._link_texts, link_texts_index=0)
        self._second = self._find_nth_xpath(self._link_texts, link_texts_index=1)

        xpaths = []
        if not self._first or not self._second:
            logger.info(f"One of the xpath not found, trying to find nested")
            # Both xpaths are not present, then it should be nested.
            xpaths = self._get_xpath_from_nested(links)
            # If also not present from nested, then it is not present.
            if not xpaths:
                logger.info(f"not even nested xpath found")
                return False

        # If xpaths is not already found from nested.
        if not xpaths:
            for xpath in self._first:
                xpaths.append(self._tree.getpath(xpath))
            for xpath in self._second:
                xpaths.append(self._tree.getpath(xpath))

        logger.info(f'Got xpaths: {xpaths}')
        # Filter out the xpaths because of the case that useless xpaths or false xpaths
        # from the divs that have the job title but still not legitimate job box are the
        # types. For example, recommended jobs, featured jobs etc.
        xpaths = self._get_eligible_xpaths(xpaths)
        logger.info(f'Eligible xpaths: {xpaths}')

        # Creating the title xpath by finding the common start
        xpath_init = common_start(xpaths[0], xpaths[1])
        xpath_end = common_start(
            "".join(reversed(xpaths[0])), "".join(reversed(xpaths[1])))

        xpath = xpath_init + "|" + "".join(reversed(xpath_end))

        logger.info(f'Title xpath: {xpath}')

        return xpath

    def _get_xpath_from_nested(self, links):
        """
        In some websites, the urls are listed one level deep. The xpath is got from link-text.
        in nested situations like this.

        For eg: <a href="job.url"><h3>Job Title Text</h3></a>

        Parameters
        ----------
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.

        Returns
        -------
        xpaths: list of str
            list of xpath
        """
        # Extract out link urls of job titles present in site and the job titles file.
        self._link_urls = [link.url for link in links if link.text.strip(
            '\n') in self._job_titles]

        # Find a with urls of link urls. Grab the node inside it. For eg.: <h3> of the above example
        try:
            nested_elements1 = self._tree.xpath(
                f"//a[contains(@href,'{self._link_urls[0]}')]/node()")
            nested_elements2 = self._tree.xpath(
                f"//a[contains(@href,'{self._link_urls[1]}')]/node()")
        except:
            return False

        # If an element object is found inside those a tags and inside of it a tag
        # is present and contains the link_text, then place that intermediate tag in
        # the path list.
        xpath_one, xpath_two = '', ''
        for element in nested_elements1:
            # text inside tag is also regarded as a 'node', to ignore it only element type, not str
            # type are taken here.
            if not isinstance(element, str):  # Normally, it is of str type.
                xpath_one = self._tree.xpath(
                    f"//a//{element.tag}[contains(text(), \"'{self._link_texts[0]}'\")]")
        for element in nested_elements2:
            if not isinstance(element, str):
                xpath_two = self._tree.xpath(
                    f"//a//{element.tag}[contains(text(), \"'{self._link_texts[1]}'\")]")
        # Issue is not having nested elements
        if not xpath_one and not xpath_two:
            return None

        # Extraction of xpaths from tree
        xpaths = []
        for xpath in xpath_one:
            xpaths.append(self._tree.getpath(xpath))
        for xpath in xpath_two:
            xpaths.append(self._tree.getpath(xpath))

        return xpaths

    def _find_nth_xpath(self, link_texts, link_texts_index=0):
        """
        Used to find the non-nested xpath from the link-text. If not found, then simply
        passes.

        Parameters
        ----------
        link_texts: list of str
            list of link text that were matched from above
        link_texts_index: int, default=0
            the index of link text that we are currently working on.

        Returns
        -------
        xpath if found, otherwise None.
        """
        logger.info(f"Finding the n = {link_texts_index} xpath...")
        try:
            # Get two matching xpaths to compute out the difference
            xpath = self._tree.xpath(
                f'//a[contains(text(), "{link_texts[link_texts_index]}")]')
            return xpath
        except:
            logger.info(f"Couldn't find the xpath.")

    def _get_eligible_xpaths(self, xpaths):
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
        logger.info(f'Filtering out non eligible xpaths')
        # compute the length of all the n xpaths in the xpaths.
        lengths = [len(xpath) for xpath in xpaths]

        # find the length of the xpath of which two instances are present in the
        # xpaths list.
        similar_xpaths_length = 0
        for length in lengths:
            if(lengths.count(length) > 1):
                similar_xpaths_length = length

        # Get the eligible xpaths that have only similar xpaths length.
        eligible_xpaths = [xpath for xpath in xpaths
                           if len(xpath) == similar_xpaths_length or len(xpath) == similar_xpaths_length + 1]
        # + 1 because [1] or [26] may be equal if there are many job ads in same page.

        return eligible_xpaths
