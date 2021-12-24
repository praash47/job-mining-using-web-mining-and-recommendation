import re
from lxml import etree
from configparser import ConfigParser

import requests
from requests.api import request
from lxml import html

import string

class Parameters:
    def __init__(self, job_block_xpath, tree, website):
        self.job_block_xpath = job_block_xpath
        self.job_block_tree = tree
        self.job_block_root = self.job_block_tree.xpath(self.job_block_xpath)[0]
        self.website = website

        self.parameters_dict = {
            "company_name":"",
            "company_info":"",
            "company_email":"",
            "location":"",
            "description":"",
            "salary":"",
            "n_vacancy":"1",
            "level":"",
            "qualifications":"",
            "experiences":"",
            "misc.":""
        }

        self.parameters_xpath_dict = {
            "company_name_xpath":"",
            "location_xpath":"",
            "description_xpath":"",
            "salary_xpath":"",
            "n_vacancy_xpath":"",
            "level_xpath":"",
            "qualifications_xpath":"",
            "experiences_xpath":""
        }

        # for parameter options
        CONFIG = '/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver/jobdetailsextractor/extraction_options.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        # interested parameters that we want to match
        self.interested_parameters = \
            self.parser.get('parameters', 'interested_parameters').split(',')
        self.interested_parameters = \
            [word.strip().lower() for word in self.interested_parameters]
        self.keywords = {}
        self.keyword_parameters = ['description', 'category', 'n_vacancy', 'location', 'level', 'salary', \
            'qualifications', 'experiences']
        
        for parameter in self.keyword_parameters:
            self.keywords[parameter] = \
                self.parser.get('parameters', parameter).split(',')
            self.keywords[parameter] = \
                [word.strip().lower() for word in self.keywords[parameter]]

        self.keywords['misc'] = \
            self.parser.get('parameters', 'misc').split(',')
        self.keywords['misc'] = \
            [word.strip().lower() for word in self.keywords['misc']]
        # symbols that we want to omit
        self.symbols_to_omit = \
            self.parser.get('parameters', 'symbols_to_omit').split(',')
    
    def get_core_parameters(self, xpaths_dict=None):
        parameters_discovered = self.get_parameters_from_node(root=self.job_block_root)

        if len(parameters_discovered) < 4 or not self.parameters_xpath_dict['description_xpath']:
            parameters_discovered = self.get_parameters_from_node(root=self.job_block_tree.getroot())
        
        self.values_from_xpaths(xpaths_dict)
        if not self.parameters_xpath_dict['company_name_xpath']:
            self.search_company_path_multiple_urls()
        print(self.parameters_xpath_dict)
        print(self.parameters_dict)


    def get_parameters_from_node(self, root):
        parameters_discovered = set()
        company_email = ""
        company_name = ""
        company_name_xpath = ""
        
        try: root = root.getparent().getchildren()
        except: pass
        
        for parent in root:
            for node in parent.iter(tag=etree.Element):
                node_text = self.clean_text(node.text_content())

                if not node.getchildren() and \
                node_text not in self.symbols_to_omit and \
                node_text in self.interested_parameters:
                    if not \
                        self.job_block_tree.getpath(node)[-2] + self.job_block_tree.getpath(node)[-1] \
                             == '/a':  #ignore a tags.
                        parameters_discovered.add(node_text)
                        self.detect_and_assign_xpath(node, node_text)
                else:
                    nested_parameter, nested_parameter_value = self.search_word_in_tag(node_text)
                    if nested_parameter_value: parameters_discovered.add(nested_parameter)

                if not node.getchildren():
                    if not company_email: company_email = self.match_company_email(node_text)
                    if not company_name: company_name, company_name_xpath = self.match_company_name(node, node_text)
        
        if company_name and company_name_xpath:
            self.parameters_dict['company_name'] = company_name
            self.parameters_xpath_dict['company_name_xpath'] = company_name_xpath

        return parameters_discovered

    def match_company_email(self, text):
        email_regex = self.parser.get('parameters', 'email_regex')
        match = re.search(email_regex, text)
        try: return match.group(0)
        except: return None

    def match_company_name(self, node, text):
        company_name_regex = self.parser.get('parameters', 'company_name_regex')
        if re.findall(company_name_regex, string.capwords(text).replace("'", "")):
            return text, self.job_block_tree.getpath(node)
        return None, None

    def search_word_in_tag(self, words):
        words_list = words.replace(':', '').split(' ')
        for word in words_list:
            if word in self.interested_parameters and word:
                return word, words_list[len(words_list) - 1]

        return None, None

    def detect_and_assign_xpath(self, node, node_text):
        for parameter in self.keyword_parameters:
            if self.get_xpath(node, node_text, parameter):
                self.parameters_xpath_dict[parameter + '_xpath'] = \
                     self.get_xpath(node, node_text, parameter)

    def get_xpath(self, node, node_text, parameter):
        if node_text == parameter or node_text in self.keywords[parameter]:
            return self.job_block_tree.getpath(node)

    def clean_text(self, text):
        text = re.sub(' +', ' ', text)
        text = text.lower().replace(':', '').replace('\\n', '').replace('\n', '').strip()
        text = text.replace('\\r', '').replace('\\s', '')

        return text

    def values_from_xpaths(self, xpaths_dict=None):
        if xpaths_dict: self.parameters_xpath_dict = xpaths_dict

        for key, value in self.parameters_xpath_dict.items():
            if value:
                node = self.job_block_tree.xpath(value)[0]
                try: 
                    if not node.getnext():
                        parent_text = self.clean_text(node.getparent().text_content())
                        
                        key = key.replace('_xpath', '')
                        for alternative_name in self.keywords[key]:
                            if alternative_name in parent_text:
                                parent_text = parent_text.replace(alternative_name, '').strip()
                                self.parameters_dict[key] = parent_text
                    else:
                        while node.getnext().text_content() in self.symbols_to_omit:
                            node = node.getnext()
                        key = key.replace('_xpath', '')
                        self.parameters_dict[key] = self.clean_text(node.getnext().text_content())
                except: pass

    def search_company_path_multiple_urls(self):
        from .models import Job
        from .main import JobDetails
        
        jobs_of_website = Job.objects.filter(website=self.website)
        for job in jobs_of_website:
            job_details = JobDetails(job.url, job.title)
            parameters = Parameters()
        #     extracted_company_name_xpath = \
        #          job_details.job_parameters.parameters_xpath_dict['company_name_xpath']
        #     if extracted_company_name_xpath:
        #         self.parameters_xpath_dict['company_name_xpath'] = extracted_company_name_xpath
        #     if self.parameters_xpath_dict['company_name_xpath']: break