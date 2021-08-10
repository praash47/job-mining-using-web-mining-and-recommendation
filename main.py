import sys
sys.path.append('/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver')

from jobminersserver.requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from jobminersserver.checkers.checkjobwebsite import CheckJobWebsite

rg = RequestGoogle()
urls = rg.get_100_urls()

checker = CheckJobWebsite(urls)
job_urls = checker.check_urls()
print(job_urls)