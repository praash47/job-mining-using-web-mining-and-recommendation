import pytest

from scrapy.linkextractors import LinkExtractor

from .searcher import Search
from .paginator import Paginator
from .site import Site, NonAJAX
from .titleextractor import TitleExtractor


def test_searcher():
    url = 'https://www.kumarijob.com/'
    search = Search()
    assert search.get_search_url(
        url) == 'https://www.kumarijob.com/search?keywords='


def test_paginator():
    url = 'https://www.kumarijob.com/search?keywords='

    pages = Paginator()
    pages.page_url = url

    response = TitleExtractor.mock_scrapy_response(url)
    link_extractor = LinkExtractor()
    links = link_extractor.extract_links(response)
    site = Site(url)

    assert pages.has_pages(links) == True
    pages.get_last_page(links)
    pages.check_search_step(site, links)
    assert type(pages.last_page) is int
    assert pages.move_to_next_page() == 2
    assert pages.curr_page == 2
    assert pages.page_url == 'https://www.kumarijob.com/search?keywords=&page=2'


@pytest.mark.django_db
def test_site_non_ajax():
    url = 'https://www.kumarijob.com/search?keywords='
    site = Site(url)

    response = TitleExtractor.mock_scrapy_response(url)
    link_extractor = LinkExtractor()
    links = link_extractor.extract_links(response)
    na = NonAJAX(response, links, site, paginated=False)

    assert na.is_crawlable() == True

    title_xpath = '/html/body/div/div[1]/div[6]/div/div/div/div/div/div[|]/div[1]/div[2]/h5/a'

    na.get_jobs_for_page(title_xpath, response)
    
    assert na.jobs.keys()

def test_xpather():
    url = 'https://www.kumarijob.com/search?keywords='
    site = Site(url)

    response = TitleExtractor.mock_scrapy_response(url)
    link_extractor = LinkExtractor()
    links = link_extractor.extract_links(response)
    na = NonAJAX(response, links, site, paginated=False)

    assert na.xpaths.get_xpath(links) == '/html/body/div/div[1]/div[6]/div/div/div/div/div/div[|]/div[1]/div[2]/h5/a'

@pytest.mark.django_db
def test_titleextractor():
    url = 'https://www.kumarijob.com/search?keywords='
    title_extractor = TitleExtractor(url)

    assert title_extractor.extract_title_xpath() == '/html/body/div/div[1]/div[6]/div/div/div/div/div/div[|]/div[1]/div[2]/h5/a'

    title_extractor.extract_jobs_from_title_xpath(title_extractor.extract_title_xpath())
    assert title_extractor._jobs.keys()
