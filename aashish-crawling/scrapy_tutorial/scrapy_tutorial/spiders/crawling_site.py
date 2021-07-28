from lxml import html
class Site:
    def __init__(self, search_page_url):
        # Search Page Initializations
        self.search_page_url = search_page_url
        self.search_step = None
        
        # Paginator Initialization
        self.pages = Paginator()

        # Xpather Initialization
        self.xpaths = Xpather()
        self.temp_xpath = None
        pass

    def get_xpaths(self, response, links):
        xpaths_got, temp_xpath = self.xpaths.get_xpaths(response, links, self.temp_xpath)
        # If normally got, just return it.
        if xpaths_got: return xpaths_got, temp_xpath
        # If not got, throw a pagination request.
        elif temp_xpath == "NO_XPATH": pass
        elif temp_xpath: self.temp_xpath = temp_xpath
        
        if self.pages.has_pages: return xpaths_got, 'PAGE_TRAVERSAL_REQUEST'
        elif not self.pages.next_page: return xpaths_got, 'NOT_POSSIBLE'
        else: return xpaths_got, 'NOT_POSSIBLE'

    def get_page_no(self, response):
        self.pages.get_page_no(response)

class Paginator:
    def __init__(self):
        self.curr_page = 1
        self.max_page = None
    #     self.has_pages = self.check_pages()

    # def check_pages(self):
    #     self   

    def get_page_no(self, response):
        if not self.max_page:
            for link in self.link_extractor.extract_links(response):
                try:
                    if int(link.text) in range(100):
                        if not self.search_page_url:
                            num = link.url[-2:-1] + link.url[-1]
                            if link.url[-1] == '/': self.search_page_url = link.url[:-2]
                            elif link.url[-1] == link.text: self.search_page_url = link.url[:-1]
                            elif num.isnumeric():
                                self.search_step = int(num)
                                self.curr_page = int(num)
                                self.search_page_url = link.url[:-2]
                            # else:
                                # reversed_url = link.url[::-1]
                                # found_index = reversed_url.find(link.text)
                                # split_url = [char for char in reversed_url]
                                # self.search_page_url = link.url[0:len(reversed_url)-1-found_index]
                                # print(self.search_page_url)

                        if not self.max_page: self.max_page = int(link.text)
                        elif self.max_page < int(link.text): self.max_page = int(link.text)
                except:
                    if self.search_step:
                        if link.url[-1].isnumeric():
                            step = -1
                            while (link.url[step-1:-1] + link.url[-1]).isnumeric():
                                step -= 1
                            self.max_page = int(link.url[step:-1] + link.url[-1])

class Xpather:
    def __init__(self):
        # Main Variables
        self.xpath = None
        self.var_index = None
        
        # Matching texts and urls of job titles
        self.job_titles = []
        with open('scrapy_tutorial/spiders/titles_combined.txt') as titles:
            self.job_titles = [title.strip('\n') for title in titles.readlines()]
        self.link_texts = []
        self.link_urls = []

        # HTML tree parsing stuff
        self.response_html = None
        self.tree = None

    def get_xpaths(self, response, links, one_xpath):
        if not self.xpath:
            # Extract out link texts of job titles present in site and the job titles file.
            self.link_texts = [link.text.strip('\n') for link in links if link.text.strip('\n') in self.job_titles]

            # Extract HTML tree for getting xpaths of the links        
            self.response_html = html.fromstring(response.text)
            self.tree = self.response_html.getroottree()

            try:
                # Get two matching xpaths to compute out the difference
                xpath_one = self.response_html.xpath(f"//a[contains(text(), '{self.link_texts[0]}')]")
                xpath_two = self.response_html.xpath(f"//a[contains(text(), '{self.link_texts[1]}')]")
            except:
                print("cannot ")
            xpaths = []
            for xpath in xpath_one: xpaths.append(self.tree.getpath(xpath))
            for xpath in xpath_two: xpaths.append(self.tree.getpath(xpath))
            
            if not xpath_one and not xpath_two:
                # Both xpaths are not present, then it must be nested.
                xpaths = self.get_xpath_from_nested()

                # Means website doesn't contain any matching job titles.
                if not xpaths: return False, 'NO_XPATH'
            
            try:
                # Compute the difference between two xpaths by individually calculating out the differences
                # in xpaths.
                xpaths[0] = xpaths[0].split('/')

                # THIS IS FOR ITERATION IN NEXT PAGES IN PAGES TRAVERSAL:
                # If in another page, still one more page couldn't be found and there is 
                # another one xpath already present from before, then use it as the second
                # xpath for comparison.
                if not xpaths[1] and one_xpath: xpaths[1] = one_xpath
                else: xpaths[1] = xpaths[1].split('/')
            except:
                # One of the xpath is found, another not found.
                return False, xpaths[0]
            
            # Get the varying index
            for index, path in enumerate(xpaths[0]):
                if path != xpaths[1][index]:
                    self.var_index = index

            self.xpath = xpaths[0]
        return True, None

    def get_xpath_from_nested(self):
        # Extract out link urls of job titles present in site and the job titles file.
        link_urls = [link.url for link in links if link.text.strip('\n') in self.job_titles]

        # Find a with urls of link urls.
        nested_elements1 = root.xpath(f"//a[contains(@href,'{link_urls[0]}')]/node()")
        nested_elements2 = root.xpath(f"//a[contains(@href,'{link_urls[1]}')]/node()")

        # If an element object is found inside those a tags and inside of it a tag
        # is present and contains the link_text, then place that intermediate tag in
        # the path list.
        for element in nested_elements1:
            if not isinstance(element, str):  # Normally, it is of str type.
                xpath_one = root.xpath(f"//a//{element.tag}[contains(text(), '{link_texts[0]}')]")
        for element in nested_elements2:
            if not isinstance(element, str):
                xpath_two = root.xpath(f"//a//{element.tag}[contains(text(), '{link_texts[1]}')]")
        
        # Issue is not having nested elements
        if not xpath_one and not xpath_two: return None
        
        # Extraction of xpaths from tree
        xpaths = []
        for xpath in xpath_one: xpaths.append(tree.getpath(xpath))
        for xpath in xpath_two: xpaths.append(tree.getpath(xpath))
        
        return xpaths