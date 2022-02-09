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
from googleapiclient.errors import HttpError

from django.utils.timezone import now

from requestutils.models import API

from backend.misc import read_config, log


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
        log("main", "info", "Created the request google object")
        log("requestinggoogle", "info", "Created the request google object")
        self._100urls = []

        # Parser
        # Google API settings
        self._parser = read_config("requestutils/requestgooglemodule/googleapis.ini")

        # Multiple google apis for switching between apis after limit reached
        # for each api.
        self._google_apis = []
        self._get_all_apis()

    def get_100_urls(self):
        """
        Gets 100 urls from first 10 pages of google search results.

        Returns
        -------
        list of strings:
            a list of 100 urls of first 10 pages of search result links
        """
        # TODO: handle logic such that 100 urls are got using different apis.
        self._100urls = self._get_from_api()
        log("main", "info", "Got 100 search URLs")
        log("requestinggoogle", "info", "Got 100 search URLs")

        return self._100urls

    def _get_all_apis(self):
        """
        Parse out all the configuration for apis listed in format:
            API<N>
            api_key = ""
            search_engine_id = ""
        and creates a Google API object and appends it to self.google_a
        """
        # First three letters API
        log("requestinggoogle", "info", "Getting APIs.")
        apis = [api for api in self._parser.sections() if api[0:3] == "API"]

        for api in apis:
            self._google_apis.append(
                GoogleAPI(
                    self._parser.get(api, "api_key"),
                    self._parser.get(api, "search_engine_id"),
                )
            )

    def _get_from_api(self):

        """
        Checks if API is available and if it is available, recursively gets 100 urls in
        10 iterations.
        """
        # If available, take the first one available.
        apis = [curr_api for curr_api in self._google_apis if curr_api._is_available()]
        api = apis[0]
        log("requestinggoogle", "info", f"Using {api.API_KEY}")

        search_results = []

        # 11, 21, 31, ..., 91
        SEARCH_INDEX_STEP = 10
        for i in range(
            1, self._parser.getint("global", "num_links"), SEARCH_INDEX_STEP
        ):
            search_result, api = api.search(
                search_query=self._parser.get("global", "search_query"),
                start_index=i,  # search index for getting from paged search result.
                api=api,  # if api is invalid, to return the api
                apis=self._google_apis,
            )
            try:
                # {items: {link: 'www.example.com'}} for all pages.
                if len(search_result) > 1:
                    search_results += [item["link"] for item in search_result["items"]]
            except:
                i -= 10  # if no search result, then don't proceed the loop

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
        self._ONE_DAY = 86400
        self._SEARCH_ENGINE_ID = search_engine_id
        self._db_ref, _created = API.objects.get_or_create(
            api_key=api_key, search_engine_id=search_engine_id
        )
        if not _created:
            # Reset the usage count to 0 on next day
            self._time_elapsed = now() - self._db_ref.last_access
            if self._time_elapsed.total_seconds() > self._ONE_DAY:
                log("requestinggoogle", "info", f"API usage of {self.API_KEY} reset")
                self._db_ref.usage_count = 0

    def search(self, search_query, num_results=10, start_index=1, api=None, apis=None):
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
        api : GoogleAPI
            api being currently used
        apis : list,
            list of Google APIs

        Raises
        ------
        Exception
            If any exception is raised, it is printed.

        Returns
        -------
        response, api
        """
        try:
            # Google API usage syntax, available on google search API documentation.
            resource = build("customsearch", "v1", developerKey=self.API_KEY).cse()
            response = resource.list(
                q=search_query,
                cx=self._SEARCH_ENGINE_ID,
                num=num_results,
                start=start_index,
            ).execute()

            if response:
                # Increment usage count and set last access time to now
                self._db_ref.usage_count += 1
                self._db_ref.last_access = now()
                self._db_ref.save()

                return response, api
        except HttpError as e:
            log("main", "error", f"{e}")
            log("requestinggoogle", "error", f"{e}")
            apis = [
                curr_api
                for curr_api in apis
                if curr_api._is_available()
                and curr_api._SEARCH_ENGINE_ID != api._SEARCH_ENGINE_ID
            ]
            api = apis[0]
            log("main", "info", f"So using {api.API_KEY}")
            log("requestinggoogle", "info", f"So using {api.API_KEY}")
            return None, api

        except Exception as e:
            log("main", "error", f"{e}")
            log("requestinggoogle", "error", f"{e}")
            return None, api

    def _is_available(self):
        """
        Checks if an api is available.

        Checks elapsed time from last used time and checks if one day has elapsed
        and API limit has been crossed for today.

        Returns
        -------
        Boolean
            True if an API usage limit for the day hasn't exceeded.
            False else.
        """
        API_DAY_LIMIT = 100
        self._time_elapsed = now() - self._db_ref.last_access

        if (
            self._db_ref.usage_count >= API_DAY_LIMIT
            and self._time_elapsed.total_seconds() < self._ONE_DAY
        ):
            return False

        return True


if __name__ == "__main__":
    google_request = RequestGoogle()
    urls = google_request.get_100_urls()
    print(urls)
