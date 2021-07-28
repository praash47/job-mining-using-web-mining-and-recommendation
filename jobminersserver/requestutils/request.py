import sys
sys.path.insert(1,'D:\job-mining-using-web-mining-and-recommendation\jobminersserver\requestutils\request.py')

from requests import *
from bs4 import BeautifulSoup
from urllib import parse

from selenium import webdriver


class Request:
	"""
	A class to request html of webpage from urls
	and convert to text 

	Methods
	-------
	request_html(url)
		returns html in string from the url passed 

	check_homepage(url)
		returns true if url passed is homepage and has no subdomain
	"""
	def __init__(self, url):
		"""
		Parameters
		---------
		url : str
			url of the webpages
		"""
		self.url = url

	def check_homepage(self):
		"""
		Returns true if url is the homepage of the site
		returns false otherwise

		Parameters
		----------
		home_page: str
			home page of the url

		format: https://merojob.com
		"""
		home_page = parse.urlsplit(self.url).scheme + '://' + parse.urlsplit(self.url).netloc
		if(self.url == home_page): return True
		return False

	def get_only_homepage_based(self):
		"""
		Returns homepage from the extracted url

		eg:- https://unjobs.org from https://unjobs.org/duty_stations/nepal

		Paramters
		---------
		home_page: list
			homepage of the urls in the format https://unjobs.org
		"""
		home_page = [(parse.urlsplit(url).scheme + '://' + parse.urlsplit(url).netloc) for url in urls if (parse.urlsplit(url).scheme + '://' + parse.urlsplit(url).netloc) != '://']
		return (home_page)


	def request_html(self):
		"""
		Returns html from the url of the webpages.

		If webpage is not accessible print error message 
		"""
		try:
			html = get(self.url).text
		except:
			print("Error getting html from url")
			return ""
		return html

if __name__ == "__main__":
	urls = 'https://nepalhealthjob.com/'

	R1 = Request(urls)
	print(R1.request_html())
