import pytest

from datetime import datetime
from django.utils.timezone import make_aware

from .main import check_deadline_existing_job, check_new_job_urls_in_existing_websites

from checkers.models import JobWebsite
from jobdetailsextractor.models import Job


@pytest.mark.django_db
def test_check_deadline_existing_job():
    job_website = JobWebsite.objects.create(url='https://merojob.com/')
    job_website.save()

    non_expired_job = Job.objects.create(
        title="Frontend Developer",
        website=job_website,
        url=".",
        deadline=make_aware(datetime.fromisoformat('2055-01-02'))
    )
    expired_job = Job.objects.create(
        title="Expired Job",
        website=job_website,
        url=".",
        deadline=make_aware(datetime.fromisoformat('2021-02-12'))
    )
    non_expired_job.save()
    expired_job.save()
    check_deadline_existing_job()

    # Check if the Expired job is removed and the non expired is still present.
    assert Job.objects.filter(title="Frontend Developer").first()
    assert not Job.objects.filter(title="Expired Job").first()


@pytest.mark.django_db
def test_check_new_job_urls_in_existing_websites():
    job_website = JobWebsite(
        url=".",
        search_url="interactor/reqs/search_file_sample.html",
        job_title_xpath='/html/body/form/div/div[3]/div[1]/div[2]/div[4]/div[|]/div[1]/div/div[2]/h1/a'
    )
    job_website.save()

    check_new_job_urls_in_existing_websites()

    # Check if the Business Analyst (one of the jobs present in the sample) is present in the test database.
    assert Job.objects.filter(title="\nBusiness Analyst\n").first()
