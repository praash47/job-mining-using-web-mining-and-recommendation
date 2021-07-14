import sys
sys.path.insert(1, 'D:/job-mining-using-web-mining-and-recommendation/jobminersserver')
from requestutils.requestgooglemodule.requestgoogle import RequestGoogle
from checkers.checkjobwebsite import CheckJobWebsite

rg = RequestGoogle()
urls = rg.get_100_urls()

checker = CheckJobWebsite(urls)
job_urls = checker.check_urls()
print(job_urls)