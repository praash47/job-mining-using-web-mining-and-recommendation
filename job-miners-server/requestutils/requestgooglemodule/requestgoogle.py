from googleapiclient.discovery import build

from configparser import ConfigParser
import time


CONFIG = 'job-miners-server/requestutils/requestgooglemodule/googleapis.ini'


class RequestGoogle:
    def __init__(self):
        self._100urls = []
        
        self.time = time.time()

        # Parser
        self.parser = ConfigParser()
        self.parser.read(CONFIG)

    def get_100_urls(self):
        # TODO: handle logic such that 100 urls are got using different apis. 
        self._100urls = self.get_from_api()

        return self._100urls

    def get_from_api(self):
        api = GoogleAPI(

            api_key=self.parser.get('API', 'api_key'),
            search_engine_id=self.parser.get('API', 'search_engine_id')
        )
        search_results = []
        for i in range(1, self.parser.getint('global', 'num_links'), 10): 
            search_result = api.search(
                search_query=self.parser.get('global', 'search_query'),
                start_index=i
            )
            search_results += [item['link'] for item in search_result['items']]

        return search_results

class GoogleAPI:
    def __init__(self, api_key, search_engine_id):
        self.API_KEY = api_key
        self.SEARCH_ENGINE_ID = search_engine_id
        self.usage_count = 0
        self.last_used_up_date_time = ''

    def search(self, search_query, num_results=10, start_index=1):
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
                return response
        except Exception as e:
            print(e)
            return None

if __name__ == "__main__":
    google_request = RequestGoogle() 
    urls = google_request.get_100_urls()
    print(urls)