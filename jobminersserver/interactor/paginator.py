"""
This submodule handles all the pagination complexities of the website. It's functions includes calculating the next page URL, the next page value and work with other modules to extract jobs in multiple paginated non AJAX websites.

Classes
-------
Paginator()
Used to handle pages inside a website.
"""
from backend.misc import log, try_and_pass


class Paginator:
    """
    This object is responsible for handling the pages in the non ajax based websites

    Methods
    -------
    has_pages(links)
        Returns true if page number is present in the page.
    check_search_step(site, links)
        Checks and assigns the search step if the search step is present. Call it before getting last page.
    get_last_page(links)
        Gets the last page of the non search step paginated non ajax website.
    move_to_next_page()
        Serially moves the current page of the paginator object up by one step or by search step.
    reset_paginator()
        Resets the paginator to 1 after use.
    """

    def __init__(self):
        # Current and Last pages
        self.curr_page = 1
        self.last_page = None

        # Page URL structure of a site
        self.page_url = None
        self.first_page_url = self.page_url

        # For search step, that is the step with which the page number is incremented, required
        # because some websites perform pagination on the basis of number of records of the job.
        self._search_step = 1

        # Page traversal utilities
        self._traversing_page = 1

    def has_pages(self, links):
        """
        Returns true if the site has Non AJAX based paginations.

        Parameters
        ----------
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.

        Returns
        -------
        boolean
            True if there is a number link present in the site's links.
        """
        log("interactor", "info", f"Checking pages")

        @try_and_pass
        def check_page_number_found(link):
            if int(link.text) in range(100):
                log(
                    "interactor",
                    "info",
                    "Paginator found the site has pages, there is integer in range 1-100 in page.",
                )
                return True

        for link in links:
            # try and catch, because everything is not a number, int throws
            # an exception in this case.
            found = check_page_number_found(link)
            if found:
                return found

        log(
            "interactor",
            "info",
            "No integer value in range 1-100 found in page. So, Non paginated",
        )
        return False

    def get_last_page(self, links):
        """
        Gets last page of the site using links. This is a kind of condition type of
        last page extracting function that only works when there is no any search step
        present in the page.

        This function applies the concept of getting out the maximum number.

        Parameters
        ----------
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.
        """
        log("interactor", "info", "Getting last page")

        @try_and_pass
        def check_last_page_in_numbers(link):  # see only numbers
            if int(link.text) in range(100):
                # Calculate the greatest number and assign it as last.
                if not self.last_page:
                    self.last_page = int(link.text)
                elif self.last_page < int(link.text):
                    self.last_page = int(link.text)

        if not self.last_page:
            for link in links:
                check_last_page_in_numbers(link)

        log("interactor", "info", f"Got the last page as {self.last_page}")

    def check_search_step(self, site, links):
        """
        Used to compute search step of a page. A search step is defined as the
        number that is used for representing the pagination structure. It is
        usually greater than 1.

        It exists due to the fact that some websites paginated not on the basis
        of serial page numbers but with the total number of job adverts present
        in a page.

        Parameters
        ----------
        site: Site object
            site object of the website whose search step is being checked
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.
        """
        log("interactor", "info", "Checking the search step for the paginated website.")
        # Seperate a search page url
        @try_and_pass
        def is_int(char):
            if type(int(char)) is int:
                return True

        @try_and_pass
        def if_number_check_search_step(link):
            if (int(link.text)) in range(100):
                # Check if integer is in that url in order to verify
                # Garbage url is often present in page 1 in some cases.
                # Removal of that garbage url
                int_in_url = False
                for char in link.url:
                    int_in_url = is_int(char)
                    if int_in_url:
                        continue

                # only accept the urls with int in them
                if int_in_url:
                    self.page_url = link.url
                    return True
                return False
            return False

        for link in links:
            search_step_found = if_number_check_search_step(link)
            if search_step_found:
                break
        self.first_page_url = self.page_url

        # Extract page value in the page url
        page = ""
        for char in self.page_url:
            if is_int(char):
                page = page.join(str(char))  # Append integer values

        self._search_step = int(page)
        # Normal also set 2, because of page 2, so reset.
        # The search step 2 also can be regarded as one because the above function may
        # also recognize pages with search step 2 as 1.
        if self._search_step == 2:
            self._search_step = 1

        log("interactor", "info", f"Got the search step as {self._search_step}")
        # Call the specific function for getting last page while the search step is
        # present.
        self._get_last_page_step(site, links)

    def _get_last_page_step(self, site, links):
        """
        Sets the value of last page if a search step is present in the link. This only
        works for the websites with search step in it.

        Parameters
        ----------
        site: Site object
            site object of the website whose search step is being checked
        links: list of scrapy.Link
            scrapy's link object that stores information abou the link.
        """
        if self._search_step > 1:
            log(
                "interactor",
                "info",
                f"As search step > 1, so reassigning the last page.",
            )
            max_page = 0
            last_page = ""
            for link in links:
                # Find if it's a search page URL.
                if set(site.search_page_url.split("/")).issubset(
                    set(link.url.split("/"))
                ):
                    for char in link.url:
                        if char.isnumeric():
                            # extract numbers and append it as last page
                            last_page += char
                    # Compute the largest page number.
                    if last_page:
                        if int(last_page) > max_page:
                            max_page = int(last_page)
                    last_page = ""
            # Assign the largest number that is the last page.
            self.last_page = max_page
            log("interactor", "info", f"Updated last page: {self.last_page}")

    def _get_search_page_url(self, page):
        """
        Gets search page url for the current website from the page number that is given to it.

        Parameters
        ----------
        page: int
            page number to generate search page url for.

        Returns
        -------
        str
            page url with the page number sent from the parameter.
        """
        # pre_string holds the preceding substring for the url.
        pre_string = [char for char in self.page_url if not char.isnumeric()]
        page_num_str_index = 0

        # here self.page_url holds the sample of the current website's page url.
        for index, char in enumerate(self.page_url):
            if char.isnumeric():
                page_num_str_index = index  # get the page number string index
                break

        pre_string = "".join(pre_string)
        # get whatever there is after page number and place it into post_string
        post_string = pre_string[page_num_str_index:]
        pre_string = pre_string[0:page_num_str_index]

        log(
            "interactor",
            "info",
            f"Got url {pre_string + str(page * self._search_step) + post_string} for page {page}.",
        )
        return pre_string + str(page * self._search_step) + post_string

    def move_to_next_page(self):
        """
        Use to move to the next page in a serial order. Moving to the next page
        implies increasing the current page by one or by the search page.

        Returns
        -------
        self.curr_page if the next page exists, otherwise False
        """
        if self.curr_page <= self.last_page:
            if self._search_step == 1:
                self.curr_page += 1
            elif self._search_step > 1:
                self.curr_page += 1

            self.page_url = self._get_search_page_url(self.curr_page)
            log("interactor", "info", f"Moved to page {self.curr_page}")
            return self.curr_page
        else:
            log("interactor", "info", "No any next page.")
            return False

    def reset_paginator(self):
        """
        Used to reset paginator back to it's original values after use.
        """
        self.page_url = self.first_page_url
        self.curr_page = 1
