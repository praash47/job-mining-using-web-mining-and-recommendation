from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class Search:

    '''
      A class to find the search box in the webpage and
      perform search with no character or single space.

      Methods
      -------
      search_term(search, self.url)
          send single space key or no key to the search box and Enter the search box to perform search

      xpath_of_textbox(self.url)
          checks the xpath of input @type = "text"[1][2][3] and "search"[1][2] and
      '''
    def __init__(self, url):
        """
                Parameters
                ---------
                url : str
                    url of the webpages
                """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)
        self.url = url

    def search_term(self, search):
        """
                performs search on textbox sending no key or space key
                Parameters
                ----------
                search : str
                xpath of the text box from xpath_of_textbox below

                check_url : ste

                """
        check_url = self.driver.current_url
        search_url = ''
        try:
            search.send_keys('')               #send no keys to search box
            search.send_keys(Keys.ENTER)  #Enter the search box
            search_url = self.driver.current_url
        except:
            pass

        if self.url == check_url:
            try:
                search.send_keys(' ')           # send ' ' key to search box
                search.send_keys(Keys.ENTER) # Enter the search box
                search_url = self.driver.current_url
            except:
                pass
        return search_url



    def get_search_url(self):
        '''xpath_of_textbox(self.url) checks the xpath of
            input @ type = "text"[1][2][3] and "search"[1][2]

        returns the search url
        '''
        try:
            self.driver.get(self.url)
        except Exception as e:
            print(e)

        check_url = self.driver.current_url
        search_url = self.find_element_by_type('text', 3, check_url)

        if not search_url: search_url = self.find_element_by_type('search', 2, check_url)

        return search_url

    def find_element_by_type(self, element_type, finish_index, check_url):
        self.search = ''
        self.search_url = ''
        
        if check_url == self.url:
            try:
                self.search = self.driver.find_element_by_xpath(
                    f"//input[@type='{element_type}']")
                self.search_url = self.search_term(self.search)
            except: pass
        for i in range(2, finish_index):
            if check_url == self.url:
                try:
                    self.search = self.driver.find_element_by_xpath(
                        f"//input[@type='{element_type}'][{i}]")
                    self.search_url = self.search_term(self.search)
                except: pass
        if self.search_url == self.url: return None

        return self.search_url
    # xpath of first textbox with input type text


if __name__ == "__main__":
    url = 'https://www.kumarijob.com/'
    s1 = Search(url)
    print(s1.get_search_url())
