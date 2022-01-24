# from jobminersserver.requestutils.request import Request
from .deadline import Deadline
from lxml import html
from requestutils.request import Request
from jobdetailsextractor.models import Job

from configparser import ConfigParser
from .parameters import Parameters
from .skills import SkillSet

from backend.misc import common_start
from django_eventstream import send_event


import re

class JobDetails:
    def __init__(self, url, name):
        self.url = url
        self.name = name

        self.html_page = None
        self.tree = None
        
        self.job_block_xpath = None
        self.skill_set = SkillSet()
        self.parameters = None

        # for parameter options
        CONFIG = '/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver/jobdetailsextractor/extraction_options.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG)
        
        # Get Website and Website Structure, store if not there.
        from .models import WebsiteStructure, Job
        self.website = Job.objects.filter(url=self.url).first().website
        self.web_structure, _ = WebsiteStructure.objects.get_or_create(website=self.website)
        if self.web_structure.deadline_xpath:
            self.deadline = Deadline(self.tree, xpath=self.web_structure.deadline_xpath)
        else:
            self.deadline = Deadline(self.tree)

    def fetch(self):
        request = Request(self.url)
        request.request_html()
        request.filter_unnecessary_tags()

        self.html_page = request.html
        self.tree = request.get_html_tree()
    
    def get_details(self):
        self.deadline.tree = self.tree
        self.parameters = \
            Parameters(
                self.get_job_block_xpath(),
                self.tree,
                self.web_structure,
                self.website
            )
        
        self.parameters.get_core_parameters()
        self.skill_set.get_skills(
            self.parameters.parameters_dict['description'] + self.parameters.parameters_dict['misc']
        )

    def get_job_block_xpath(self):
        if not self.deadline.get_deadline_date(self.html_page):
            try:
                job = Job.objects.get(self.url)
                send_event('backend_daemon', 'message', {
                    'currentMessage': f'Deleting job advert for {job.url}: Deadline Expired.',
                    'messagePriority': 'error'
                })
                job.delete()
            except: pass
        name_xpath = self.get_name_xpath()
        
        if not self.web_structure.name_xpath and name_xpath: self.web_structure.name_xpath = name_xpath

        common_xpath = common_start(self.deadline.xpath, name_xpath)
        common_xpath_list = common_xpath.split('/')
        job_block_xpath = '/'.join(common_xpath_list[:len(common_xpath_list)-1])

        return job_block_xpath

    def get_name_xpath(self):
        try:
            if not self.web_structure.name_xpath:
                name_xpaths = self.tree.xpath(f'//*[normalize-space(text()= \'"{self.name}"\')]')
                title_xpaths = []
                if len(name_xpaths) == 1:
                    title_xpaths.append(self.tree.getpath(name_xpaths[0]))
                else:
                    for xpath in name_xpaths:
                        if re.search('^h[1-6]$', xpath.tag):
                            element = self.tree.xpath(f"//{xpath.tag}[normalize-space(text()= \"'{str(xpath.text_content())}'\")]")[0]
                            title_xpaths.append(self.tree.getpath(element))
                
                return title_xpaths[0]
            return self.web_structure.name_xpath
        except: return None

    def store_into_database(self):
        from .models import Job
        try: 
            job = Job.objects.get(url=self.url)
            job.deadline = self.deadline.deadline
            job.job_skills = set(self.skill_set)
            job.company_name = self.parameters.parameters_dict['company_name']
            job.company_info = self.parameters.parameters_dict['company_info']
            job.company_email = self.parameters.parameters_dict['company_email']
            job.location = self.parameters.parameters_dict['location']
            job.description = self.parameters.parameters_dict['description']
            job.salary = self.parameters.parameters_dict['salary']
            if self.parameters.parameters_dict['n_vacancy']: job.n_vacancy = re.findall(r'\d+', self.parameters.parameters_dict['n_vacancy'])[0]
            job.level = self.parameters.parameters_dict['level']
            job.qualifications = self.parameters.parameters_dict['qualifications']
            job.experiences = self.parameters.parameters_dict['experiences']
            job.misc = self.parameters.parameters_dict['misc']
            job.extracted = True
            job.save()
        except Exception as e: print(e)
        
if __name__ == '__main__':
    job_details = JobDetails('https://merojob.com/officer-corporate-advisory/', '''Hub Manager''')
    job_details.fetch()
    job_details.get_details()
    job_details.store_into_database()