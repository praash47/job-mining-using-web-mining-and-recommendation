"""
Request Google
--------------
This file requests google and gets 100 urls.

This file returns 100 urls as a list.

This file requires googleapiclient to be installed.

This file consists of two classes:
    * RequestGoogle: used for requesting 100 urls from
    google from API.
    * GoogleAPI: Google API object used for making request.
"""
from googleapiclient.discovery import build

from configparser import ConfigParser
import time

class RequestGoogle:
    """
    Class used to request google for 100 urls from api. Manages the api
    such that you don't reach API limit for each api
    ...

    Attributes
    ----------
    _100urls : list
        100 urls list of google returned seach results

    Methods
    -------
    get_100_urls()
        Returns list of 100 urls from Google Custom Search API.
    """
    def __init__(self):
        """
        * Read configuration files.
        * Initialize all api objects
        """
        self._100urls = []

        # Parser
        # Google API settings
        CONFIG = 'jobminersserver/requestutils/requestgooglemodule/googleapis.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        
        # Multiple google apis for switching between apis after limit reached
        # for each api.
        self.google_apis = []
        self.get_all_apis()


    def get_100_urls(self):
        """
        Gets 100 urls from first 10 pages of google search results.

        Returns
        -------
        list of strings:
            a list of 100 urls of first 10 pages of search result links
        """
        # TODO: handle logic such that 100 urls are got using different apis.
        self._100urls = self.get_from_api()
        print("Got from google.")

        return self._100urls

    def get_all_apis(self):
        """
        Parse out all the configuration for apis listed in format:
            API<N>
            api_key = ""
            search_engine_id = ""
        and creates a Google API object and appends it to self.google_a
        """
        # First three letters API
        apis = [api for api in self.parser.sections() if api[0:3] == 'API']

        for api in apis:
            self.google_apis.append(GoogleAPI(
                self.parser.get(api, "api_key"),
                self.parser.get(api, "search_engine_id")
            ))

    def get_from_api(self):
        
        """
        Checks if API is available and if it is available, recursively gets 100 urls in
        10 iterations.
        """
        # If available, take the first one available.
        api = [curr_api for curr_api in self.google_apis if curr_api.is_available()][0]

        search_results = []
        
        # 11, 21, 31, ..., 91
        SEARCH_INDEX_STEP = 10
        for i in range(1, self.parser.getint('global', 'num_links'), SEARCH_INDEX_STEP): 
            search_result = api.search(
                search_query=self.parser.get('global', 'search_query'),
                start_index=i  # search index for getting from paged search result.
            )
            # {items: {link: 'www.example.com'}} for all pages.
            search_results += [item['link'] for item in search_result['items']]

        return search_results

class GoogleAPI:
    """
    Creating and searching using a Google API.

    Attributes
    ----------
    usage_count : int
        number of time the API is used in a day.
    last_used_time : time object (current time in ms)
        last time instance that API was created or used to
        fetch a search result. 

    Methods
    -------
    search(sound=None)
        Search using a search query to google search api with optional parameters
        num_results and start_index for specifying the page.
    is_available()
        Checks elapsed time from last used time and checks if one day has elapsed
        and API limit has been crossed for today.
    """
    def __init__(self, api_key, search_engine_id):
        """
        Parameters
        ----------
        api_key : str
            unique key for google API
        search_engine_id : str
            unique key for search engine id
        """
        self.API_KEY = api_key
        self.SEARCH_ENGINE_ID = search_engine_id
        self.usage_count = 0
        self.last_used_time = time.time()

    def search(self, search_query, num_results=10, start_index=1):
        """
        Uses google search api to "search" (fetch) the google search results.

        Parameters
        ----------
        search_query : str
            Search query for searching into the API.
        num_results : int, optional, valid: 1-10
            The number of links to get from the API (default=10)
        start_index : int, optional
            The offset of search results to start search from (default=1)

        Raises
        ------
        Exception
            If any exception is raised, it is printed.
        """
        try:
            # Google API usage syntax, available on google search API documentation.
            resource = build("customsearch", 'v1', developerKey=self.API_KEY).cse()
            response = resource.list(
                q=search_query,
                cx=self.SEARCH_ENGINE_ID,
                num=num_results,
                start=start_index
            ).execute()
            
            if response:
                self.usage_count += 1
                self.last_used_time = time.time()
                return response
        except Exception as e:
            print(e)
            return None

    def is_available(self):
        """
        Checks if an api is available.

        Returns
        -------
        Boolean
            True if an API usage limit for the day hasn't exceeded.
            False else.
        """
        ONE_DAY = 86400000
        API_DAY_LIMIT = 100
        elapsed_time = time.time() - self.last_used_time
        if self.usage_count < API_DAY_LIMIT and elapsed_time < ONE_DAY:
            return True
        
        return False

if __name__ == "__main__":
    google_request = RequestGoogle() 
    urls = google_request.get_100_urls()
    print(urls)