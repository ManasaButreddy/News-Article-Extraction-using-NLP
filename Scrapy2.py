#import subprocess
from datetime import date, timedelta
import pandas as pd
import time
import scrapy
from scrapy.crawler import CrawlerProcess
import os


current_date = date.today()
current_date
cd = current_date.strftime("%d%m%Y")

# Function to run Scrapy spider and extract articles
def run_scrapy_spider():
    class MalaySpider(scrapy.Spider):
        name = 'malay_spider'
        custom_settings = {
            "FEEDS": {"MMArticles"+ "_" + str(cd)+ ".csv":{"format":"csv"}},
        }
        start_urls = ['https://www.malaymail.com/']

        def parse(self, response):
            # Fetch all links
            links = response.xpath("//h2[@class='article-title']/a/@href")
            for link in links:
                yield scrapy.Request(url=link.get(), callback=self.parse_website)

        def parse_website(self, response):
            # Fetch article details
            title = response.xpath("//h1[@class='article-title']/text()").get()
            caption = response.xpath("//div[@class='image-caption']/text()").get()
            date = response.xpath("//div[@class='article-date']/text()").get()
            body = response.xpath("//div[@class='article-body']/p/text()")
            href = response.request.url

            content = ''
            for text in body:
                content += text.get()

            article_data = {
                'Headline': title,
                'Caption': caption,
                'Published date': date,
                'Content': content,
                'Link': href
            }

            yield article_data

    process = CrawlerProcess()

    process.crawl(MalaySpider)
    process.start()

# Function to compare yesterday's articles with today's articles
def compare_articles():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    
    y = yesterday.strftime("%d%m%Y")
    
    yesterdays_file = 'MMArticles_{}.csv'.format(y)
    todays_file = 'MMArticles_{}.csv'.format(time.strftime("%d%m%Y"))

#check if files with yesterdays date exists    
    if os.path.exists(yesterdays_file):
  
        yesterdays_articles = pd.read_csv(yesterdays_file)
        todays_articles = pd.read_csv(todays_file)
        
        df_non_match = pd.merge(todays_articles, yesterdays_articles, how='outer', indicator=True, on='Published date')
        df_non_match = df_non_match[(df_non_match._merge == 'left_only')]

        result = df_non_match.iloc[:, 0:5]
        result = result.drop_duplicates()
        result.rename(columns={'Headline_x' : 'Headline',
                           'Caption_x': 'Caption',
                           'Content_x': 'Content',
                           'Link_x': 'Link'
                           }, inplace=True)

        result.to_csv("MMArticles{}.csv".format(time.strftime("%d%m%Y")), index=False)
    else:
        todays_articles = pd.read_csv(todays_file)
        todays_articles.to_csv("MMArticles{}.csv".format(time.strftime("%d%m%Y")), index=False)
        return
        
        


# Run the Scrapy spider and extract articles
run_scrapy_spider()

# Compare yesterday's articles with today's articles
compare_articles()

