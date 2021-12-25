# from jobminersserver.requestutils.request import Request
from deadline import Deadline
import requests
from lxml import html

from configparser import ConfigParser
from parameters import Parameters
from skills import SkillSet


import re

class JobDetails:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.html_page = requests.get(self.url).content
        self.html_page = re.subn(r'<(script).*?</\1>(?s)', '', str(self.html_page))[0]
        # self.html_page = None
        # self.request = Request(url)
        self.tree = None
        self.job_block_xpath = None
        self.skill_set = SkillSet()
        self.parameters = None

        # for parameter options
        CONFIG = '/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver/jobdetailsextractor/extraction_options.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        
        from .models import WebsiteStructure, Job
        self.website = Job.objects.get(url=self.url).website
        
        self.web_structure, _ = WebsiteStructure.objects.get_or_create(website=self.website)
        if self.web_structure.deadline_xpath:
            self.deadline = Deadline(xpath=self.web_structure.deadline_xpath)
        else:
            self.deadline = Deadline()

    def fetch(self):
        # self.html_page = self.request.request_html()
        # self.tree = self.request.request_html_tree()
        resp_html = html.fromstring(self.html_page)
        self.tree = resp_html.getroottree()
    
    def get_details(self):
        self.parameters = \
            Parameters(
                self.get_job_block_xpath(),
                self.tree,
                self.web_structure,
                self.website
            )
        
        company_name_xpath = self.web_structure.company_name_xpath
        company_desc_xpath = self.web_structure.company_description_xpath
        location_xpath = self.web_structure.location_xpath
        desc_xpath = self.web_structure.job_description_xpath
        salary_xpath = self.web_structure.salary_xpath
        no_vacancy_xpath = self.web_structure.no_vacancy_xpath
        level_xpath = self.web_structure.level_xpath
        qualification_xpath = self.web_structure.qualification_xpath
        experience_xpath = self.web_structure.experience_xpath
        
        parameters_xpath_dict = None
        if location_xpath:
            parameters_xpath_dict = {
                "company_name_xpath":company_name_xpath,
                "company_info_xpath":company_desc_xpath,
                "location_xpath":location_xpath,
                "description_xpath":desc_xpath,
                "salary_xpath":salary_xpath,
                "n_vacancy_xpath":no_vacancy_xpath,
                "level_xpath":level_xpath,
                "qualifications_xpath":qualification_xpath,
                "experiences_xpath":experience_xpath
            }
        
        self.parameters.get_core_parameters(xpaths_dict=parameters_xpath_dict)
        self.skill_set.get_skills(self.parameters.parameters_dict['description'])

    def get_job_block_xpath(self):
        self.deadline.tree = self.tree
        self.deadline.get_deadline_date(self.html_page)
        if not self.web_structure.deadline_xpath: self.web_structure.deadline_xpath = self.deadline.xpath
        name_xpath = self.get_name_xpath()
        
        if not self.web_structure.name_xpath and name_xpath: self.web_structure.name_xpath = name_xpath

        common_xpath = self.common_start(self.deadline.xpath, name_xpath)
        common_xpath_list = common_xpath.split('/')
        job_block_xpath = '/'.join(common_xpath_list[:len(common_xpath_list)-1])

        return job_block_xpath

    def get_name_xpath(self):
        try:
            if not self.web_structure.name_xpath:
                name_xpaths = self.tree.xpath(f'//*[text()="{self.name}"]')
                title_xpaths = []
                if len(name_xpaths) == 1:
                    title_xpaths.append(self.tree.getpath(name_xpaths[0]))
                else:
                    for xpath in name_xpaths:
                        if re.search('^h[1-6]$', xpath.tag):
                            element = self.tree.xpath(f"//{xpath.tag}[contains(text(), '{str(xpath.text_content())}')]")[0]
                            title_xpaths.append(self.tree.getpath(element))
                
                return title_xpaths[0]
            return self.web_structure.name_xpath
        except: return None

    @staticmethod
    def common_start(sa, sb):
        """
        Returns the longest common substring from the beginning of sa and sb

        Parameters
        ----------
        sa: string
            string 'a' to compare
        sb: string
            string 'b' to compare
        # ref: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
        
        Returns
        -------
        string
            common part between sa and sb.
        """
        def _iter():
            for a, b in zip(sa, sb):
                if a == b:
                    yield a
                else:   
                    return

        return ''.join(_iter())

    def store_into_database(self):
        from .models import Job
        job = Job.objects.get(website=self.website, url=self.url)
        job.deadline = self.deadline.deadline
        job.job_skills = set(self.skill_set)
        job.company_name = self.parameters.parameters_dict['company_name']
        job.company_info = self.parameters.parameters_dict['company_info']
        job.company_email = self.parameters.parameters_dict['company_email']
        job.location = self.parameters.parameters_dict['location']
        job.description = self.parameters.parameters_dict['description']
        job.salary = self.parameters.parameters_dict['salary']
        job.n_vacancy = self.parameters.parameters_dict['n_vacancy']
        job.level = self.parameters.parameters_dict['level']
        job.qualifications = self.parameters.parameters_dict['qualifications']
        job.experiences = self.parameters.parameters_dict['experiences']
        job.misc = self.parameters.parameters_dict['misc']
        if self.parameters.parameters_dict['company_name'] and self.parameters.parameters_dict['company_info']:
            job.extracted = True
        job.save()
        
if __name__ == '__main__':
    job_details = JobDetails('https://merojob.com/hub-manager-9/', '''Hub Manager''')
    job_details.fetch()
    job_details.get_details()
    job_details.store_into_database()