"""
This file acts as the main flow for the jobdetailsextractor and abstracts all the details that are performed by it's submodules. This module is responsible for extraction of the job parameters like job location, description etc and skills. It's submodules are deadline, parameters and skills.

Classes
-------
JobDetails()
Job Details object which is responsible for extraction of skills and parameters and storing into the database.
"""
import re

from backend.misc import common_start, log
from jobdetailsextractor.exceptions import (
    DeadlineNotFound,
    DeadlineXpathNotFound,
    NameXpathNotFound,
)
from requestutils.request import Request

from .deadline import Deadline
from .parameters import Parameters
from .skills import SkillSet


class JobDetails:
    """
    Job Details object with parameters and skills which facilitates it's extractions and storing into the database.

    Methods
    -------
    fetch()
        Used to fetch job details of the job from the server
    get_details(company_names)
        Used to get details of the job. company_names for checking of the company names in the details.
    store_into_database()
        Stores the job details that are extracted into the database.
    """

    def __init__(self, job):
        """
        Parameters
        ----------
        job: Job
            database object Job of the job that we are extracting details from.
        """
        # Main Required Details
        self._url = job.url
        self._name = job.title

        # HTML tree related
        self._html_page = None
        self._tree = None

        # The main variables
        self.parameters = None
        self.skill_set = SkillSet()

        # Get Website, store if not there.
        self.website = job.website
        self.deadline = Deadline(self._tree)
        log(
            "jobdetailsextractor",
            "info",
            f"Job Details, Skillset and Deadline object created for {self._name}: {self._url}",
        )
        log("main", "info", f"Extracting {self._name}: {self._url}")

    def fetch(self):
        """
        ** Call this first
        Fetches HTML content from server, extracts out the tree and does some minor pre-processing.
        """
        log("jobdetailsextractor", "info", f"Fetching HTML for: {self._url}")
        request = Request(self._url)
        request.request_html()
        request.filter_unnecessary_tags()

        self._html_page = request.html
        self._tree = request.get_html_tree()

    def get_details(self, company_names):
        """
        ** Call this after calling fetch()
        Extracts out job details from the HTML page including the skill-set of the job.

        Parameters
        ----------
        company_names: list
            company names list of 2001-2074
        """
        self.deadline._tree = self._tree
        self.parameters = Parameters(
            self._get_job_block_xpath(),
            self._tree,
            company_names,
            self.website,
        )
        self.parameters.get_core_parameters()
        self.skill_set.get_skills(
            self.parameters.parameters_dict["description"]
            + self.parameters.parameters_dict["misc"]
        )

        from .models import Job

        job = Job.objects.get(url=self._url)
        job.extracted = True
        job.save()

    def _get_job_block_xpath(self):
        """
        Gets the job block xpath from the html text.

        Job block is the block excluding all of the other content from page, which includes the block where the details of the job are present.
        """
        log("jobdetailsextractor", "info", f"Getting job block xpath")
        job_block_xpath = "/"
        name_xpath = ""
        try:
            log("jobdetailsextractor", "info", f"Getting name xpath")
            name_xpath = self._get_name_xpath()

            log("jobdetailsextractor", "info", f"Getting deadline date")
            self.deadline.get_deadline_date(self._html_page)

        except NameXpathNotFound:
            log("jobdetailsextractor", "error", f"Name Xpath Not Found")
            log("main", "error", f"Name Xpath Not Found")

            log("jobdetailsextractor", "info", f"Getting deadline date")
            self.deadline.get_deadline_date(self._html_page)

        except DeadlineNotFound:
            log(
                "jobdetailsextractor",
                "error",
                f"Deadline Not Found: maybe expired or unable to be detected",
            )
            log(
                "main",
                "error",
                f"Deadline Not Found: maybe expired or unable to be detected",
            )

        except DeadlineXpathNotFound:
            log("jobdetailsextractor", "error", f"Deadline Xpath Not Found")
            log("main", "error", f"Deadline Xpath Not Found")

        else:
            # If deadline date is found, find the common xpath between the deadline and name xpath.
            common_xpath = common_start(self.deadline.xpath, name_xpath)
            if common_xpath:
                common_xpath_list = common_xpath.split("/")
                job_block_xpath = "/".join(
                    common_xpath_list[: len(common_xpath_list) - 1]
                )

        return job_block_xpath

    def _get_name_xpath(self):
        """
        Extracts out and returns the name xpath using job name from the HTML document.

        Returns
        -------
        name_xpath
            xpath of the name in the HTML document
        """
        try:
            name_xpaths = self._tree.xpath(
                f"//*[normalize-space(text()= '\"{self._name}\"')]"
            )
            title_xpaths = []
            # If one found, just accept directly.
            if len(name_xpaths) == 1:
                title_xpaths.append(self._tree.getpath(name_xpaths[0]))
            else:
                # If more than one, just search for the h1 - h6, because the name xpath we are interested in most is in the header tags.
                for xpath in name_xpaths:
                    if re.search("^h[1-6]$", xpath.tag):
                        element = self._tree.xpath(
                            f"//{xpath.tag}[normalize-space(text()= \"'{str(xpath.text_content())}'\")]"
                        )[0]
                        title_xpaths.append(self._tree.getpath(element))

                return title_xpaths[0]
        except:
            raise NameXpathNotFound

    def store_into_database(self):
        """
        Stores the job details into the database.
        """
        from .models import Job

        try:
            job = Job.objects.get(url=self._url)
            job.deadline = self.deadline.deadline
            job.job_skills = set(self.skill_set)
            job.company_name = self.parameters.parameters_dict["company_name"]
            job.company_info = self.parameters.parameters_dict["company_info"]
            job.company_email = self.parameters.parameters_dict["company_email"]
            job.location = self.parameters.parameters_dict["location"]
            job.description = self.parameters.parameters_dict["description"]
            job.salary = self.parameters.parameters_dict["salary"]
            if self.parameters.parameters_dict["n_vacancy"]:
                job.n_vacancy = re.findall(
                    r"\d+", self.parameters.parameters_dict["n_vacancy"]
                )[0]
            job.level = self.parameters.parameters_dict["level"]
            job.qualifications = self.parameters.parameters_dict["qualifications"]
            job.experiences = self.parameters.parameters_dict["experiences"]
            job.misc = self.parameters.parameters_dict["misc"]
            job.save()
        except Exception as e:
            log("jobdetailsextractor", "error", f"{e}")


if __name__ == "__main__":
    job_details = JobDetails(
        "https://merojob.com/officer-corporate-advisory/", """Hub Manager"""
    )
    job_details.fetch()
    job_details.get_details()
    job_details.store_into_database()
