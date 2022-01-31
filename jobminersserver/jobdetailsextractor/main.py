"""
This file acts as the main flow for the jobdetailsextractor and abstracts all the details that are performed by it's submodules. This module is responsible for extraction of the job parameters like job location, description etc and skills. It's submodules are deadline, parameters and skills.

Classes
-------
JobDetails()
    Job Details object which is responsible for extraction of skills and parameters and storing into the database.
"""
import logging
import re

from .deadline import Deadline
from .parameters import Parameters
from .skills import SkillSet

from backend.misc import common_start, read_config
from jobdetailsextractor.exceptions import DeadlineNotFound, DeadlineXpathNotFound, NameXpathNotFound
from requestutils.request import Request

mainlogger = logging.getLogger('main')
logger = logging.getLogger('jobdetailsextractor')


class JobDetails:
    """
    Job Details object with parameters and skills which facilitates it's extractions and storing into the database.

    Parameters
    ----------
    url: str
        url of the job to extract details from
    name: str
        name of the job to extract details from
    """
    def __init__(self, url, name):
        # Main Required Details
        self.url = url
        self.name = name

        # HTML tree related
        self.html_page = None
        self.tree = None
        self.job_block_xpath = None

        # The main variables
        self.parameters = None
        self.skill_set = SkillSet()

        # for parameter options
        self.parser = read_config('jobdetailsextractor/reqs/extraction_options.ini')

        # Get Website, store if not there.
        from .models import Job
        self.website = Job.objects.filter(url=self.url).first().website
        self.deadline = Deadline(self.tree)

    def fetch(self):
        """
        ** Call this first
        Fetches HTML content from server, extracts out the tree and does some minor pre-processing.
        """
        request = Request(self.url)
        request.request_html()
        request.filter_unnecessary_tags()

        self.html_page = request.html
        self.tree = request.get_html_tree()

    def get_details(self, nlp):
        """
        ** Call this after calling fetch()
        Extracts out job details from the HTML page including the skill-set of the job.
        
        Parameters
        ----------
        nlp: spacy
            Spacy object with nlp
        """
        self.deadline._tree = self.tree
        self.parameters = \
            Parameters(
                self.get_job_block_xpath(),
                self.tree,
                nlp,
                self.website,
            )

        self.parameters.get_core_parameters()
        self.skill_set.get_skills(
            self.parameters.parameters_dict['description'] +
            self.parameters.parameters_dict['misc']
        )

    def get_job_block_xpath(self):
        """
        Gets the job block xpath from the html text.
        
        Job block is the block excluding all of the other content from page, which includes the block where the details of the job are present.
        """
        job_block_xpath = '/'
        name_xpath = ''
        try:
            name_xpath = self.get_name_xpath()
            self.deadline.get_deadline_date(self.html_page)
        except DeadlineNotFound:
            pass
            # job = Job.objects.get(self.url)
            # send_event('backend_daemon', 'message', {
            #     'currentMessage': f'Deleting job advert for {job.url}: Deadline Expired.',
            #     'messagePriority': 'error'
            # })
            # job.delete()
        except NameXpathNotFound:
            pass
        except DeadlineXpathNotFound:
            pass

        else: 
            # If deadline date is found, find the common xpath between the deadline and name xpath.
            common_xpath = common_start(self.deadline.xpath, name_xpath)
            common_xpath_list = common_xpath.split('/')
            job_block_xpath = '/'.join(
                common_xpath_list[:len(common_xpath_list)-1])

        return job_block_xpath

    def get_name_xpath(self):
        """
        Extracts out and returns the name xpath using job name from the HTML document.

        Returns
        -------
        name_xpath
            xpath of the name in the HTML document
        """
        try:
            name_xpaths = self.tree.xpath(
                f'//*[normalize-space(text()= \'"{self.name}"\')]')
            title_xpaths = []
            # If one found, just accept directly.
            if len(name_xpaths) == 1:
                title_xpaths.append(self.tree.getpath(name_xpaths[0]))
            else:
                # If more than one, just search for the h1 - h6, because the name xpath we are interested in most is in the header tags.
                for xpath in name_xpaths:
                    if re.search('^h[1-6]$', xpath.tag):
                        element = self.tree.xpath(
                            f"//{xpath.tag}[normalize-space(text()= \"'{str(xpath.text_content())}'\")]")[0]
                        title_xpaths.append(self.tree.getpath(element))

                return title_xpaths[0]
        except: raise NameXpathNotFound

    def store_into_database(self):
        """
        Stores the job details into the database.
        """
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
            if self.parameters.parameters_dict['n_vacancy']:
                job.n_vacancy = re.findall(
                    r'\d+', self.parameters.parameters_dict['n_vacancy'])[0]
            job.level = self.parameters.parameters_dict['level']
            job.qualifications = self.parameters.parameters_dict['qualifications']
            job.experiences = self.parameters.parameters_dict['experiences']
            job.misc = self.parameters.parameters_dict['misc']
            job.extracted = True
            job.save()
        except Exception as e:
            logger.info(f'{e}')


if __name__ == '__main__':
    job_details = JobDetails(
        'https://merojob.com/officer-corporate-advisory/', '''Hub Manager''')
    job_details.fetch()
    job_details.get_details()
    job_details.store_into_database()
