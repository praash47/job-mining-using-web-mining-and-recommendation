"""
This file consists of class that is required to check whether a
website is a job website or not.
"""
from configparser import ConfigParser
import requests
import json

# Need while using main for debugging.
import sys
sys.path.insert(1, 'D:/job-mining-using-web-mining-and-recommendation/jobminersserver/tagprocessor')
from tagprocessor import TagProcessor
from metatagprocessor import MetaTagProcessor

class CheckJobWebsite:
    """
    Utilities required to check whether a website is job website or not.
    
    Methods
    -------
    check_urls()
        Returns dictionary of checked urls.
    check_single_url(url), @staticmethod
        Checks single url is job website url or not.
        * No need to initialize the class of this method for
        using this function.     
    """
    def __init__(self, urls=None):
        """
        Parameters
        ----------
        urls: list of strings, optional
            Strings here are individual urls.
        """
        self.urls_to_check = urls
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
        results = {}
        for (index, url) in enumerate(self.urls_to_check):
            print("Checking ", url)
            results[str(index)] = {}
            results[str(index)]['url'] = url
            # Check url one by one.
            status = CheckJobWebsite.check_single_url(url, job_or_jobs_nepal)
            results[str(index)]['status'] = status
        return results
    
    @staticmethod
    def check_single_url(url):
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
        # Try to get html content from the url.
        html = ''
        try: html = requests.get(url).content
        except: pass

        meta_info = []
        # Get title tag contents
        title = TagProcessor(html, tag='title')
        title_content = title.get_content()
        if title_content: meta_info += title_content

        # Get meta tag keywords, description, og title & description
        meta_tag = MetaTagProcessor(html)
        to_get = [
            meta_tag.get_keywords,
            meta_tag.get_description,
            meta_tag.get_og_title,
            meta_tag.get_og_description]
        # call each function one by one and append to meta_info.
        meta_info += [func() for func in to_get if func()]

        # job, jobs and nepal must keywords
        self.jobandjobs = CheckJobWebsite.check_job_website(meta_info)
        # job or jobs and nepal must keywords
        self.joborjobs = CheckJobWebsite.check_job_website(meta_info, job_or_jobs_nepal=True)

        return self.analyze_keywords()

    @staticmethod
    def check_job_website(meta_info, job_or_jobs_nepal=False):
        """
        Check if a website is job website or not based on meta_info. 

        Parameters
        ----------
            meta_info: list of strings
                meta_info here refers to all the content present in the title tag, meta name = description,
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
        CONFIG = 'jobminersserver/checkers/checkjobwebsite.ini'
        parser = ConfigParser()
        parser.read(CONFIG)

        must_keywords = parser.get('global', 'must_keywords').split(',')
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

    def analyze_keywords(self):
        # TODO: Need to analyze the jobandjobsnepal and joborjobsnepal keywords
        pass
        

if __name__ == "__main__":
    print(CheckJobWebsite.check_single_url('https://getjobnepal.com', job_or_jobs_nepal=True))