"""
This submodule abstracts all the searching related operations to a search page of any website to obtain it's search page and search page URL.

Classes
-------
Search()
    The main class used to extract search page URL.
"""
import logging
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from urllib.parse import urlparse


from .exceptions import SearchURLNotFound
from .exceptions import DriverNotFound

logger = logging.getLogger('interactor')
mainlogger = logging.getLogger('main')


class Search:
    """
    A class to find the search box in the webpage and
    perform search with no character or single space.

    Methods
    -------
    get_search_url(search, self._url)
        Gets search URL from the page and returns it.
    """

    def __init__(self):
        """
        Parameters
        ---------
        url : str
            url of the webpages

        Raises
        ------
        DriverNotFound
            Web Driver not found in the server due to some reasons.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self._url = None

        try:
            path = os.getcwd() + '/interactor/reqs/chromedriver'
            # if windows
            if sys.platform.startswith('win32'):
                path += '_win.exe'
            self._driver = webdriver.Chrome(
                executable_path=path, options=chrome_options)
        except WebDriverException as e:
            logger.error(f'{e}')
            raise DriverNotFound
        except Exception as e:
            logger.error(f'{e}')

    def _search_term(self, search):
        """
        performs search on textbox sending no key or space key
        Parameters
        ----------
        search: str
            xpath of the text box from xpath_of_textbox below

        Returns
        -------
        search_url: str
            search_url computed.
        """
        if not hasattr(self, '_driver'):
            raise DriverNotFound
        check_url = self._driver.current_url
        search_url = ''
        try:
            search.send_keys('')  # send no keys to search box
            search.send_keys(Keys.ENTER)  # Enter the search box
            search_url = self._driver.current_url
            logger.info(f'sent "" to {search}')
        except:
            pass

        if self._url == check_url:
            try:
                search.send_keys(' ')           # send ' ' key to search box
                search.send_keys(Keys.ENTER)  # Enter the search box
                search_url = self._driver.current_url
                logger.info(f'sent " " to {search}')
            except:
                pass

        return search_url

    def get_search_url(self, url):
        '''xpath_of_textbox(self._url) checks the xpath of
            input @ type = "text"[1][2][3] and "search"[1][2]

        Returns
        -------
        search_url
            url of the search page

        Raises
        ------
        SearchURLNotFound
            Search URL of the URL not able to be found.
        '''
        self._url = url
        logger.info(f"Using searcher for {self._url}")
        mainlogger.info(f"Using searcher for {self._url}")
        try:
            self._driver.get(self._url)
        except Exception as e:
            logger.error(f"Couldn't get html response for {self._url}: {e}")
            mainlogger.error(f"Couldn't get html response for {self._url}: {e}")

        check_url = self._driver.current_url

        logger.info("Finding in 3 <input type='text'>")
        search_url = self._find_element_by_type('text', 3, check_url)

        if not search_url:
            logger.info(
                "Couldn't find in <input type='text'>, so checking in 2 <input type='search'>")
            search_url = self._find_element_by_type('search', 2, check_url)

        try:
            if '_token' in search_url:
                logger.info("_token found in search url, removing _token.")
                search_url = urlparse(search_url).scheme + '://' + urlparse(search_url).netloc \
                    + urlparse(search_url).path + '?' + \
                    urlparse(search_url).query.split('&')[-1]
        except:
            pass

        if not search_url:
            raise SearchURLNotFound(url)

        logger.info(f'Run searcher module and got search url: {search_url}')
        mainlogger.info(
            f'Run searcher module and got search url: {search_url}')

        return search_url

    def _find_element_by_type(self, element_type, finish_index, check_url):
        self._search = ''
        self._search_url = ''

        if check_url == self._url:
            try:
                self._search = self._driver.find_element_by_xpath(
                    f"//input[@type='{element_type}']")
                self._search_url = self._search_term(self._search)
            except:
                pass
        for i in range(2, finish_index):
            if check_url == self._url:
                try:
                    self._search = self._driver.find_element_by_xpath(
                        f"//input[@type='{element_type}'][{i}]")
                    self._search_url = self._search_term(self._search)
                except:
                    pass
        if self._search_url == self._url:
            return None

        return self._search_url
    # xpath of first textbox with input type text


if __name__ == "__main__":
    url = 'https://www.kumarijob.com/'
    s1 = Search()
    print(s1.get_search_url(url))
