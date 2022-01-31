"""
This submodule deals with complexities of extraction of parameters from the Job Advertisement HTML document. This includes all of the parameters like Job Location, Job Description, Job Salary, Company Name etc.

Classes
-------
Parameters()
    Parameters abstracts all the details for extraction of the parameters
"""
import re
import string
import logging
import spacy


from backend.misc import read_config, try_and_pass
from tagprocessor.decorators import for_existing_leaf_nodes
from tagprocessor.misc import clean_text

logger = logging.getLogger('jobdetailsextractor')
mainlogger = logging.getLogger('main')


class Parameters:
    """
    Parameters extract the parameters of a job advertisement.

    This involves:
    1. Extraction of the parameters values from node like location, salary, description etc and it's xpaths in the HTML document.
    2. Extraction of the Values from Xpaths
        2.1. Involves to extracting value from the next node of the xpath of the parameter.
        2.2. Paragraph values are got out then by collecting values from some nodes after the discovered parameters. This is valid for parameters like description, specifications etc.
    """
    def __init__(self, job_block_xpath, tree, website=None):
        """
        Initializes Parameters object

        Parameters
        ----------
        job_block_xpath: str
            block of the job where the most of the job details are expected to be present
        tree: lxml.etree
            tree of the HTML document
        website: JobWebsite
            JobWebsite that we are currently working on
        """
        self.job_block_xpath = job_block_xpath
        self.job_block_tree = tree

        # If no any job_block_xpath, then use the root of the current tree as the job block root node
        if job_block_xpath == '/':
            self.job_block_root = self.job_block_tree.getroot()
        else:
            self.job_block_root = self.job_block_tree.xpath(self.job_block_xpath)[0]
        self.website = website

        # Loading of the NLP module for company name extraction
        self.nlp = spacy.load("en_core_web_lg")

        # Parameters and Parameters Xpath Structured Storage
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
            "location_xpath":"",
            "description_xpath":"",
            "salary_xpath":"",
            "n_vacancy_xpath":"",
            "level_xpath":"",
            "qualifications_xpath":"",
            "experiences_xpath":""
        }

        # for parameter options
        self.parser = read_config("jobdetailsextractor/reqs/extraction_options.ini")
        # interested parameters that we want to match
        self.interested_parameters = \
            self.parser.get('parameters', 'interested_parameters').split(',')
        self.interested_parameters = \
            [word.strip().lower() for word in self.interested_parameters]

        # Our keywords for parameters (Our naming convention / identification for the job parameters)
        self.keywords = {}
        self.keyword_parameters = ['description', 'category', 'n_vacancy', 'location', 'level', 'salary', \
            'qualifications', 'experiences', 'misc']
        
        # Getting the alternative name of the paramaters for each parameter.
        for parameter in self.keyword_parameters:
            self.keywords[parameter] = \
                self.parser.get('parameters', parameter).split(',')
            self.keywords[parameter] = \
                [word.strip().lower().replace('|', ',') for word in self.keywords[parameter]]

        # symbols that we want to omit
        self.symbols_to_omit = \
            self.parser.get('parameters', 'symbols_to_omit').split(',')
    
    def get_core_parameters(self):
        """
        Gets out the core parameters from the HTML document of the job advertisement. Extracts out both single word, multi word and paragraph values.
        """
        # Discover parameters by iterating through each leaf node inside the job block tree.
        parameters_discovered = self.get_parameters_from_node(root=self.job_block_root)

        if parameters_discovered:
            # If not enough parameters discovered, then, use the root of the node to search the whole document.
            if len(parameters_discovered) < 4 or not self.parameters_xpath_dict['description_xpath']:
                parameters_discovered = self.get_parameters_from_node(root=self.job_block_tree.getroot())
        
        logger.info(f"Core parameters discovered: {parameters_discovered}")
        
        # Xpaths are also assigned while in discovery of parameters. We get the values from the xpaths now
        self.values_from_xpaths()

        # Values from xpaths cannot extract paragraph values. So, extraction of paragraph base values like description, misc etc.
        self.parameters_dict['description'] = self.get_paragraph_values(self.keywords['description'])
        self.parameters_dict['misc'] = self.get_paragraph_values(self.keywords['misc'])

    def get_parameters_from_node(self, root):
        """
        Returns the parameters discovered from the HTML document and assigns its xpaths into the self.parameters_xpath_dict. Applies some special techniques for company name and company email.

        Parameters
        ----------
        root: lxml.HtmlElement
            root node to iterate in the child (leaf) nodes on

        Returns
        -------
        set
            set of parameters discovered under the root node
        """
        # Get adjacent or sibling root nodes
        check_root = try_and_pass(lambda root: root.getparent().getchildren())
        root = check_root(root) or root

        @for_existing_leaf_nodes
        def get_parameters(node, **kwargs):
            node_text = kwargs.get('node_text')
            obj = kwargs.get('obj')
            parameters_discovered = obj['parameters_discovered']
            company_name = obj['company_name']
            company_email = obj['company_email']

            @try_and_pass
            def try_extracting():
                if node_text not in self.symbols_to_omit and \
                    node_text in self.interested_parameters:
                        if not \
                        self.job_block_tree.getpath(node)[-2] + self.job_block_tree.getpath(node)[-1] \
                            == '/a':  #ignore a tags.
                            parameters_discovered.add(node_text)
                            self.detect_and_assign_xpath(node, node_text)

                            # Search word in the tag. i.e. Nested inside the tag.
                            nested_parameter, nested_parameter_value = self.search_word_in_tag(node_text)
                            if nested_parameter_value: parameters_discovered.add(nested_parameter)

            # Try to get out company name and company email
            if not company_email: company_email = self.match_company_email(node_text)
            if not company_name: company_name = self.match_company_name(node_text, node)

            try_extracting()
            
            obj['parameters_discovered'] = parameters_discovered
            obj['company_name'] = company_name
            obj['company_email'] = company_email
            
            return parameters_discovered, company_name, company_email

        obj = {
            'parameters_discovered': set(),
            'company_name': '',
            'company_email': ''
        }
        get_parameters(
            root=root,
            obj=obj
        )
    
        self.parameters_dict['company_name'] = obj['company_name']
        self.parameters_dict['company_email'] = obj['company_email']
        # self.find_company_info(company_name)
        
        logger.info(f"company name and email found: {obj['company_name']} and {obj['company_email']}")

        return obj['parameters_discovered']

    def detect_and_assign_xpath(self, node, node_text):
        """
        Detects the xpath of the parameter and assign its xpath inside the self.parameters_xpath_dict.

        Parameters
        ----------
        node: lxml.HtmlElement
            node to find xpath of
        node_text: str
            node text of the node to find xpath of
        """
        for parameter in self.keyword_parameters:
            path = self.get_xpath(node, node_text, parameter)
            if path:
                self.parameters_xpath_dict[parameter + '_xpath'] = path

    def values_from_xpaths(self):
        """
        Extracts and assign single word and multi word (not paragraph values) from the parameters xpaths already obtained.
        """
        for key, value in self.parameters_xpath_dict.items():
            if value:
                @try_and_pass
                def get_next_value(key):
                    """
                    Gets next node value of the parameter node
                    """
                    node = self.job_block_tree.xpath(value)[0]
                    # If there is no next node
                    if not node.getnext():
                        # Get the parent text of the ndoe
                        parent_text = clean_text(node.getparent().text_content())
                        
                        key = key.replace('_xpath', '')
                        # Check if the parameter name or alternative name is present in the parent node text, if present. This is the nested form of the parameter value like
                        # <span>Location: Kathmandu</span>
                        # Replace alternative_name, like Replace Location above and get Kathmandu
                        self.parameters_dict[key] = [parent_text.replace(alternative_name, '').strip() for alternative_name in self.keywords[key] if alternative_name in parent_text][0]
                                
                    else:
                        # There is next node
                        while node.getnext().text_content() in self.symbols_to_omit:
                            node = node.getnext()
                        key = key.replace('_xpath', '')
                        # Get the text of the next node
                        self.parameters_dict[key] = self.clean_text(node.getnext().text_content())
                get_next_value(key)
                logger.info(f"Values are got from xpath")

        # Assign the miscellaneous parameters that are discovered
        @for_existing_leaf_nodes
        def assign_misc_parameters(node, **kwargs):
            node_text = kwargs.get('node_text')
            if node_text not in self.symbols_to_omit and \
            node_text in self.interested_parameters:
                self.assign_misc_parameters_value(node, node_text)
        
        assign_misc_parameters(root=self.job_block_root)
        
    def get_paragraph_values(self, keywords):
        """
        Returns the paragraph values of the nodes with keywords inside the text.

        Parameters
        ----------
        keywords
            keywords of which to extract paragraph values of
        
        Returns
        -------
        str
            string of the paragraph values thus extracted
        """
        # Keywords except the keywords mentioned in the parameter passed in the keyword
        other_keywords = (keyword for parameter in self.keyword_parameters for keyword in self.keywords[parameter] if keyword not in keywords)

        @for_existing_leaf_nodes
        def check_paragraph(node, **kwargs):
            node_text = kwargs.get('node_text')
            obj = kwargs.get('obj')
            found_title = obj['found_title']
            repeat_keywords = obj['repeat_keywords']
            paragraph = obj['paragraph']
            common_parent = obj['common_parent']

            # If title is found
            if found_title \
            and node_text not in other_keywords:
                # Same parent is not found
                if common_parent \
                and id(self.get_parent(node)) != id(common_parent):
                    # Stop the collection when parents don't match
                    found_title = False
                    return ''
                paragraph += node_text + '\n'
            
            # Stop the paragraph collection
            elif node_text in other_keywords:
                found_title = False
            
            if node_text in keywords and node_text not in repeat_keywords:  # Exclude repeated keywrods
                found_title = True
                
                paragraph += node_text + '\n' if node_text in self.keywords['misc'] else ''

                repeat_keywords.append(node_text)
                
                # Getting of the common parent
                get_common_parent = try_and_pass(lambda node: self.get_parent(node).getnext() if len(self.get_parent(node).getchildren()) < 2 else self.get_parent(node))
                get_common_parent(node)


            obj['found_title'] = found_title
            obj['repeat_keywords'] = repeat_keywords
            obj['paragraph'] = paragraph
            obj['common_parent'] = common_parent

            return paragraph

        obj =  {
            'found_title': False, 
            'repeat_keywords': [],
            'paragraph': '',
            'common_parent': ''
        }          
        check_paragraph(
            root=self.job_block_root,
            obj=obj
        )
        logger.info(f'{obj["paragraph"]}')


        return obj['paragraph']

    # Utilities
    def match_company_email(self, text):
        """
        Tries to match the company email if the company email is in the text.

        Parameters
        ----------
        text: str
            text to match company email on

        Returns
        -------
        str or None
            str of the email if found else None
        """
        email_regex = self.parser.get('parameters', 'email_regex')
        # Match with the email regex
        match = re.search(email_regex, text)
        try: 
            return match.group(0)
        except: return None

    def match_company_name(self, text, node):
        """
        Tries to match the company name if the company name is in the text.

        Parameters
        ----------
        text: str
            text to match company name on
        node: lxml.HtmlElement
            node to check for if it is not a title, to exclude <title>

        Returns
        -------
        str or None
            str of the name if found else None
        """
        if isinstance(text, str) and not node.tag == 'title':
            company_name_regex = self.parser.get('parameters', 'company_name_regex')
            nlp_res = self.nlp(text)

            # Try to use spacy to find company name
            for ent in nlp_res.ents:
                if ent.label == 'ORG':
                    logger.info(f"Company name is matched from spacy")
                    return ent.text
            
            # If not found, try to match the company name regex
            if re.findall(company_name_regex, string.capwords(text).replace("'", "")):
                logger.info(f"Company name is matched from regex")
                return re.findall(company_name_regex, string.capwords(text).replace("'", ""))[0]
            return None
        return None

    def search_word_in_tag(self, words):
        """
        Returns a list of words in tag and returns the word and last index value of the word list, if the word is present in the tag.

        Parameters
        ----------
        words: list
            list of words to search the parameters on

        Returns
        -------
        tuple
            word and it's value (last index of the words list) if word present else None, None
        """
        words_list = words.replace(':', '').split(' ')
        word = [word for word in words_list if word in self.interested_parameters][0]

        if word: return word, words_list[len(words_list) - 1]

        return None, None  

    def get_xpath(self, node, node_text, parameter):
        """
        Returns the xpath of node by checking the node_text if it is inside the alternative keywords.

        Parameters
        ----------
        node
            node to get xpath of
        node_text
            node text to get xpath of
        parameter
            parameter to get alternative text and consecutively get xpath of

        Returns
        -------
        str
            xpath of the node
        """
        if node_text == parameter or node_text in self.keywords[parameter]:
            return self.job_block_tree.getpath(node)

    # def find_company_info(self, company_name, company_name_xpath):
    #     tokenizer = RegexpTokenizer(r'\w+')
    #     tokenized = tokenizer.tokenize(company_name)

    #     tags_interested_in = ['a', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']
    #     all_nodes_with_token = set()
    #     for token in tokenized:
    #         nodes_matched = self.job_block_tree.xpath(f"//*[contains(text(),'{token}')]")
    #         for node in nodes_matched:
    #             if node.tag in tags_interested_in:
    #                 all_nodes_with_token.add(node)
    #     all_text_content = set()
    #     for node in all_nodes_with_token:
    #         all_text_content.add(node.text_content())
    #     all_text_content = list(sorted(all_text_content, key = len))
    #     try:
    #         print(self.job_block_tree.xpath(f"//*[contains(text(),'{all_text_content[0]}')]"))
    #         # self.parameters_xpath_dict['company_info_x']
    #         self.parameters_xpath_dict['company_info_xpath'] = self.job_block_tree.getpath(
    #             self.job_block_tree.xpath(f"//*[contains(text(),'{all_text_content[1]}')]")[0]
    #         )
    #         self.parameters_dict['company_info'] += clean_text(all_text_content[1])
    #     except: pass

    #     try:
    #         for node in self.job_block_tree.getpath(self.parameters_xpath_dict['company_info_xpath']).getparent()[0].iter(tag=etree.Element):
    #             self.parameters_dict['company_info'] += clean_text(node.text_content())
    #     except: pass

    def assign_misc_parameters_value(self, node, node_text):
        """
        Assigns the value of the misc parameters.

        Parameters
        ----------
        node: lxml.HtmlElement
            node to assign misc parameters values from
        node_text: str
            node text of the node to assign misc parameters values from
        """
        if node_text in self.keywords['misc']:
            # Append like something: value
            self.parameters_dict['misc'] += node_text + ': '
            # Append values
            try: 
                while node.getnext().text_content() in self.symbols_to_omit:
                    node = node.getnext()
                self.parameters_dict['misc'] += clean_text(node.getnext().text_content()) + '\n'
            except: pass

    def get_parent(self, node):
        """
        Returns parent of a node.

        Parameters
        ----------
        node: lxml.HtmlElement
            node to get parent of
        
        Returns
        -------
        lxml.HtmlElement
            parent of the node.
        """
        parent = node.getparent()
        # We are interested in <div> parent.
        while not parent.tag == 'div':
            parent = parent.getparent()
        return parent