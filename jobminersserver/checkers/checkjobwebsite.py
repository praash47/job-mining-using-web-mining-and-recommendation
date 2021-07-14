"""
This file consists of class that is required to check whether a
website is a job website or not.

Classes
-------
CheckJobWebsite(urls=None)
    checks if a website is job website or not.
"""
from configparser import ConfigParser
from urllib import parse
import requests
import json

# Need while using main for debugging.
import sys
sys.path.insert(1, 'D:/job-mining-using-web-mining-and-recommendation/jobminersserver/')
from requestutils.request import Request
from checkers.misccheckers import is_interested_website

sys.path.insert(
    1, 
    'D:/job-mining-using-web-mining-and-recommendation/jobminersserver/tagprocessor/'
)
from tagprocessor import TagProcessor
from metatagprocessor import MetaTagProcessor

class CheckJobWebsite:
    """
    Utilities required to check whether a website is job website or not.
    
    Methods
    -------
    check_urls()
        Returns dictionary of checked urls.
    check_single_url(url)
        Checks single url is job website url or not.    
    """
    def __init__(self, urls=None):
        """
        Parameters
        ----------
        urls: list of strings, optional
            Strings here are individual urls.
        """
        print("Getting job websites...")
        self.urls_to_check = []
        print(urls)
        for url in urls:
            req = Request(url)
            if req.check_homepage(): self.urls_to_check.append(url)
        print(self.urls_to_check)
        
        CONFIG = 'jobminersserver/checkers/checkjobwebsite.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)

        # needed for performing jobandjobs or joborjobs logic
        self.jobandjobs = {}
        self.joborjobs = {}

    def check_urls(self):
        """
        Used after the url property of the object has been set.

        Returns
        -------
            dict:
                of the following format
                Eg:
                {
                    {
                        "url": www.merojob.com  # url checked.
                        "status": True  # status whether it is job website. True if yes else False
                    }
                }
        """
        job_website_urls = []
        for url in self.urls_to_check:
            print(f"Verifying {url}")
            if self.check_single_url(url): job_website_urls.append(url)

        return job_website_urls
        
    
    def check_single_url(self, url):
        """
        Checks single url and returns True if it is a job website.

        Parameters
        ----------
        url: str
            url to check if it is a job website or not.
        job_or_jobs_nepal: boolean, optional
            Set if job or jobs nepal keyword is to be checked instead of job
            and jobs and nepal.

        Returns
        -------
        boolean
            True if self.analyze_keywords() or in general terms, it is a job website.
            else False.
        """
        # check if jobs domain present in url or it is not interested website.   
        if parse.urlsplit(url).netloc[0:5] == 'jobs.' \
        or not is_interested_website(url[:-1]):
            return False

        # Try to get html content from the url.
        req = request(url)
        html = req.request_html()

        meta_info = []
        # Get title tag contents
        title = TagProcessor(html, tag='title')
        title_content = title.get_content()
        if title_content: meta_info += title_content

        # Get meta tag keywords, description, og title & description
        meta_tag = MetaTagProcessor(html)
        meta_info += meta_tag.get_keywords()
        meta_info += meta_tag.get_description()
        meta_info += meta_tag.get_og_title()
        meta_info += meta_tag.get_og_description()

        # job, jobs and nepal must keywords
        self.jobandjobs = self.analyze_keywords(meta_info)
        # job or jobs and nepal must keywords
        self.joborjobs = self.analyze_keywords(meta_info, job_or_jobs_nepal=True)

        # if both parameters false, return False.
        if not self.jobandjobs and not self.joborjobs: return False

        # check if nepali website with abroad based ads.
        if self.check_if_abroad_based(meta_info): return False

        return True

    def analyze_keywords(self, meta_info, job_or_jobs_nepal=False):
        """
        Check if a website is job website or not based on meta_info. 

        Parameters
        ----------
            meta_info: list of strings
                meta_info here refers to all the content present in 
                the title tag, meta name = description,
                title, property = og:title, og: description.
            job_or_jobs_nepal: boolean
                job or jobs nepal specifies which type of checking we need.        
                There are two methods for checking:
                1. Default way: job and jobs nepal; here the keywords job, jobs and
                nepal is to be present in the urls's meta info.
                2. Job or Jobs Nepal: Here either job or jobs word and nepal word is 
                to be present in the url's meta info.

        Returns
        -------
        boolean
            True if the parameter specified keywords are present.
            False if not present or there are no keywords in the metainfo part.
        
        Raises
        ------
            No Exception. Exception gets activated when meta_info is not present.
        """
        # Job Website Checking Related Info

        must_keywords = self.parser.get('global', 'must_keywords').split(',')
        must_keywords = [keyword.strip() for keyword in must_keywords]
        
        # Default conditon_to_use is False because we want to use job and jobs
        condition_to_use = False
        # For computing job_or_jobs_nepal results.
        joborjobs = []
        if job_or_jobs_nepal:
            # extract job and jobs into a list for checking in meta info or not.
            joborjobs = [must_keywords.pop(0), must_keywords.pop(0)]
            condition_to_use = (joborjobs[0] in meta_info or joborjobs[1] in meta_info)

        try:
            # all keywords present 
            if all(keyword in meta_info for keyword in must_keywords) \
            or condition_to_use:
                return True
            else:
                return False
        except:
            # Exception gets activated when meta_info is not present.
            return False

    def check_if_abroad_based(self, meta_info):
        """
        Checks if a website is abroad based or non-abroad 
        based on analyzing it's meta_info.

        Parameters
        ----------
        meta_info: list of strings
            meta_info here refers to all the content 
            present in the title tag, meta name = description,
            title, property = og:title, og: description.

        Returns
        -------
        boolean
            True if ALL the abroad websites keywords are present.
            False if not present or there are no keywords in the metainfo part.
        """
        abroad_website_keywords = \
            self.parser.get('global', 'abroad_website_keywords').split(',')
        abroad_website_keywords = \
            [keyword.strip() for keyword in abroad_website_keywords]

        if set(abroad_website_keywords).issubset(set(meta_info)):
            return True
        return False


if __name__ == "__main__":
    urls = [
        'https://www.jobsnepal.com/',
        'https://merojob.com/',
        'https://www.ramrojob.com/',
        'https://www.kumarijob.com/',
        'https://www.merorojgari.com/',
        'https://getjobnepal.com/',
        'https://nepalhealthjob.com/',
        'https://jobs.unops.org/',
        'https://froxjob.com/',
        'https://kantipurjob.com/',
        'https://www.jobejee.com/',
        'https://jobs.unicef.org/',
        'https://www.sajhajobs.com/',
        'https://www.cmsjob.com/',
        'https://www.globaljob.com.np/',
        'https://medjobsnepal.com/',
        'httts://youtube.com/'
    ]
    obj = CheckJobWebsite(urls=urls)
    print(obj.check_urls())