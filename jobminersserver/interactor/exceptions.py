import imp
import logging

from backend.baseexceptions import SomeThingNotFound

logger = logging.getLogger('interactor')

class SearchURLNotFound(SomeThingNotFound):
    def __init__(self, url):
        logger.error(f'Search URL for {url} site not found')
        super().__init__(f'Search URL for {url} site not found')

class NoTwoMatchingTitles(SomeThingNotFound):
    def __init__(self, url):
        message = f"Couldn't find two matching titles in first page in {url}. Hence, the site is not crawlable. Ignoring the site."
        super().__init__(message)