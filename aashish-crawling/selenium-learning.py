from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = EdgeOptions()
options.use_chromium = True
options.add_argument('headless')

driver = Edge(executable_path="D:\python-learning\selenium-scrapy-learning\msedgedriver.exe", options=options)

driver.get("https://merojob.com/search/?q=")
print(driver.page_source)

# init = 0
# while(1):
#     try:
#         init += 3000
#         driver.execute_script(f"window.scrollTo(0, {init})")  
#         element = driver.find_element_by_link_text("Load more listings")
#         element.click()
#         driver.implicitly_wait(4)   
#     except: pass      