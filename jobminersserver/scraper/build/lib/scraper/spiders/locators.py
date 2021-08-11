from lxml import html


class Paginator():
    def __init__(self):
        # Current and Last pages
        self.curr_page = 1
        self.last_page = None

        # Page URL structure of a site
        self.page_url = None

        self.curr_search_page_url = None

        # For search step
        self.search_step = 1

        # Page traversal utilities
        self.traversing_page = 1

    def has_pages(self, links):
        """
        Returns true if the site has Non AJAX based paginations.
        """
        for link in links:
            try:
                if int(link.text) in range(100):
                    return True
            except: pass
        return False

    def get_last_page(self, links):
        """
        Gets last page of the site using links.
        """
        if not self.last_page:
            for link in links:
                try: # see only numbers
                    if int(link.text) in range(100):
                        # Calculate the greatest number and assign it as last.
                        if not self.last_page: self.last_page = int(link.text)
                        elif self.last_page < int(link.text): self.last_page = int(link.text)
                except: pass

    def check_search_step(self, site, links):
        """
        Used to compute search step of a page. A search step is defined as the
        number that is used for representing the pagination structure. It is
        usually greater than 1.

        It exists due to the fact that some websites paginated not on the basis
        of serial page numbers but with the total number of job adverts present
        in a page.
        """
        # Seperate a search page url
        for link in links:
            try:
                if(int(link.text)) in range(100):
                    # Check if integer is in that url in order to verify
                    # Garbage url is often present in page 1 in some cases.
                    # Removal of that garbage url
                    int_in_url = False
                    for char in link.url: 
                        try:
                            if type(int(char)) is int: int_in_url = True
                        except: pass

                    if int_in_url:
                        self.page_url = link.url
                        break
            except: pass
        
        # Extract page value in the page url
        page = ''
        for char in self.page_url:
            try: 
                if type(int(char)) is int: page += str(char)
            except: 
                if page: break
                else: pass
        self.search_step = int(page)
        # Normal also set 2, because of page 2, so reset.
        if self.search_step == 2: self.search_step = 1
        self.get_last_page_step(site, links)

    def get_last_page_step(self, site, links):
        """
        Sets the value of last page if a search step is present in the link.
        """
        if self.search_step > 1:
            max_page = 0
            last_page = ''
            for link in links:
                # Find if it's a search page URL.
                if set(site.search_page_url.split('/')).issubset(set(link.url.split('/'))):
                    for char in link.url:
                        if char.isnumeric():
                            last_page += char
                    # Compute the largest page number.
                    if last_page:    
                        if int(last_page) > max_page: 
                            max_page = int(last_page)
                    last_page = ''
            self.last_page = max_page

    def get_search_page_url(self, page):
        pre_string = [char for char in self.page_url if not char.isnumeric()]
        page_num_str_index = 0
        for index, char in enumerate(self.page_url): 
            if char.isnumeric(): 
                page_num_str_index = index
                break
            
        pre_string = ''.join(pre_string)
        post_string = pre_string[page_num_str_index:]
        pre_string = pre_string[0:page_num_str_index]

        return pre_string + str(page * self.search_step) + post_string

    # TODO: Fix the traverse pages for searching xpaths in other pages as
    # well.
    # def traverse_pages(self, response):
    #     print(response)
    #     if self.traversing_page <= self.last_page:
    #         if self.search_step == 1: self.traversing_page += 1
    #         traversing_url = self.get_search_page_url(self.traversing_page)
    #         if self.search_step > 1: self.traversing_page += 1
    #         print(f"page {self.traversing_page}")
    #         yield Request(traversing_url, callback=self.place_response)
    #     else:
    #         return False

    # def place_response(self, response):
    #     print(response)

    def move_to_next_page(self):
        """
        Use to move to the next page in a serial order.
        """
        if self.curr_page <= self.last_page:
            if self.search_step == 1: self.curr_page += 1
            self.page_url = self.get_search_page_url(self.curr_page)
            if self.search_step > 1: self.curr_page += 1
            return self.curr_page
        else:
            return False

class Xpather():
    def __init__(self, response, site, paginated):
        """
        This class is responsible for handling and computing the xpaths.
        """
        # Xpath #1 and #2
        self.first = None
        self.second = None

        # Xpath variable element index
        self.var_index = None
        
        # Matching texts and urls of job titles
        self.job_titles = []
        with open('scraper/spiders/titles_combined.txt') as titles:
            self.job_titles = [title.strip('\n') for title in titles.readlines()]
        
        # Link Text and URLs 
        self.link_texts = []
        self.link_urls = []

        # Extract HTML tree for getting xpaths of the links
        self.response = response        
        self.response_html = html.fromstring(response.text)
        self.tree = self.response_html.getroottree()

        # Site object
        self.site = site
        self.paginated = paginated

    def get_xpaths(self, links):
        # Extract out link texts of job titles present in site and the job titles file.
        self.link_texts = [link.text.strip('\n') for link in links if link.text.strip('\n') in self.job_titles]
        
        if self.paginated:
            self.site.pages.get_last_page(links)
            self.site.pages.check_search_step(self.site, links)

            xpaths = self.find_xpaths(links)
            
            return xpaths
        else:
            xpaths = self.find_xpaths(links)

            if xpaths: return xpaths

            return False    


    def find_xpaths(self, links):   
        self.first = self.find_xpath(self.first, self.link_texts, link_texts_index=0)
        self.second = self.find_xpath(self.second, self.link_texts, link_texts_index=1)

        if not self.first or not self.second:
            # Both xpaths are not present, then it must be nested.
            xpaths = self.get_xpath_from_nested(links)
            if not xpaths: return False

        xpaths = []
        for xpath in self.first: xpaths.append(self.tree.getpath(xpath))
        for xpath in self.second: xpaths.append(self.tree.getpath(xpath))

        return xpaths

    def get_xpath_from_nested(self, links):
        # Extract out link urls of job titles present in site and the job titles file.
        self.link_urls = [link.url for link in links if link.text.strip('\n') in self.job_titles]

        # Find a with urls of link urls.
        try:
            nested_elements1 = self.tree.xpath(f"//a[contains(@href,'{self.link_urls[0]}')]/node()")
            nested_elements2 = self.tree.xpath(f"//a[contains(@href,'{self.link_urls[1]}')]/node()")
        except:
            return False

        # If an element object is found inside those a tags and inside of it a tag
        # is present and contains the link_text, then place that intermediate tag in
        # the path list.
        xpath_one, xpath_two = '', ''
        for element in nested_elements1:
            if not isinstance(element, str):  # Normally, it is of str type.
                xpath_one = self.tree.xpath(f"//a//{element.tag}[contains(text(), '{self.link_texts[0]}')]")
        for element in nested_elements2:
            if not isinstance(element, str):
                xpath_two = self.tree.xpath(f"//a//{element.tag}[contains(text(), '{self.link_texts[1]}')]")
        
        # Issue is not having nested elements
        if not xpath_one and not xpath_two: return None
        
        # Extraction of xpaths from tree
        xpaths = []
        for xpath in xpath_one: xpaths.append(self.tree.getpath(xpath))
        for xpath in xpath_two: xpaths.append(self.tree.getpath(xpath))
        
        return xpaths

    def find_xpath(self, xpath, link_texts, link_texts_index=0):
        try:
            # Get two matching xpaths to compute out the difference
            xpath = self.response_html.xpath(f"//a[contains(text(), '{link_texts[link_texts_index]}')]")
            return xpath
        except: pass