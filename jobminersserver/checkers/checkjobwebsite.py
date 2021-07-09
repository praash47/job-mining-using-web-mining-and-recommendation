from configparser import ConfigParser
import requests

import sys
sys.path.insert(1, 'D:/job-mining-using-web-mining-and-recommendation/jobminersserver/tagprocessor')
import json

from tagprocessor import TagProcessor
from metatagprocessor import MetaTagProcessor

class CheckJobWebsite:
    def __init__(self, urls):
        self.urls_to_check = urls

    def check(self, job_or_jobs_nepal=False):
        results = {}
        for (index, url) in enumerate(self.urls_to_check):
            print("Checking ", url)
            results[str(index)] = {}
            results[str(index)]['url'] = url
            status = CheckJobWebsite.check_single_url(url, job_or_jobs_nepal)
            results[str(index)]['status'] = status
        return results
        with open('jobwebsitesL2.txt', 'w') as json_file:
            json.dump(results, json_file)
    
    @staticmethod
    def check_single_url(url, job_or_jobs_nepal=False):
        html = requests.get(url).content
        meta_info = []
    
        title = TagProcessor(html, tag='title')
        title_content = title.get_content()
        if title_content: meta_info += title_content

        meta_tag = MetaTagProcessor(html)
        to_get = [
            meta_tag.get_keywords,
            meta_tag.get_description,
            meta_tag.get_og_title,
            meta_tag.get_og_description]

        meta_info += [func() for func in to_get if func()]

        return CheckJobWebsite.check_job_website(meta_info, job_or_jobs_nepal=False)

    @staticmethod
    def check_job_website(meta_info, job_or_jobs_nepal=False):
        # Job Website Checking Related Info
        CONFIG = 'jobminersserver/checkers/checkjobwebsite.ini'
        parser = ConfigParser()
        parser.read(CONFIG)

        must_keywords = parser.get('global', 'must_keywords').split(',')
        score_plus_keywords = parser.get('global', 'score_plus_keywords').split(',')

        must_keywords = [keyword.strip() for keyword in must_keywords]
        score_plus_keywords = [keyword.strip() for keyword in score_plus_keywords]
        
        condition = True
        # For computing job_or_jobs_nepal results.
        jobandjobs = []
        if not job_or_jobs_nepal:
            jobandjobs = [must_keywords.pop(0), must_keywords.pop(0)]
            condition = (jobandjobs[0] in meta_info or jobandjobs[1] in meta_info)

        try:
            if all(keyword in meta_info for keyword in must_keywords) \
            and condition:
                return True
            else:
                return False
        except:
            return False

        

if __name__ == "__main__":
    print(CheckJobWebsite.check_single_url('https://www.merojob.com'))