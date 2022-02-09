"""
This module consists of exceptions for the jobdetailsextractor module for exceptions for JobTitleXpath, Deadline, DeadlineXpath, NameXpath not being found.
"""
from backend.baseexceptions import SomeThingNotFound
from backend.misc import log


class JobTitleXpathNotFound(SomeThingNotFound):
    def __init__(self, url):
        super().__init__(f"Job Title Xpath for {url} site not found")


class DeadlineNotFound(SomeThingNotFound):
    def __init__(self):
        log("jobdetailsextractor", "error", "Deadline expired or not found")
        log("main", "error", "Deadline expired or not found")

        super().__init__("Deadline expired or not found")


class DeadlineXpathNotFound(SomeThingNotFound):
    def __init__(self):
        log("jobdetailsextractor", "error", "Deadline Xpath not found")
        log("main", "error", "Deadline Xpath not found")

        super().__init__("Deadline Xpath not found")


class NameXpathNotFound(SomeThingNotFound):
    def __init__(self):
        log("jobdetailsextractor", "error", "Name xpath not found")
        log("main", "error", "Name xpath not found")

        super().__init__("Name xpath not found")
