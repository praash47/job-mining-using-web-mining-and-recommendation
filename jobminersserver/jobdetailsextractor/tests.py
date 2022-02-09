import datefinder
import pytest
import spacy

from requestutils.request import Request

from checkers.models import JobWebsite

from jobdetailsextractor.exceptions import DeadlineNotFound

from .deadline import Deadline
from .main import JobDetails
from .models import Job
from .parameters import Parameters
from .skills import SkillSet


def test_deadline():
    actual_deadline = list(datefinder.find_dates("Feb. 11, 2022 23:55"))[0]
    html = ""
    with open("jobdetailsextractor/reqs/sample_deadline.txt") as deadline_html:
        html = "".join(deadline_html.readlines())
    request = Request(".")
    request.html = html
    deadline = Deadline(request.get_html_tree())
    deadline.get_deadline_date(html)
    assert deadline.deadline == actual_deadline
    assert deadline.xpath

    sample_html = "<span>Jan. 1, 2021 23:55</span>"
    request.html = sample_html
    deadline = Deadline(request.get_html_tree())
    with pytest.raises(DeadlineNotFound):
        deadline.get_deadline_date(sample_html)


def test_skills():
    skills_text = """    
    Skills Required 

    Strong knowledge in javascript
    Proficient in developing web applications
    Must have experience in web application development using VueJs or ReactJS
    Sound knowledge in working with restful API or GraphQL
    Proficient in understanding of code versioning tools, such as Git
    Good knowledge of SQL and No-SQL 
    Good knowledge of HTML and CSS (SCSS or similar) 
    
    Skills Preferred 

    Experience in developing applications using MEARN stack 
    Proficient in understanding of CI/CD pipeline
    Understanding differences between multiple delivery platforms, such as mobile vs. desktop, and optimizing output to match the specific platform
    Sound knowledge in unit testing
    Should have sound analytical skills and problem-solving skills
    """
    from backend.misc import log

    skills = SkillSet()
    skills.get_skills(skills_text)

    assert set(skills)


@pytest.mark.django_db
def test_jobdetailsextractor():
    job_url = "https://froxjob.com/sales-executive-68"
    job_title = "Sales Executive"
    job_website = JobWebsite.objects.create(url="https://merojob.com/", name="merojob")
    job_website.save()

    job = Job.objects.create(website=job_website, title=job_title, url=job_url)
    job.save()

    company_names = []
    # titles_combined.txt: 70,000 titles to match xpaths from.
    with open("jobdetailsextractor/reqs/company_names.txt") as company_names:
        company_names = [
            company_name.strip("\n") for company_name in company_names.readlines()
        ]

    job_details = JobDetails(job)
    job_details.fetch()
    job_details.get_details(company_names)
    job_details.store_into_database()

    job = Job.objects.get(title=job_title)
    assert job.description
    assert job.misc


@pytest.mark.django_db
def test_parameters():
    job_url = "https://merojob.com/account-officer-revenue-collection-2/"
    job_title = "Account Officer (Revenue Collection)"
    job_website = JobWebsite.objects.create(url="https://merojob.com/", name="merojob")
    job_website.save()

    job = Job.objects.create(website=job_website, title=job_title, url=job_url)
    job.save()

    job_details = JobDetails(job)
    job_details.fetch()
    job_details.deadline._tree = job_details._tree

    company_names = []
    # titles_combined.txt: 70,000 titles to match xpaths from.
    with open("jobdetailsextractor/reqs/company_names.txt") as company_names:
        company_names = [
            company_name.strip("\n") for company_name in company_names.readlines()
        ]
    parameters = Parameters(
        job_details._get_job_block_xpath(),
        job_details._tree,
        company_names,
        website=job_website,
    )
    parameters_discovered = parameters.get_parameters_from_node(
        job_details._tree.getroot()
    )
    assert parameters_discovered

    parameters.values_from_xpaths()
    assert parameters.get_paragraph_values(parameters.keywords["description"])
    assert parameters.get_paragraph_values(parameters.keywords["misc"])
