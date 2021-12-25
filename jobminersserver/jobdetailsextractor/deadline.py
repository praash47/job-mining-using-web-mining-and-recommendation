"""
This module consists of class and it's methods in order to discover, handle and
process deadlines.

Classes
--------
Deadline():
    used for getting the deadline date in string format and it's xpath.
"""
from configparser import ConfigParser
from bs4 import BeautifulSoup
import bs4
# from jobminersserver.requestutils.request import Request
import requests

import datefinder
import datetime

import re
from lxml import html
from requests.api import request

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
    def __init__(self, xpath=None):
        """
        Parameters
        ----------
        None
        """
        self.soup = None

        self.probable_date_strings = None
        self.tags_with_date_string = []

        self.xpath = xpath

        # for deadline options
        CONFIG = 'C:\\Users\\Lenovo\\job-mining-using-web-mining-and-recommendation\\jobminersserver\\jobdetailsextractor\\extraction_options.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        # commonly used words in the deadline such as Apply before,
        # apply, deadline etc.
        self.common_deadline_words = \
            self.parser.get('deadline', 'common_deadline_words').split(',')
        self.common_deadline_words = \
            [word.strip() for word in self.common_deadline_words]
        
        self.deadline = None
    
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
            self.soup = BeautifulSoup(html, 'html.parser')
            self.get_probable_dates()  # this function summarizes date string as date.
            self.get_tags_with_date_string()
            self.check_deadline_words()
            self.assign_deadline_otherwise()
            self.get_xpath()

    def get_probable_dates(self):
        """
        Gets a list of probable date strings in the document using the datefinder
        module. datefinder is a module that can find strings with many date formats
        in the string. 
        """
        # print(self.soup.get_text())
        dates = list(
                    datefinder.find_dates(
                        self.soup.get_text()
                    )
                )
        future_dates = list(filter(Deadline.check_if_future_date, dates))
        # Intersted date refers to date within 90 days from today.
        interested_dates = list(filter(Deadline.is_interested_date, future_dates))
        # find probable date strings from the interested_dates datetime objects.
        self.probable_date_strings = [self.soup.findAll(text=re.compile(str(date.year))) for date in interested_dates][0]

    def get_tags_with_date_string(self):
        """
        Used to find tags with probable date strings in the html document. Stores
        it in the self.tags_with_date_string variable.
        """
        for tag in self.soup.findAll():
            if tag.string and not tag.name == 'script':  # ignore <script>:
                # match the date string and find the tags
                if str(tag.string) in self.probable_date_strings:
                    self.tags_with_date_string.append(tag.name)
            elif not tag.name == 'script':
                # If the deadline word is present inside a nested tag then,
                date_to_check = \
                    list(datefinder.find_dates(self.probable_date_strings[0]))[0]
                if self.check_for_nested_tag_label(tag, date_to_check):
                    self.tags_with_date_string.append(tag.name)

    def check_for_nested_tag_label(self, tag, date_to_check):
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
                    if list(datefinder.find_dates(tag.contents[index+1]))[0] == \
                        date_to_check:
                        return True
                except: pass
        return False

    def check_deadline_words(self):
        """
        Checks if the deadline word is present on the nodes that are on the
        left or right of where the probable date string was found.
        
        If it's found then, it's created as a list and first element of the
        list is assigned as a deadline.
        """
        for tag_name in self.tags_with_date_string:
            for tag in self.soup.findAll(tag_name):
                if str(tag.string) in self.probable_date_strings:
                    if self.check_deadline_word_present(list(tag.previous_siblings)) or \
                    self.check_deadline_word_present(list(tag.next_siblings)):
                        self.deadline = list(datefinder.find_dates(str(tag.string)))[0]

    
    def check_deadline_word_present(self, words_list):
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
                for deadline_word in self.common_deadline_words:
                    if deadline_word in str(words).lower():
                        return True

        return False

    def assign_deadline_otherwise(self):
        """
        Assigns deadline if the deadline word is not found in the left or right
        nodes of the probable date strings.
        """
        # if deadline is still not found, and if only option is available then
        # use that date string and parse out deadline from that.
        if not self.deadline and len(self.probable_date_strings) == 1:
            self.deadline = list(datefinder.find_dates(self.probable_date_strings[0]))[0]
        # if more than one probable date strings then, check to see if deadline
        # word is present in the probable date string itself.
        elif not self.deadline and len(self.probable_date_strings) > 1:
            for string in self.probable_date_strings:
                processed_words = string.lower().replace('\n', '').strip().split()
                if len(processed_words) > 1:
                    # if any words in the date string is in common deadline words,
                    # then assign that date string as the deadline.
                    for word in processed_words:
                        if word in self.common_deadline_words:
                            self.deadline = list(datefinder.find_dates(string))[0]
                else:
                    # this branch creates a contradicting opinion with the words
                    # collection presented in the check_deadline_words_documents.
                    # instead of some words collections, if only directly words
                    # are present.
                    if processed_words in self.common_deadline_words:
                        self.deadline = list(datefinder.find_dates(processed_words[0]))[0]

        if self.deadline and type(self.deadline) is not datetime.datetime:
            if len(self.deadline) == 2:
                # If 2 deadlines are present, take the later onhttps://jobaxle.com/jobs/quality-assurance-engineer/5821e.
                self.deadline = sorted(self.deadline)[1]
            
        if not self.deadline:
            # If deadline is still not there, just sort the dates, take the most later
            # one.
            dates = []
            for date in self.probable_date_strings:
                try:
                    dates.append(list(datefinder.find_dates(date))[0])
                except: pass
            self.deadline = sorted(dates)[len(dates)-1]

        print("Deadline", self.deadline)

    def get_xpath(self):
        """
        Extracts the deadline xpath from the deadline string.

        Uses a list because there may be more than one string that
        matches the deadline string.
        """
        deadline_xpaths = []
        for tag_name in self.tags_with_date_string:
            for tag in self.soup.findAll(tag_name):
                try:
                    if list(datefinder.find_dates(str(tag.string)))[0] == self.deadline:
                        element = self.tree.xpath(f"//{tag.name}[contains(text(), '{str(tag.string)}')]")[0]
                        deadline_xpaths.append(self.tree.getpath(element))
                except:
                    try:
                        # if common deadline word is in the nested tag. 
                        if self.check_for_nested_tag_label(tag, \
                            self.deadline):
                            element = None
                            for node in self.tree.xpath(f"//{ tag.name }"):
                                # find the node with date as text content and assign it
                                # as the element and compute it's xpath.
                                try:
                                    if list(datefinder.find_dates(str(node.text_content())))[0] == \
                                        self.deadline:
                                        element = node
                                except: pass
                            deadline_xpaths.append(self.tree.getpath(element))
                    except Exception as e: print(e)
        self.xpath = deadline_xpaths[0]
        # self.deadline = list(datefinder.find_dates(self.deadline))[0]

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
    url = "https://merojob.com/vp-engineer/"
    deadline_obj = Deadline()
    # request = Request(url)
    request_html = requests.get(url).content
    # strip off <script tag>
    request_html = re.subn(r'<(script).*?</\1>(?s)', '', str(request_html))[0]
    tree = html.fromstring(request_html).getroottree()
    deadline_obj.tree = tree
    deadline_obj.get_deadline_date(request_html) #request.request_html())
    print(deadline_obj.xpath)