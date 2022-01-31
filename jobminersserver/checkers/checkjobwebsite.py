"""
This file consists of class that is required to check whether a
website is a job website or not.

Classes
-------
CheckJobWebsite(urls=None)
    checks if a website is job website or not.
"""
import logging
from urllib import parse

from .models import JobWebsite

from .misccheckers import is_interested_website

from backend.misc import read_config
from requestutils.request import Request
from tagprocessor.tagprocessor import TagProcessor
from tagprocessor.metatagprocessor import MetaTagProcessor


logger = logging.getLogger('checkjobs')
mainlogger = logging.getLogger('main')


class CheckJobWebsite:
    """
    Utilities required to check whether a website is job website or not.

    Methods
    -------
    check_urls()
        Returns dictionary of checked urls.
    check_single_url(url)
        Checks single url is job website url or not.    
    """

    def __init__(self, urls=None):
        """
        Parameters
        ----------
        urls: list of strings, optional
            Strings here are individual urls.
        """
        logger.info('CheckJobWebsite object created')
        mainlogger.info('Checking Homepage based websites:')
        self._urls_to_check = []
        if urls:
            for url in urls:
                req = Request(url)
                # Only homepage based websites: like https://www.merojob.com not, https://www.facebook.com/jobminers
                if req.check_homepage():
                    self._urls_to_check.append(url)
        logger.info(f'Only Homepage based websites: {self._urls_to_check}')

        self._parser = read_config('checkers/checkjobwebsite.ini')

        # needed for performing _jobandjobs or joborjobs logic
        self._jobandjobs = {}
        self._joborjobs = {}

    def check_urls(self):
        """
        Used after the url property of the object has been set.

        Returns
        -------
            dict:
                of the following format
                Eg:
                {
                    {
                        "url": www.merojob.com  # url checked.
                        "status": True  # status whether it is job website. True if yes else False
                    }
                }
        """
        job_websites = []
        for url in self._urls_to_check:
            if not JobWebsite.objects.filter(url=url).first():
                if self.check_single_url(url):
                    logger.info(f"Verifying {url}")
                    mainlogger.info(f"Verifying {url}")
                    # extraction of domain name i.e. merojob from https://merojob.com
                    domain_name = self._get_domain_name(url)

                    job_websites.append(url)
                    job_website = JobWebsite.objects.create(
                        url=url,
                        name=domain_name
                    )
                    job_website.save()

        logger.info(f"Verified {job_websites} to be new job websites.")
        mainlogger.info(f"Verified {job_websites} to be new job websites.")

        return job_websites

    def check_single_url(self, url):
        """
        Checks single url and returns True if it is a job website.

        Parameters
        ----------
        url: str
            url to check if it is a job website or not.
        job_or_jobs_nepal: boolean, optional
            Set if job or jobs nepal keyword is to be checked instead of job
            and jobs and nepal.

        Returns
        -------
        boolean
            True if self._analyze_keywords() or in general terms, it is a job website.
            else False.
        """
        # check if jobs domain present in url or it is not interested website.
        if parse.urlsplit(url).netloc[0:5] == 'jobs.' \
                or not is_interested_website(url[:-1]):
            logger.info(f"{url} failed the jobs. test")
            return False

        # Try to get html content from the url.
        req = Request(url)
        html = req.request_html()

        meta_info = CheckJobWebsite.collect_meta_info(html)

        # job, jobs and nepal must keywords
        self._jobandjobs = self._analyze_keywords(meta_info)
        # job or jobs and nepal must keywords
        self._joborjobs = self._analyze_keywords(
            meta_info, job_or_jobs_nepal=True)

        # if both parameters false, return False.
        if not self._jobandjobs and not self._joborjobs:
            logger.info(f"{url} failed the andorjob test")
            return False

        # check if nepali website with abroad based ads.
        if self._check_if_abroad_based(meta_info):
            logger.info(
                f"{url} is an abroad based job website. Thus, ignored.")
            return False

        return True

    @staticmethod
    def collect_meta_info(html):
        """
        Collects meta info and returns from the html.

        Parameters
        ----------
        html: str
            html string to collect meta info from

        Returns
        -------
        list
            list of meta_info keywords
        """
        meta_info = []
        # Get title tag contents
        title = TagProcessor(html, tag='title')
        title_content = title.get_content()
        if title_content:
            meta_info += title_content

        # Get meta tag keywords, description, og title & description
        meta_tag = MetaTagProcessor(html)
        meta_info += meta_tag.get_keywords()
        meta_info += meta_tag.get_description()
        meta_info += meta_tag.get_og_title()
        meta_info += meta_tag.get_og_description()

        return meta_info

    def _analyze_keywords(self, meta_info, job_or_jobs_nepal=False):
        """
        Check if a website is job website or not based on meta_info. 

        Parameters
        ----------
            meta_info: list of strings
                meta_info here refers to all the content present in 
                the title tag, meta name = description,
                title, property = og:title, og: description.
            job_or_jobs_nepal: boolean
                job or jobs nepal specifies which type of checking we need.        
                There are two methods for checking:
                1. Default way: job and jobs nepal; here the keywords job, jobs and
                nepal is to be present in the urls's meta info.
                2. Job or Jobs Nepal: Here either job or jobs word and nepal word is 
                to be present in the url's meta info.

        Returns
        -------
        boolean
            True if the parameter specified keywords are present.
            False if not present or there are no keywords in the metainfo part.

        Raises
        ------
            No Exception. Exception gets activated when meta_info is not present.
        """
        # Job Website Checking Related Info

        must_keywords = self._parser.get('global', 'must_keywords').split(',')
        must_keywords = [keyword.strip() for keyword in must_keywords]

        # Default conditon_to_use is False because we want to use job and jobs
        condition_to_use = False
        # For computing job_or_jobs_nepal results.
        joborjobs = []
        if job_or_jobs_nepal:
            # extract job and jobs into a list for checking in meta info or not.
            joborjobs = [must_keywords.pop(0), must_keywords.pop(0)]
            condition_to_use = (
                joborjobs[0] in meta_info or joborjobs[1] in meta_info)

        try:
            # all keywords present
            if all(keyword in meta_info for keyword in must_keywords) \
                    or condition_to_use:
                return True
            else:
                return False
        except:
            # Exception gets activated when meta_info is not present.
            return False

    def _check_if_abroad_based(self, meta_info):
        """
        Checks if a website is abroad based or non-abroad 
        based on analyzing it's meta_info.

        Parameters
        ----------
        meta_info: list of strings
            meta_info here refers to all the content 
            present in the title tag, meta name = description,
            title, property = og:title, og: description.

        Returns
        -------
        boolean
            True if ALL the abroad websites keywords are present.
            False if not present or there are no keywords in the metainfo part.
        """
        abroad_website_keywords = \
            self._parser.get('global', 'abroad_website_keywords').split(',')
        abroad_website_keywords = \
            [keyword.strip() for keyword in abroad_website_keywords]

        if set(abroad_website_keywords).issubset(set(meta_info)):
            return True
        return False

    @staticmethod
    def _get_domain_name(url):
        """
        Returns the domain name. For instance: https://merojob.com's domain name is merojob.

        Parameters
        ----------
        url: str
            url string to extract domain name from

        Returns
        -------
        str
            domain_name of the url
        """
        domain_name = parse.urlparse(url).hostname.split('.')
        return [domain_name[0] if (len(
            domain_name) == 2 or len(domain_name) == 3) and domain_name[0] != 'www' 
            else domain_name[1]][0]
        

if __name__ == "__main__":
    # urls = [
    #     'https://www.jobsnepal.com/',
    #     'https://merojob.com/',
    #     'https://www.ramrojob.com/',
    #     'https://www.kumarijob.com/',
    #     'https://www.merorojgari.com/',
    #     'https://getjobnepal.com/',
    #     'https://nepalhealthjob.com/',
    #     'https://jobs.unops.org/',
    #     'https://froxjob.com/',
    #     'https://kantipurjob.com/',
    #     'https://www.jobejee.com/',
    #     'https://jobs.unicef.org/',
    #     'https://www.sajhajobs.com/',
    #     'https://www.cmsjob.com/',
    #     'https://www.globaljob.com.np/',
    #     'https://medjobsnepal.com/',
    #     'httts://youtube.com/'
    # ]
    urls = ['https://www.jobsnepal.com/', 'https://merojob.com/', 'https://openknowledge.worldbank.org/handle/10986/33956', 'https://www.ramrojob.com/', 'https://pubmed.ncbi.nlm.nih.gov/30771663/', 'https://unjobs.org/duty_stations/nepal', 'https://pubmed.ncbi.nlm.nih.gov/31735939/', 'https://juniperpublishers.com/jojnhc/JOJNHC.MS.ID.555814.php', 'https://np.usembassy.gov/jobs/', 'https://blogs.worldbank.org/jobs/job-quality-nepal-improving-women-lag-behind', 'https://www.educatenepal.com/notice_announcements/mobile/list-of-government-jobs-in-nepal', 'https://www.colgate.edu/news/stories/anna-kosa-14-brings-international-relations-background-un-job-nepal', 'https://www.worldbank.org/en/country/nepal', 'https://us.nepalembassy.gov.np/vacancy-announcement-2/', 'https://www.reuters.com/article/health-coronavirus-nepal/nearly-a-quarter-of-nepals-workers-lose-jobs-due-to-coronavirus-central-bank-idINKCN2591A8', 'https://www.indeed.com/q-Nepal-jobs.html', 'https://app.smartsheet.com/b/form/b78db7f6cdb54d2cb0f91d1ab573aa13', 'https://www.naukri.com/jobs-in-nepal', 'https://www.business-humanrights.org/en/latest-news/nepal-labour-ministry-records-over-500000-job-losses-both-home-and-abroad-amid-covid-19-pandemic/', 'https://jobs.gecareers.com/healthcare/global/en/job/R3568994/Territory-Manager', 'https://www.readglobal.org/read-offices/read-nepal/read-nepal-job-openings/', 'https://nepal.mercycorps.org/vacancy-announcement/', 'https://www.justice.gov/archives/criminal-icitap/blog/nepal-icitap-partners-nepal-police-complete-job-task-analysis-criminal', 'https://www.kumarijob.com/', 'https://www.linkedin.com/jobs/nepali-jobs', 'https://www.upwork.com/freelance-jobs/nepali/', 'http://www.ipsnews.net/2021/01/wanted-affirmative-legislation-job-market-nepal/', 'https://www.facebook.com/pages/category/Advertising-Marketing/Anmol-Job-Nepal-100804748041220/', 'https://np.linkedin.com/jobs', 'http://www.xinhuanet.com/english/2019-02/13/c_137819124.htm', 'http://cotiviti.com.np/jobs', 'https://jobs.undp.org/cj_view_job.cfm?cur_job_id=98159', 'https://www.usaid.gov/nepal/vacancy-announcements/21-02-human-resources-assistant-fsnpsc-9', 'https://getjobnepal.com/', 'https://www.rollingnexus.com/jobs', 'https://www.ustraveldocs.com/np/np-niv-typework.asp', 'https://www.solidaritycenter.org/publication/rebuilding-nepal-creating-good-job-amid-reconstruction-migration/', 'https://kathmandupost.com/national/2021/07/31/for-israeli-job-a-nepali-worker-needs-to-invest-around-rs165-700', 'https://eeas.europa.eu/delegations/nepal/90609/vacancy-administrative-assistant_en', 'https://rtiint.referrals.selectminds.com/international/jobs/chief-of-party-nepal-early-grade-learning-5877', 'https://www.collegenp.com/vacancy', 'https://www.who.int/nepal/careers', 'https://servlife.org/nepal-field-agent-job-description/', 'https://bmcnurs.biomedcentral.com/articles/10.1186/s12912-019-0379-2', 'https://thehimalayantimes.com/nepal/israel-announces-1000-job-vacancies-for-nepalis', 'https://jobs.unops.org/', 'https://jobs.unicef.org/fr/job/541328/individual-contractor-supply-manager-unicef-nepal-2-months', 'https://www.instagram.com/phalanojob/?hl=en', 'https://www.csmonitor.com/World/Making-a-difference/2013/1122/Olga-Murray-found-a-second-career-educating-the-children-of-Nepal', 'https://www.jobejee.com/', 'https://www.glassdoor.com/Job/nepal-systems-analyst-jobs-SRCH_IL.0,5_IN181_KO6,21.htm', 'https://www.merorojgari.com/',
            'https://www.workforgood.org/employer/471431/nepal-youth-foundation/', 'https://www.payscale.com/research/NP/Job=Accountant/Salary', 'https://nepalhealthjob.com/', 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4676855/', 'https://www.ifj.org/media-centre/news/detail/category/press-releases/article/nepal-union-officials-arrested-protesting-job-losses.html', 'https://documents.worldbank.org/en/publication/documents-reports/documentdetail/501501592797725280/nepal-jobs-diagnostic', 'https://prabhubank.com/career/', 'http://federalgovernmentjobs.us/job-location/nepal.html', 'https://rollingnexus.com/blog/1/Government-Jobs-in-Nepal', 'https://www.pinterest.com/pin/589901251188033947/', 'https://www.international-alert.org/jobs/gender-and-peacebuilding-adviser-nepal', 'https://missoulian.com/news/local/knitted-together-montana-nepal-partnership-builds-jobs-and-security/article_e95bc8f1-c999-5eb7-8b49-693185c925f2.html', 'https://www.flexjobs.com/remote-jobs/company/nepal_youth_foundation', 'https://blogs.uofi.uic.edu/view/8284/805783', 'https://www.savetherhino.org/poaching-crisis/assam-rocked-by-claims-kaziranga-poaching-is-an-insider-job-nepal-celebrates-two-poaching-free-years/', 'https://www.wfp.org/careers/job-openings', 'https://www.gsif.it/job-vacancy-program-manager-nepal-country-office/', 'https://www.tefl.org/tefl-jobs-centre/countries/tefl-jobs-in-nepal/', 'https://careers.wvi.org/job-opportunities-in-nepal', 'https://www.welthungerhilfe.org/news/latest-articles/i-love-my-job-emergency-response-team-in-nepal/', 'https://news.trust.org/item/20200715093743-vypfq/', 'https://www.financialnotices.com/career-notices.html', 'https://www.fhi360.org/careers', 'https://econpapers.repec.org/RePEc:wbk:jbsgrp:32149232', 'https://winrock.org/join-us/careers/job-openings/', 'https://www.nepalitimes.com/banner/missing-the-plot-in-nepals-job-scheme/', 'https://brainly.in/question/36161325', 'https://nepal.un.org/en/jobs', 'https://www.livemint.com/Consumer/7KFvNSxoIZ2T6qZumYQodO/LokSewa-Nepal-An-app-for-govt-job-openings.html', 'https://www.nepallivetoday.com/2021/07/27/israel-announces-1000-job-vacancies-for-nepalis/', 'https://www.ziprecruiter.com/Jobs/Nepali', 'https://www.nicasiabank.com/current-vacancies', 'https://www.np.undp.org/content/nepal/en/home/presscenter/articles/2020/Three-in-Five-employees-lost-their-jobs-due-to-COVID19-in-Nepal.html', 'https://spajumpmarco.com/jl1cknb/nepal-investigation-bureau-vacancy', 'https://unctad.org/press-material/job-creation-critical-durable-economic-progress-nepal', 'https://www.sajhajobs.com/', 'https://www.icranepal.com/career/', 'https://publichealthupdate.com/category/healthjobopportunities/', 'https://www.ilo.org/employment/Whatwedo/Publications/WCMS_502340/lang--en/index.htm', 'https://www.hindustantimes.com/india-news/former-ips-officer-accused-in-assam-police-job-scam-could-be-hiding-in-nepal/story-e01ojqxnPtTMD3Hkgi2WbI.html', 'https://www.theguardian.com/global-development/2013/sep/25/qatar-nepalese-workers-poverty-camps', 'https://www.nursingtimes.net/clinical-archive/critical-care/nurse-swaps-nhs-job-to-develop-icu-in-nepal-06-07-2012/', 'https://abtassociates.dejobs.org/npl/jobs/', 'https://www.allnepaljob.com/', 'https://m.facebook.com/Anmol-Job-Nepal-100804748041220/groups/?ref=page_internal&mt_nav=0', 'https://www.nepalyouthfoundation.org/get-involved/career/', 'https://capmh.biomedcentral.com/articles/10.1186/s13034-020-00319-5', 'https://www.unilever.com/careers/']
    obj = CheckJobWebsite(urls=urls)
    print(obj.check_urls())
