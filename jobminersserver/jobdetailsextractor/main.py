# from jobminersserver.requestutils.request import Request
from deadline import Deadline
import requests
from lxml import html, etree
from configparser import ConfigParser

import re

class JobDetails:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.html_page = requests.get(self.url).content
        self.html_page = re.subn(r'<(script).*?</\1>(?s)', '', str(self.html_page))[0]
        # self.html_page = None
        # self.request = Request(url)
        self.tree = None
        self.deadline = Deadline()
        self.job_block_xpath = None

        # for parameter options
        CONFIG = '/home/aasis/Documents/job-mining-using-web-mining-and-recommendation/jobminersserver/jobdetailsextractor/extraction_options.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        # interested parameters that we want to match
        self.interested_parameters = \
            self.parser.get('parameters', 'interested_parameters').split(',')
        self.interested_parameters = \
            [word.strip().lower() for word in self.interested_parameters]
        # symbols that we want to omit
        self.symbols_to_omit = \
            self.parser.get('parameters', 'symbols_to_omit').split(',')

    def fetch(self):
        # self.html_page = self.request.request_html()
        # self.tree = self.request.request_html_tree()
        resp_html = html.fromstring(self.html_page)
        self.tree = resp_html.getroottree()
    
    def extract_parameters(self):
        self.job_block_xpath = self.get_job_block_xpath()
        self.get_core_parameters()

    def get_job_block_xpath(self):
        self.deadline.tree = self.tree
        self.deadline.get_deadline_date(self.html_page)
        name_xpath = self.get_name_xpath()
        
        common_xpath = self.common_start(self.deadline.xpath, name_xpath)
        common_xpath_list = common_xpath.split('/')
        job_block_xpath = '/'.join(common_xpath_list[:len(common_xpath_list)-1])

        return job_block_xpath

    def get_core_parameters(self):
        job_block_root = self.tree.xpath(self.job_block_xpath)[0]
        for parent in job_block_root.getparent().getchildren():
            for node in parent.iter(tag=etree.Element):
                print(node.text_content())
                if not node.getchildren() and \
                node.text_content() not in self.symbols_to_omit and \
                node.text_content() in self.interested_parameters:
                    print(node.text_content())

    def get_name_xpath(self):
        name_xpaths = self.tree.xpath(f'//*[text()="{self.name}"]')
        title_xpaths = []
        if len(name_xpaths) == 1:
            title_xpaths.append(self.tree.getpath(name_xpaths[0]))
        else:
            for xpath in name_xpaths:
                if re.search('^h[1-6]$', xpath.tag):
                    element = self.tree.xpath(f"//{xpath.tag}[contains(text(), '{str(xpath.text_content())}')]")[0]
                    title_xpaths.append(self.tree.getpath(element))
        
        return title_xpaths[0]

    @staticmethod
    def common_start(sa, sb):
        """
        Returns the longest common substring from the beginning of sa and sb

        Parameters
        ----------
        sa: string
            string 'a' to compare
        sb: string
            string 'b' to compare
        # ref: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
        
        Returns
        -------
        string
            common part between sa and sb.
        """
        def _iter():
            for a, b in zip(sa, sb):
                if a == b:
                    yield a
                else:
                    return

        return ''.join(_iter())

if __name__ == '__main__':
    job_details = JobDetails('https://www.kumarijob.com/premiumjob/technical-support/34908', 'Technical Support')
    job_details.fetch()
    job_details.extract_parameters()