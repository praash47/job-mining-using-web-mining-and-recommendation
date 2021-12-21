import re
from lxml import etree
from configparser import ConfigParser

class Parameters:
    def __init__(self, job_block_xpath, tree):
        self.job_block_xpath = job_block_xpath
        self.job_block_tree = tree
        self.job_block_root = self.job_block_tree.xpath(self.job_block_xpath)[0]

        # for parameter options
        CONFIG = '/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver/jobdetailsextractor/extraction_options.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        # interested parameters that we want to match
        self.interested_parameters = \
            self.parser.get('parameters', 'interested_parameters').split(',')
        self.interested_parameters = \
            [word.strip().lower().replace('|', ',') for word in self.interested_parameters]
        # symbols that we want to omit
        self.symbols_to_omit = \
            self.parser.get('parameters', 'symbols_to_omit').split(',')
    
    def get_core_parameters(self):
        parameters_discovered = self.get_parameters_from_node(root=self.job_block_root)
        
        if len(parameters_discovered) < 100:
            parameters_discovered = self.get_parameters_from_node(root=self.job_block_tree.getroot())

        print(parameters_discovered)

    def get_parameters_from_node(self, root):
        parameters_discovered = set()
        try: root = root.getparent().getchildren()
        except: pass
        for parent in root:
            for node in parent.iter(tag=etree.Element):
                node_text = re.sub(' +', ' ', node.text_content())
                node_text = node_text.lower().replace(':', '').replace('\\n', '').replace('\n', '').strip()
                if not node.getchildren() and \
                node_text not in self.symbols_to_omit and \
                node_text in self.interested_parameters:
                    parameters_discovered.add(node_text)
                    print(node_text)
                    print(self.job_block_tree.getpath(node))
                else:
                    nested_parameter, nested_parameter_value = self.search_word_in_tag(node_text)
                    if nested_parameter_value: parameters_discovered.add(nested_parameter)
        return parameters_discovered

    def match_company_email(self, text):
        email_regex = self.parser.get('parameters', 'email_regex')
        match = re.search(email_regex, text)
        try: return match.group(0)
        except: return None

    def search_word_in_tag(self, words):
        words_list = words.replace(':', '').split(' ')
        for word in words_list:
            if word in self.interested_parameters and word:
                return word, words_list[len(words_list) - 1]
        
        return None, None
