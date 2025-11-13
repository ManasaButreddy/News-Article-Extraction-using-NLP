from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from scrapy.crawler import CrawlerProcess
import scrapy
import os
import time
from datetime import date, timedelta
import boto3

# retreive today's date and set format
current_date = date.today()
current_date
cd = current_date.strftime("%d%m%Y")

#Extracting the links of each page from the Star website
browser = webdriver.Chrome()

page_url_list =[] #this is the list of urls pertaining to each categories mentioned in the home page.example:url of sport page,url of education page..
PageNames_Thestar=['starplus','news','aseanplus','business','sport','metro','lifestyle','food','tech','education','opinion','starpicks']

#iterate through the pages to collect the urls from each pages
for page in PageNames_Thestar:
    page_to_open = "https://www.thestar.com.my/" +str(page)
    page_url_list.append(page_to_open)


'''taking each page url from the 'page_url_list' and opening the page and extracting all the news 
article urls within that page and finally extracting all the news article urls within the website '''
news_links = []
for urls in page_url_list:
    browser.get(urls)
    browser.implicitly_wait(10)
    
    headings = browser.find_elements("xpath",'//h2') #extract headings of each news
    
    #On the webpage that is currently open, we create a list of all the news urls
    # Extract the links from the headings
    
    for heading in headings:
        link = heading.find_element(By.TAG_NAME,'a')
        news_links.append(link.get_attribute('href'))
browser.quit()

'''In the news links we are extracting there are chances for duplicate links since many articles are referenced in other pages also.
We need to remove those duplicates'''
unique_elements_set1 = set(news_links) #Convert the list of url to set to eliminate duplicates
news_links_list = list(unique_elements_set1) #convert the set back to list

def run_scrapy_spider():
    class StarSpider(scrapy.Spider):
        name = "star_spider"
        custom_settings = {
            "FEEDS": {"StarArticles"+ "_" + str(cd)+ ".csv":{"format":"csv"}},
            }
    
        def start_requests(self):
            # Start crawling each URL
            for url in news_links_list:
                yield scrapy.Request(url=url, callback=self.parse)

        def parse(self, response):
            
            #Extract title and content of each webpage using css
            title = response.css(".story-pg h1::text").getall()
            #Extract the content and title using xpath
            content = response.xpath("//div[@id='story-body']//p/text()").getall()
        
        
            self.log(f'Title: {title}')# for logging the data to scrapy
            #Return the data in the form of dictionary
            yield {
                'Title': title,
                'Content': content
                }


    process = CrawlerProcess()
    process.crawl(StarSpider)
    process.start()
    

# Function to compare yesterday's articles with today's articles
def compare_articles():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    
    y = yesterday.strftime("%d%m%Y")
    
    yesterdays_file = 'StarArticles_{}.csv'.format(y)
    todays_file = 'StarArticles_{}.csv'.format(time.strftime("%d%m%Y"))

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
        result.to_csv("StarArticles{}.csv".format(time.strftime("%d%m%Y")), index=False)
    else:
        todays_articles = pd.read_csv(todays_file)
        todays_articles.to_csv("StarArticles{}.csv".format(time.strftime("%d%m%Y")), index=False)
        return

    
# Run the Scrapy spider and extract articles
run_scrapy_spider()

# Compare yesterday's articles with today's articles
compare_articles()


        
