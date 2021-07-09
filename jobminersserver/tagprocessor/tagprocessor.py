"""
Tag Processor:
--------------
This file is used to process related to tag.
"""
from bs4 import BeautifulSoup

class TagProcessor:
    """
    Class used in processing tags. It is used to get content from the
    tag attributes. The attribute may be a name or may be any property that
    includes both og and non og properties.
    ...
    """
    def __init__(self, html, tag=None):
        """
        Params
        """
        self.html_page = html
        self.tag_to_process = tag
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_content(self):
        if self.tag_to_process == 'title':
            title = self.soup.title
            if title: 
                title = title.string.split(' ')
                title = [word.strip(',').strip('|').strip(',').lower() for word in title]
                
                return title

    def get_content_from_name(self, name_to_get_from):
        try:
            tag = self.soup.find(self.tag_to_process, {"name":name_to_get_from})
            return tag['content']
        except:
            return ''

    def get_content_from_property(self, property_name, og=False):
        try:
            if og: property_name = "og:" + property_name 
            tag = self.soup.find(self.tag_to_process, {"property":property_name})
            return tag['content']
        except:
            return ''

