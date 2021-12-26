import re
from lxml import etree
from configparser import ConfigParser
import spacy

from requests.api import request
from nltk.tokenize import RegexpTokenizer

import string

class Parameters:
    def __init__(self, job_block_xpath, tree, web_structure, website=None):
        self.job_block_xpath = job_block_xpath
        self.job_block_tree = tree
        self.job_block_root = self.job_block_tree.xpath(self.job_block_xpath)[0]
        self.web_structure = web_structure
        self.website = website
        self.nlp = spacy.load("en_core_web_lg")

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
            "misc":""
        }

        self.parameters_xpath_dict = {
            "company_name_xpath":"",
            "company_info_xpath":"",
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
            'qualifications', 'experiences', 'misc']
        
        for parameter in self.keyword_parameters:
            self.keywords[parameter] = \
                self.parser.get('parameters', parameter).split(',')
            self.keywords[parameter] = \
                [word.strip().lower().replace('|', ',') for word in self.keywords[parameter]]

        # symbols that we want to omit
        self.symbols_to_omit = \
            self.parser.get('parameters', 'symbols_to_omit').split(',')
    
    def get_core_parameters(self, xpaths_dict=None):
        parameters_discovered = self.get_parameters_from_node(root=self.job_block_root, xpaths_dict=xpaths_dict)

        if len(parameters_discovered) < 4 or not self.parameters_xpath_dict['description_xpath']:
            parameters_discovered = self.get_parameters_from_node(root=self.job_block_tree.getroot(), xpaths_dict=xpaths_dict)
        
        self.values_from_xpaths(xpaths_dict)
        self.parameters_dict['description'] = self.get_paragraph_values(self.keywords['description'])
        self.parameters_dict['misc'] += self.get_paragraph_values(self.keywords['misc'])
        self.store_xpaths(xpaths_dict)

    def get_parameters_from_node(self, root, xpaths_dict):
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
                node_text in self.interested_parameters and \
                not xpaths_dict:
                    if not \
                        self.job_block_tree.getpath(node)[-2] + self.job_block_tree.getpath(node)[-1] \
                             == '/a':  #ignore a tags.
                        parameters_discovered.add(node_text)
                        self.detect_and_assign_xpath(node, node_text)
                elif not xpaths_dict:
                    nested_parameter, nested_parameter_value = self.search_word_in_tag(node_text)
                    if nested_parameter_value: parameters_discovered.add(nested_parameter)

                already_company_name, already_company_info = None, None
                try: 
                     already_company_name = xpaths_dict['company_name_xpath']
                     already_company_info = xpaths_dict['company_info_xpath']
                except: pass

                if not node.getchildren() and not already_company_name and not already_company_info:
                    if not company_email: company_email = self.match_company_email(node_text)
                    if not company_name: company_name, company_name_xpath = self.match_company_name(node_text, node)
        
        if company_name and company_name_xpath:
            self.parameters_dict['company_name'] = company_name
            self.parameters_xpath_dict['company_name_xpath'] = company_name_xpath
            self.find_company_info(company_name, company_name_xpath)

        return parameters_discovered

    def match_company_email(self, text):
        email_regex = self.parser.get('parameters', 'email_regex')
        match = re.search(email_regex, text)
        try: return match.group(0)
        except: return None

    def match_company_name(self, text, node):
        if isinstance(text, str) and not node.tag=='title':
            company_name_regex = self.parser.get('parameters', 'company_name_regex')
            nlp_res = self.nlp(text)
            for ent in nlp_res.ents:
                if ent.label == 'ORG':
                    return ent.text, self.self.job_block_tree.getpath(node)
            if re.findall(company_name_regex, string.capwords(text).replace("'", "")):
                return re.findall(company_name_regex, string.capwords(text).replace("'", ""))[0], self.job_block_tree.getpath(node)
            return None, None
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

    def find_company_info(self, company_name, company_name_xpath):
        tokenizer = RegexpTokenizer(r'\w+')
        tokenized = tokenizer.tokenize(company_name)

        tags_interested_in = ['a', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']
        all_nodes_with_token = set()
        for token in tokenized:
            nodes_matched = self.job_block_tree.xpath(f"//*[contains(text(),'{token}')]")
            for node in nodes_matched:
                if node.tag in tags_interested_in:
                    all_nodes_with_token.add(node)
        all_text_content = set()
        for node in all_nodes_with_token:
            all_text_content.add(node.text_content())
        all_text_content = list(sorted(all_text_content, key = len))
        try:
            print(self.job_block_tree.xpath(f"//*[contains(text(),'{all_text_content[0]}')]"))
            # self.parameters_xpath_dict['company_info_x']
            self.parameters_xpath_dict['company_info_xpath'] = self.job_block_tree.getpath(
                self.job_block_tree.xpath(f"//*[contains(text(),'{all_text_content[1]}')]")[0]
            )
            self.parameters_dict['company_info'] += self.clean_text(all_text_content[1])
        except: pass

        try:
            for node in self.job_block_tree.getpath(self.parameters_xpath_dict['company_info_xpath']).getparent()[0].iter(tag=etree.Element):
                self.parameters_dict['company_info'] += self.clean_text(node.text_content())
        except: pass

    def values_from_xpaths(self, xpaths_dict):
        company_name_xpath = self.parameters_xpath_dict['company_name_xpath']
        company_info_xpath = self.parameters_xpath_dict['company_info_xpath']
        if xpaths_dict: self.parameters_xpath_dict = xpaths_dict
        self.parameters_xpath_dict['company_name_xpath'] = company_name_xpath
        self.parameters_xpath_dict['company_info_xpath'] = company_info_xpath

        for key, value in self.parameters_xpath_dict.items():
            if value:
                try: 
                    node = self.job_block_tree.xpath(value)[0]
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

        # misc text property extraction
        for parent in self.job_block_tree.getroot():
            for node in parent.iter(tag=etree.Element):
                node_text = self.clean_text(node.text_content())

                if not node.getchildren() and \
                node_text not in self.symbols_to_omit and \
                node_text in self.interested_parameters:
                    self.assign_misc_parameters_value(node, node_text)

    def assign_misc_parameters_value(self, node, node_text):
        if node_text in self.keywords['misc']:
            self.parameters_dict['misc'] += node_text + ': '
            try: 
                while node.getnext().text_content() in self.symbols_to_omit:
                    node = node.getnext()
                self.parameters_dict['misc'] += self.clean_text(node.getnext().text_content()) + '\n'
            except: pass
        
    def get_paragraph_values(self, keywords):
        found_title = False
        paragraph = ''
        repeat_keywords = []
        other_keywords = []
        common_parent = None
        for parameter in self.keyword_parameters:
            for keyword in self.keywords[parameter]:
                if keyword not in keywords:
                    other_keywords.append(keyword)

        for parent in self.job_block_tree.getroot():
            for node in parent.iter(tag=etree.Element):
                node_text = self.clean_text(node.text_content())
                if not node.getchildren() and node_text:
                    if found_title and node_text not in other_keywords:
                        if common_parent:
                            if id(self.get_parent(node)) != id(common_parent): 
                                found_title = False
                                continue
                        paragraph += node_text + '\n'
                    elif node_text in other_keywords:
                        found_title = False
                    if node_text in keywords and node_text not in repeat_keywords:
                        found_title = True
                        if node_text in self.keywords['misc']:
                            paragraph += node_text + '\n'
                        repeat_keywords.append(node_text)
                        try:
                            if len(self.get_parent(node).getchildren()) < 2:
                                common_parent = self.get_parent(node).getnext()
                            else: common_parent = self.get_parent(node)
                        except: pass
        return paragraph

    def get_parent(self, node):
        parent = node.getparent()
        while not parent.tag == 'div':
            parent = parent.getparent()
        return parent
                        
    def store_xpaths(self, xpaths_dict):
        if not xpaths_dict:
            self.web_structure.location_xpath = self.parameters_xpath_dict['location_xpath']
            self.web_structure.job_description_xpath = self.parameters_xpath_dict['description_xpath']
            self.web_structure.salary_xpath = self.parameters_xpath_dict['salary_xpath']
            self.web_structure.no_vacancy_xpath = self.parameters_xpath_dict['n_vacancy_xpath']
            self.web_structure.level_xpath = self.parameters_xpath_dict['level_xpath']
            self.web_structure.qualification_xpath = self.parameters_xpath_dict['qualifications_xpath']
            self.web_structure.experience_xpath = self.parameters_xpath_dict['experiences_xpath']
        if not self.web_structure.company_name_xpath and not self.web_structure.company_description_xpath:
            if self.parameters_xpath_dict['company_name_xpath'] and self.parameters_xpath_dict['company_info_xpath']: 
               self.web_structure.company_name_xpath = self.parameters_xpath_dict['company_name_xpath'] 
               self.web_structure.company_description_xpath = self.parameters_xpath_dict['company_info_xpath']
        self.web_structure.save()