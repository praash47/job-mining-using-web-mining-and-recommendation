import logging

from backend.baseexceptions import SomeThingNotFound

mainlogger = logging.getLogger('main')
logger = logging.getLogger('jobdetailsextractor')

class JobTitleXpathNotFound(SomeThingNotFound):
    def __init__(self, url):
        super().__init__(f'Job Title Xpath for {url} site not found')

class DeadlineNotFound(SomeThingNotFound):
    def __init__(self):
        logger.error('Deadline expired or not found')
        mainlogger.error('Deadline expired or not found')
        
        super().__init__('Deadline expired or not found')
    
class DeadlineXpathNotFound(SomeThingNotFound):
    def __init__(self):
        logger.error('Deadline Xpath not found')
        mainlogger.error('Deadline Xpath not found')
        
        super().__init__('Deadline Xpath not found')

class NameXpathNotFound(SomeThingNotFound):
    def __init__(self):
        logger.error('Name xpath not found')
        mainlogger.error('Name xpath not found')
        
        super().__init__('Name xpath not found')