"""
This submodule abstracts all the searching related operations to a search page of any website to obtain it's search page and search page URL.

Classes
-------
Search()
The main class used to extract search page URL.
"""
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from urllib.parse import urlparse

from backend.misc import log, try_and_pass

from .exceptions import SearchURLNotFound, DriverNotFound


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
            path = os.getcwd() + "/interactor/reqs/chromedriver"
            # if windows
            if sys.platform.startswith("win32"):
                path += "_win.exe"
            self._driver = webdriver.Chrome(
                executable_path=path, options=chrome_options
            )
        except WebDriverException as e:
            log("interactor", "error", f"{e}")
            raise DriverNotFound
        except Exception as e:
            log("interactor", "error", f"{e}")

    def _search_term(self, search):
        """
        Performs search on textbox sending no key or space key

        Parameters
        ----------
        search: str
            xpath of the text box from xpath_of_textbox below

        Returns
        -------
        search_url: str
            search_url computed.

        Raises
        ------
        DriverNotFound
            if the selenium web driver file is not found in the server.
        """
        if not hasattr(self, "_driver"):
            raise DriverNotFound

        check_url = self._driver.current_url
        search_url = ""

        @try_and_pass
        def send_empty(search):
            search.send_keys("")  # send no keys to search box
            search.send_keys(Keys.ENTER)  # Enter the search box
            log("interactor", "info", f'sent "" to search box')
            return self._driver.current_url

        search_url = send_empty(search)

        if search_url == check_url:

            @try_and_pass
            def send_space(search):
                search.send_keys(" ")  # send ' ' key to search box
                search.send_keys(Keys.ENTER)  # Enter the search box
                log("interactor", "info", f'sent " " to search box')

                return self._driver.current_url

            search_url = send_space(search)

        return search_url

    def get_search_url(self, url):
        """
        Returns the search URL of the website is able to be extracted else raises error.

        Parameters
        ----------
        url
            url to get search_url from

        Returns
        -------
        search_url
            url of the search page

        Raises
        ------
        SearchURLNotFound
            Search URL of the URL not able to be found.
        """
        self._url = url
        log("interactor", "info", f"Using searcher for {self._url}")
        log("main", "info", f"Using searcher for {self._url}")

        try:
            self._driver.get(self._url)
        except Exception as e:
            log(
                "interactor", "info", f"Couldn't get html response for {self._url}: {e}"
            )
            log("main", "info", f"Couldn't get html response for {self._url}: {e}")

        check_url = self._driver.current_url

        log("interactor", "info", "Finding in 3 <input type='text'>")
        search_url = self._find_element_by_type("text", 3, check_url)

        if not search_url:
            log("interactor", "info", "Checking in 2 <input type='search'>")
            search_url = self._find_element_by_type("search", 2, check_url)

        if not search_url:
            raise SearchURLNotFound(url)

        # For kumarijobs type websites
        @try_and_pass
        def remove_token(search_url):
            if "_token" in search_url:
                log(
                    "interactor", "info", "_token found in search url, removing _token."
                )
                return (
                    urlparse(search_url).scheme
                    + "://"
                    + urlparse(search_url).netloc
                    + urlparse(search_url).path
                    + "?"
                    + urlparse(search_url).query.split("&")[-1]
                )
            return search_url

        search_url = remove_token(search_url)

        log("interactor", "info", f"Got search url: {search_url}")
        log("main", "info", f"Got search url: {search_url}")

        return search_url

    def _find_element_by_type(self, element_type, finish_index, check_url):
        """
        Finds an element by it's type.

        Parameters
        ----------
        element_type: str
            type of element. Can be 'search', 'text'
        finish_index: int
            specifies the finish index of the search object. For eg, if we want to search 2 elements, then finish index is 3, if 3, then 4 and so on.
        check_url: str
            URL of the page to check on.

        Returns
        -------
        str
            search_url if it is found else None.
        """
        search_url = ""

        if check_url == self._url:

            @try_and_pass
            def check_first_element(element_type):
                search = self._driver.find_element_by_xpath(
                    f"//input[@type='{element_type}']"
                )
                search_url = self._search_term(search)

                return search_url

            search_url = check_first_element(element_type)

        @try_and_pass
        def check_nth_element(element_type, i):
            search = self._driver.find_element_by_xpath(
                f"//input[@type='{element_type}'][{i}]"
            )
            search_url = self._search_term(search)

            return search_url

        for i in range(2, finish_index):
            if check_url == self._url:
                if check_nth_element(
                    element_type, i
                ) != self._url and check_nth_element(element_type, i):
                    search_url = check_nth_element(element_type, i)

        if search_url == self._url:
            return None

        return search_url


if __name__ == "__main__":
    url = "https://www.kumarijob.com/"
    s1 = Search()
    print(s1.get_search_url(url))
