from backend.baseexceptions import SomeThingNotFound

class JobTitleXpathNotFound(SomeThingNotFound):
    def __init__(self, url):
        super().__init__(f'Job Title Xpath for {url} site not found')