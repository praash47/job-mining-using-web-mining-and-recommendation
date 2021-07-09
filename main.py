import sys
sys.path.insert(1, 'D:/job-mining-using-web-mining-and-recommendation/jobminersserver')
from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from checkers.checkjobwebsite import CheckJobWebsite

rg = RequestGoogle()
urls = rg.get_100_urls()

checker = CheckJobWebsite(urls)
job_and_jobs_nepal = checker.check()
job_or_jobs_nepal = checker.check(job_or_jobs_nepal=True)
print(job_and_jobs_nepal)
print(job_or_jobs_nepal)