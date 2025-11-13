import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from datetime import date, timedelta
from scrapy.crawler import CrawlerProcess
import scrapy

# retreive today's date and set format
current_date = date.today()
current_date
cd = current_date.strftime("%d%m%Y")

browser = webdriver.Chrome()
PageNames_Bornepost=['news/sarawak/','news/sarawak/page/2/','news/sarawak/page/3/','news/sabah/','news/sabah/page/2/','news/sabah/page/3/','news/nation/','news/nation/page/2/','world/','business/','sports/','lite-stories/','features/','columns/']
article_url =[] #a list to store the urls extracted
# Navigate to the base URL
base_url = "https://www.theborneopost.com/category/"
for page in PageNames_Bornepost:
    url = base_url + page
    browser.get(url)
    # Wait for the page to load
    browser.implicitly_wait(10)
    # Create the dynamic XPath with string formatting
    xpath = "//a[@class='post-title']"
    # Find all the article links on the page using the dynamic XPath
    article_links = browser.find_elements(By.XPATH, xpath)
    # Extract and print the links
    for link in article_links:
        url = link.get_attribute("href")
        article_url.append(url)
browser.quit()

'''In the news links we are extracting there are chances for duplicate links since many articles are referenced in other pages also.
We need to remove those duplicates'''
unique_elements_set3 = set(article_url) #Convert the list of url to set to eliminate duplicates
news_links_list = list(unique_elements_set3) #convert the set back to list

#Scrape the content and title using scrapy
        
def run_scrapy_spider():
    class BorneoSpider(scrapy.Spider):
        name = "borneo_spider"
        custom_settings = {
            "FEEDS": {"BorneoArticles"+ "_" + str(cd)+ ".csv":{"format":"csv"}},
            }
        
        def start_requests(self):
            # Start crawling each URL
            for url in news_links_list:
                yield scrapy.Request(url=url, callback=self.parse)

        def parse(self, response):
        
            #Extract title and content of each webpage using css
            title = response.xpath("//h1/text()").getall()  
            #Extract the content and title using css
            content = response.xpath("//div[@class='post-content description ']//p[not(@class='wp-caption-text')]/text()").getall()
        
            self.log(f'Title: {title}')# for logging the data to scrapy
            #Return the data in the form of dictionary
            yield {
                'Title': title,
                'Content': content
                }
        
    process = CrawlerProcess()
    process.crawl(BorneoSpider)
    process.start()

# Function to compare yesterday's articles with today's articles
def compare_articles():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    
    y = yesterday.strftime("%d%m%Y")
    
    yesterdays_file = 'BorneoArticles_{}.csv'.format(y)
    todays_file = 'BorneoArticles_{}.csv'.format(time.strftime("%d%m%Y"))

#check if files with yesterdays date exists    
    if os.path.exists(yesterdays_file):
  
        yesterdays_articles = pd.read_csv(yesterdays_file)
        todays_articles = pd.read_csv(todays_file)
        
        df_non_match = pd.merge(todays_articles, yesterdays_articles, how='outer', indicator=True, on='Title')
        df_non_match = df_non_match[(df_non_match._merge == 'left_only')]

        result = df_non_match.iloc[:, 0:2]
        result = result.drop_duplicates()
        result.rename(columns={'Title_x' : 'Title',
                           'Content_x': 'Content'
                           }, inplace=True)
        result = result.dropna(axis = 0, subset=['Content']) #drop rows with no content 
        result.to_csv("BorneoArticles{}.csv".format(time.strftime("%d%m%Y")), index=False)
    else:
        todays_articles = pd.read_csv(todays_file)
        todays_articles.to_csv("BorneoArticles{}.csv".format(time.strftime("%d%m%Y")), index=False)
        return

# Run the Scrapy spider and extract articles
run_scrapy_spider()

# Compare yesterday's articles with today's articles
compare_articles()