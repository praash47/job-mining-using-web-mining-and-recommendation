"""
This module consists of class and it's methods in order to discover, handle and
process deadlines.

Classes
--------
Deadline():
used for getting the deadline date in string format and it's xpath.
"""
import bs4
import datefinder
import datetime
import re
import requests

from bs4 import BeautifulSoup
from lxml import html

from backend.misc import read_config, log
from tagprocessor.decorators import for_all_tags, for_existing_leaf_nodes
from tagprocessor.misc import clean_text

from .exceptions import DeadlineNotFound, DeadlineXpathNotFound


class Deadline:
    """
    Extracts deadline from a html document. You create a deadline object and
    pass in a html document while calling get_deadline_date() function to get
    the deadline inside self.deadline and it's respective xpath inside the self.
    xpath variable.

    Methods
    -------
    get_deadline_date(html):
        finds the deadline date in an html document and stores into deadline
        variable as a date string which can be parsed to obtain a python datetime
        object.

    Static Methods
    --------------
    check_if_future_date(date):
        checks if a date if a future date or a past date.
    is_interested_date(date):
        interested date refers to the date from which 90 days
        haven't been passed. checks if a date passed is within
        90 days.
    """

    def __init__(self, tree, xpath=None):
        """
        Parameters
        ----------
        tree: lxml.etree
            lxml.etree to find the deadline on.
        """
        self._soup = None

        self._probable_date_strings = None
        self._tags_with_date_string = []

        self._tree = tree
        self.xpath = xpath

        # for deadline options
        self._parser = read_config("jobdetailsextractor/reqs/extraction_options.ini")
        # commonly used words in the deadline such as Apply before,
        # apply, deadline etc.
        self._common_deadline_words = self._parser.get(
            "deadline", "common_deadline_words"
        ).split(",")
        self._common_deadline_words = [
            word.strip() for word in self._common_deadline_words
        ]

        self.deadline = None
        log("jobdetailsextractor", "info", "Deadline Object Created")

    def get_deadline_date(self, html):
        """
        Stores deadline date and xpath in the object variables after it's
        extraction from the document.

        Parameters
        ----------
        html: string
            String in which an HTML document is present.
        """
        if not self.xpath:
            self._soup = BeautifulSoup(html, "html.parser")
            try:
                self._get_probable_dates()  # this function summarizes date string as date.
                self._get_tags_with_date_string()
                self._check_deadline_words(
                    tags=self._tags_with_date_string, soup=self._soup
                )
                self._assign_deadline_otherwise()
                self._get_xpath()
                if not self.deadline:
                    raise DeadlineNotFound
                else:
                    log("jobdetailsextractor", "info", f"Deadline: {self.deadline}")
                    log("main", "info", f"Deadline: {self.deadline}")
            except DeadlineNotFound:
                raise DeadlineNotFound
            except DeadlineXpathNotFound:
                raise DeadlineXpathNotFound
            except Exception as e:
                log("jobdetailsextractor", "error", f"{e}")
                log("main", "error", f"{e}")
        else:
            self.deadline = self._tree.xpath(self.deadline.xpath)[0].text_content()

    def _get_probable_dates(self):
        """
        Gets a list of probable date strings in the document using the datefinder
        module. datefinder is a module that can find strings with many date formats
        in the string.
        """
        log("jobdetailsextractor", "info", "Getting probable dates")
        dates = list(datefinder.find_dates(self._soup.get_text()))
        future_dates = list(filter(Deadline.check_if_future_date, dates))
        # Intersted date refers to date within 90 days from today.
        interested_dates = list(filter(Deadline.is_interested_date, future_dates))
        if not interested_dates:
            raise DeadlineNotFound
        # find probable date strings from the interested_dates datetime objects.
        self._probable_date_strings = [
            self._soup.findAll(text=re.compile(str(date.year)))
            for date in interested_dates
        ][0]
        log(
            "jobdetailsextractor",
            "info",
            f"Probable date strings: {self._probable_date_strings}",
        )

    def _get_tags_with_date_string(self):
        """
        Used to find tags with probable date strings in the html document. Stores
        it in the self._tags_with_date_string variable.
        """
        log("jobdetailsextractor", "info", "Getting tags with date string")
        for tag in self._soup.findAll():
            if tag.string and not tag.name == "script" and not tag.name == "title":
                # ignore <script> & title:
                # match the date string and find the tags
                if str(tag.string) in self._probable_date_strings:
                    self._tags_with_date_string.append(tag.name)
            elif not tag.name == "script":
                # If the deadline word is present inside a nested tag then,
                date_to_check = list(
                    datefinder.find_dates(self._probable_date_strings[0])
                )[0]
                if self._check_for_nested_tag_label(tag, date_to_check):
                    self._tags_with_date_string.append(tag.name)
        log(
            "jobdetailsextractor",
            "info",
            f"Tags with date string: {self._tags_with_date_string}",
        )

    def _check_for_nested_tag_label(self, tag, date_to_check):
        """
        Checks for a date in a nested tag label.

        Eg.: <p><strong>Apply Before: </strong> 2021-12-23</p>

        Parameters
        ----------
        tag: bs4.element.Tag
            tag to check sub contents of, in example <p>
        date_to_check: datetime object
            convert your string into python datetime object and put
            here.

        Returns
        -------
        boolean:
            True if a deadline word is present in the nested tag label and
            there is date_to_check besides that label otherwise False.
        """
        # If the deadline word is present inside a nested tag then,
        # loop through that parent tag's sub contents
        for index, content in enumerate(tag.contents):
            # if a nested tag is found
            if type(content) is bs4.element.Tag:
                try:
                    # find the sub contents just beside that tag, the tag
                    # has a label for that sub content, thus, check to see
                    # if the probable date strings matches with the date, if
                    # matched, parent tag is sent for the xpath.
                    if (
                        list(datefinder.find_dates(tag.contents[index + 1]))[0]
                        == date_to_check
                    ):
                        return True
                except:
                    pass
        return False

    @for_all_tags
    def _check_deadline_words(self, tag):
        """
        [wrapped with @loop_in_all_tags decorator]
        Checks if the deadline word is present on the nodes that are on the
        left or right of where the probable date string was found.

        If it's found then, it's created as a list and first element of the
        list is assigned as a deadline.
        """
        if str(tag.string) in self._probable_date_strings:
            if self._check_deadline_word_present(
                list(tag.previous_siblings)
            ) or self._check_deadline_word_present(list(tag.next_siblings)):
                self.deadline = list(datefinder.find_dates(str(tag.string)))[0]

    def _check_deadline_word_present(self, words_list):
        """
        Takes in a words_list and checks if any of the common deadline words
        are present in the words_list.

        Parameters
        ----------
        words_list: list of strings
            words_list is a collection of sentences like collection of group
            of words termed as words_collections here.

        Returns
        -------
        boolean
            True if the deadline word is present in common_deadline_words else
            False.
        """
        for words_collections in words_list:
            for words in words_collections:
                for deadline_word in self._common_deadline_words:
                    if deadline_word in str(words).lower():
                        return True

        return False

    def _assign_deadline_otherwise(self):
        """
        Assigns deadline if the deadline word is not found in the left or right
        nodes of the probable date strings.
        """
        # if deadline is still not found, and if only option is available then
        # use that date string and parse out deadline from that.
        if not self.deadline and len(self._probable_date_strings) == 1:
            self.deadline = list(datefinder.find_dates(self._probable_date_strings[0]))[
                0
            ]
        # if more than one probable date strings then, check to see if deadline
        # word is present in the probable date string itself.
        elif not self.deadline and len(self._probable_date_strings) > 1:
            for string in self._probable_date_strings:
                # If time component present then assign date.
                self._check_deadline_in_nested_string(string)

        if self.deadline and type(self.deadline) is not datetime.datetime:
            if len(self.deadline) == 2:
                # If 2 deadlines are present, take the later onhttps://jobaxle.com/jobs/quality-assurance-engineer/5821e.
                self.deadline = sorted(self.deadline)[1]

        if not self.deadline:
            # If deadline is still not there, just sort the dates, take the most later
            # one.
            dates = []
            for date in self._probable_date_strings:
                try:
                    dates.append(list(datefinder.find_dates(date))[0])
                except:
                    pass
            self.deadline = sorted(dates)[len(dates) - 1]

    def _check_deadline_in_nested_string(self, string):
        """
        Checks for deadline word in the nested string and assigns the string if a common deadline word is found in that string.
        """
        if not self.deadline:
            processed_words = string.lower().replace("\n", "").strip().split()
            if len(processed_words) > 1:
                # if any words in the date string is in common deadline words,
                # then assign that date string as the deadline.
                for word in processed_words:
                    if word in self._common_deadline_words:
                        self.deadline = list(datefinder.find_dates(string))[0]
            else:
                # this branch creates a contradicting opinion with the words
                # collection presented in the _check_deadline_words_documents.
                # instead of some words collections, if only directly words
                # are present.
                if processed_words in self._common_deadline_words:
                    self.deadline = list(datefinder.find_dates(processed_words[0]))[0]

    def _get_xpath(self):
        """
        [wrapped with @loop_in_all_tags decorator]
        Extracts the deadline xpath from the deadline string.

        Uses a list because there may be more than one string that
        matches the deadline string.
        """
        if not self.deadline:
            raise DeadlineNotFound

        @for_all_tags
        def try_get_path(tag):
            deadline_xpaths = []
            try:
                if list(datefinder.find_dates(str(tag.string)))[0] == self.deadline:
                    try:
                        root = self._tree.getroot().getchildren()
                    except Exception as e:
                        log("jobdetailsextractor", "error", f"{e}")

                    @for_existing_leaf_nodes
                    def assign_el_if_matches(node, tag, **kwargs):
                        node_text = kwargs.get("node_text")
                        if node_text == clean_text(tag.string):
                            return node

                        return ""

                    element = assign_el_if_matches(tag, root=root)

                    if type(element) is html.HtmlElement:
                        deadline_xpaths.append(self._tree.getpath(element))
            except Exception:
                try:
                    # if common deadline word is in the nested tag.
                    if self._check_for_nested_tag_label(tag, self.deadline):
                        element = None
                        for node in self._tree.xpath(f"//{ tag.name }"):
                            # find the node with date as text content and assign it
                            # as the element and compute it's xpath.
                            try:
                                if (
                                    list(
                                        datefinder.find_dates(str(node.text_content()))
                                    )[0]
                                    == self.deadline
                                ):
                                    element = node
                            except:
                                pass
                        deadline_xpaths.append(self._tree.getpath(element))
                except Exception as e:
                    print(e)
            return deadline_xpaths

        deadline_xpaths = try_get_path(
            tags=self._tags_with_date_string, soup=self._soup
        )

        if not deadline_xpaths:
            raise DeadlineXpathNotFound

        self.xpath = deadline_xpaths[0]
        log("jobdetailsextractor", "info", f"Deadline Xpath: {self.xpath}")

    @staticmethod
    def check_if_future_date(date):
        """
        Takes in a datetime object date and checks whether the date is a future
        date or not.

        Parameters
        ----------
        date: datetime
            python datetime object to check

        Returns
        -------
        boolean
            True if future date, False otherwise.
        """
        try:
            return datetime.datetime.now() < date
        except:
            return False

    @staticmethod
    def is_interested_date(date):
        """
        Checks whether the date or the datetime object passed is interested date
        or not. Interested date refers to the date within 90 days from today's
        date.

        Parameters
        ----------
        date: datetime
            python datetime object to check

        Returns
        -------
        boolean
            True if within 90 days (interested date), False otherwise.
        """
        now = datetime.datetime.now()
        if (date - now) <= datetime.timedelta(days=90):
            return True
        return False


if __name__ == "__main__":
    url = "https://merojob.com/intern-social-media-coordinator/"
    # request = Request(url)
    request_html = requests.get(url).content
    # strip off <script tag>
    request_html = re.subn(r"<(script).*?</\1>(?s)", "", str(request_html))[0]
    tree = html.fromstring(request_html).getroottree()
    deadline_obj = Deadline(tree)
    deadline_obj.get_deadline_date(request_html)  # request.request_html())
    print(deadline_obj.deadline)
    print(deadline_obj.xpath)
