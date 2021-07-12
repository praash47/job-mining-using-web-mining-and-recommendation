import sys
sys.path.insert(1,'D:\job-mining-using-web-mining-and-recommendation\jobminersserver\requestutils\request.py')

from requests import *
from bs4 import BeautifulSoup
from urllib import parse

class request:
	'''
	A class to request html of webpage from urls
	and convert to text 

	Methods
	--------
	request_html(url)
		returns html in string from the url passed 

	text_from_html()
		return text seen in webpage from html string
	'''
	def __init__(self, url):
		'''
		Parameters
		---------
		url : str
				url of the webpages
		'''
		self.url = url

	def get_homepage(self):
		'''
		returns homepage from the extracted url

		eg:-https://unjobs.org from   https://unjobs.org/duty_stations/nepal
		'''
		home_page = parse.urlsplit(self.url).scheme + '://' + parse.urlsplit(self.url).netloc
		print(home_page)
		return (home_page)


	def request_html(self):
		'''
		returns html from the url of the webpages.

		If webpage is not accessible print error message 
		'''
		try:
			html = get(self.url).text
		except:
			print("Error getting html from url")
			return ""
		return html
url = "https://merojob.com/"

R1 = request(url)
R1.get_homepage()
html = R1.request_html()
print(html)

