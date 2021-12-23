import re
from lxml import etree
from configparser import ConfigParser

class Parameters:
    def __init__(self, job_block_xpath, tree):
        self.job_block_xpath = job_block_xpath
        self.job_block_tree = tree
        self.job_block_root = self.job_block_tree.xpath(self.job_block_xpath)[0]

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
    
    def get_core_parameters(self):
        self.get_from_structured_layout()
        self.search_for_rest_layout()

    def get_parameters_from_node(self, root):
        parameters_discovered = set()
        company_email = ""
        company_name = ""
        try: root = root.getparent().getchildren()
        except: pass
        print(self.job_block_xpath)
        for parent in root:
            for node in parent.iter(tag=etree.Element):
                if not node.getchildren() and \
                node_text not in self.symbols_to_omit and \
                node_text in self.interested_parameters:
                    parameters_discovered.add(node_text)
                    if node.getnext() is not None and node.getnext().text_content() == ":": 
                        print(node.getnext().getnext().text_content())
                    elif node.getnext() is not None:
                        print(node.getnext().text_content())
                    else:
                        pass
                    print(node_text)
                    print(self.job_block_tree.getpath(node))
                else:
                    nested_parameter, nested_parameter_value = self.search_word_in_tag(node_text)
                    if nested_parameter_value: parameters_discovered.add(nested_parameter)

                if not node.getchildren():
                    company_email = self.match_company_email(node_text)
                    company_name = self.match_company_name(node_text)
                

        print(company_email)
        print(company_name)

        return parameters_discovered


    def match_company_email(self, text):
        email_regex = self.parser.get('parameters', 'email_regex')
        match = re.search(email_regex, text)
        if match.group(0): return match.group(0)
        
        return None

    def search_for_rest_layout(self):
        pass

    def match_company_name(self, text):
        regex = r"\b[A-Z]\w+(?:\.com?)?(?:[ -]+(?:&[ -]+)?[A-Z]\w+(?:\.com?)?){0,2}[,\s]+(?i:ltd|llc|school|limited|service|services|organization|agency|corps|company|corporation|society|international|builder|clinic|inc|pvt|pvt.|plc|co(?:rp)?|group|holding|gmbh)\b"
        return(re.findall(regex, text))

    def search_word_in_tag(self, words):
            words_list = words.replace(':', '').split(' ')
            for word in words_list:
                if word in self.interested_parameters and word:
                    return word, words_list[len(words_list) - 1]

            return None, None