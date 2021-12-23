import re
from lxml import etree
from configparser import ConfigParser

class Parameters:
    def __init__(self, job_block_xpath, tree):
        self.job_block_xpath = job_block_xpath
        self.job_block_tree = tree
        self.job_block_root = self.job_block_tree.xpath(self.job_block_xpath)[0]

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

    def get_from_structured_layout(self):   
        print(self.interested_parameters)
        for parent in self.job_block_root.getparent().getchildren():
            for node in parent.iter(tag=etree.Element):
                if not node.getchildren() and \
                node.text_content() not in self.symbols_to_omit and \
                node.text_content().lower() in self.interested_parameters:
                    if self.match_company_email(node.text_content()):
                        print(self.match_company_email(node.text_content()))
                    print(node.text_content().replace("\n", "").lower())
                    print(self.job_block_tree.getpath(node))
                else:
                    for parameters in self.interested_parameters:
                        if parameters in node.text_content().lower():
                            pass
                            # print(node.text_content())

    def match_company_email(self, text):
        email_regex = self.parser.get('parameters', 'email_regex')
        match = re.search(email_regex, text)
        if match.group(0): return match.group(0)
        
        return None

    def search_for_rest_layout(self):
        pass

    def match_company_name(self, text):
        regex = r"\b[A-Z]\w+(?:\.com?)?(?:[ -]+(?:&[ -]+)?[A-Z]\w+(?:\.com?)?){0,2}[,\s]+(?i:ltd|llc|school|limited|service|services|organization|agency|corps|company|corporation|society|international|builder|clinic|inc|pvt|plc|co(?:rp)?|group|holding|gmbh)\b"
        return(re.findall(regex, text))

