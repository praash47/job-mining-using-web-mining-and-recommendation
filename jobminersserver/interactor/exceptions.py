"""
This file consists of exceptions related to the interactor module. The exceptions are self explanatory with it's name.

Exceptions
----------
* SearchURLNotFound
* NoTwoMatchingTitles
* DriverNotFound
"""
from backend.baseexceptions import SomeThingNotFound
from backend.misc import log


class SearchURLNotFound(SomeThingNotFound):
    def __init__(self, url):
        log("interactor", "error", f"Search URL for {url} site not found")
        super().__init__(f"Search URL for {url} site not found")


class NoTwoMatchingTitles(SomeThingNotFound):
    def __init__(self, url):
        message = f"Couldn't find two matching titles in first page in {url}. Hence, the site is not crawlable. Ignoring the site."
        super().__init__(message)


class DriverNotFound(SomeThingNotFound):
    def __init__(self):
        log("interactor", "error", f"Web Driver not found")
        super().__init__(f"Web Driver not found")
