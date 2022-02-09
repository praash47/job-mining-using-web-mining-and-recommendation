import pytest

from checkers.checkjobwebsite import CheckJobWebsite
from requestutils.request import Request

from .misccheckers import is_interested_website


def test_is_interested_website():
    assert is_interested_website("https://play.google.com") == False
    assert is_interested_website("https://youtube.com") == False
    assert is_interested_website("https://www.youtube.com") == False
    assert is_interested_website("https://www.facebook.com") == False
    assert is_interested_website("https://merojob.com") == True


@pytest.mark.django_db
def test_checkers_check_urls():
    urls_to_test = [
        "https://www.jobsnepal.com/",
        "https://merojob.com/",
        "https://www.ramrojob.com/",
        "https://www.kumarijob.com/",
        "https://www.merorojgari.com/",
        "https://getjobnepal.com/",
        "https://nepalhealthjob.com/",
        "https://jobs.unops.org/",
        "https://froxjob.com/",
        "https://kantipurjob.com/",
        "https://www.jobejee.com/",
        "https://jobs.unicef.org/",
        "https://www.sajhajobs.com/",
        "https://www.cmsjob.com/",
        "https://www.globaljob.com.np/",
        "https://medjobsnepal.com/",
        "httts://youtube.com/",
    ]
    checker = CheckJobWebsite(urls=urls_to_test)
    job_websites = checker.check_urls()
    actual_job_websites = [
        "https://www.jobsnepal.com/",
        "https://merojob.com/",
        "https://www.ramrojob.com/",
        "https://www.kumarijob.com/",
        "https://www.merorojgari.com/",
        "https://getjobnepal.com/",
        "https://froxjob.com/",
        "https://kantipurjob.com/",
        "https://www.jobejee.com/",
    ]

    assert sorted(job_websites) == sorted(actual_job_websites)


def test_checkers_check_if_abroad_based():
    abroad_based = "https://www.sajhajobs.com/"
    non_abroad_based = "https://www.jobsnepal.com/"

    abroad_html = Request(abroad_based).request_html()
    non_abroad_html = Request(non_abroad_based).request_html()
    ab_meta_info = CheckJobWebsite.collect_meta_info(abroad_html)
    non_ab_meta_info = CheckJobWebsite.collect_meta_info(non_abroad_html)

    checkers = CheckJobWebsite()
    assert checkers._check_if_abroad_based(ab_meta_info) == True
    assert checkers._check_if_abroad_based(non_ab_meta_info) == False
