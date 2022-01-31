import logging
import re

from lxml import html
from requests import *
from urllib import parse

mainlogger = logging.getLogger('main')


class Request:
    """
    A class to request html of webpage from urls
    and convert to text 

    Methods
    -------
    request_html(url)
            returns html in string from the url passed 

    check_homepage(url)
            returns true if url passed is homepage and has no subdomain

    get_only_homepage_based(urls)
            returns only the homepage based in urls list

    get_html_tree()
            returns the html tree

    filter_script_tags()
            filters the script tags from the html.
    """

    def __init__(self, url):
        """
        Parameters
        ---------
        url : str
                url of the webpages
        """
        self.url = url
        self.html = None

    def check_homepage(self):
        """
        Returns true if url is the homepage of the site
        returns false otherwise

        Parameters
        ----------
        home_page: str
                home page of the url

        format: https://merojob.com
        """
        home_page = parse.urlsplit(self.url).scheme + \
            '://' + parse.urlsplit(self.url).netloc + '/'

        if(self.url == home_page):
            return True
        return False

    def get_only_homepage_based(self, urls=None):
        """
        Returns homepage from the extracted url

        eg:- https://unjobs.org from https://unjobs.org/duty_stations/nepal

        Paramters
        ---------
        home_page: list
                homepage of the urls in the format https://unjobs.org
        """
        home_page = ''
        if urls:
            home_page = [(parse.urlsplit(url).scheme + '://' + parse.urlsplit(url).netloc)
                         for url in urls if (parse.urlsplit(url).scheme + '://' + parse.urlsplit(url).netloc) != '://']
        if (parse.urlsplit(self.url).scheme + '://' + parse.urlsplit(self.url).netloc) != '://':
            home_page = parse.urlsplit(
                self.url).scheme + '://' + parse.urlsplit(self.url).netloc
        return home_page

    def request_html(self):
        """
        Returns html from the url of the webpages.

        If webpage is not accessible print error message 
        """
        try:
            self.html = get(self.url).text
        except Exception as e:
            mainlogger.error(
                f'Error while requesting {self.url}: {e}\n so returning ""')
            return ""
        return self.html

    def get_html_tree(self):
        """
        Creates a html tree using lxml out of the current
        object's HTML document and Returns the HTML tree.

        Requirement: HTML document present in html variable.

        Returns
        -------
        tree: lxml.etree
                tree that is computed from the html dom.
        """
        if self.html:
            html_doc = html.fromstring(self.html)
            tree = html_doc.getroottree()

            return tree
        return None

    def filter_unnecessary_tags(self):
        """
        Filters/Removes the script tags from the request html and assigns back to
        request html.
        """
        self.html = re.subn(r'<(script).*?</\1>(?s)', '', str(self.html))[0]
        self.html = re.subn(r'<(footer).*?</\1>(?s)', '', str(self.html))[0]
        self.html = re.subn(r'<(header).*?</\1>(?s)', '', str(self.html))[0]


if __name__ == "__main__":
    # urls = 'https://nepalhealthjob.com/'

    # R1 = Request(urls)
    # print(R1.request_html())

    req = Request("https://merojob.com/search?q=")
    print(req.get_only_homepage_based())
