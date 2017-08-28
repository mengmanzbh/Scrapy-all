# -*- coding: utf-8 -*-
import scrapy
import csv
import json
from pymongo import MongoClient
import pika

class JdSpider(scrapy.Spider):
    name = "neep"
   # allowed_domains = ["jd.com"]
    start_urls = (
        'http://www.neeq.com.cn/disclosure/announcement.html',
    )

    def parse(self, response):
        # time = response.css('td.tl td::text').extract_first()
        # print(time)
        # base = 'http://www.neeq.com.cn'
        # url = response.css('td.tl a::attr(href)').extract_first()
        # url = base+url
        # content = response.css('td.tl a em::text').extract()
        # print(content)
        # for index in range(len(time)):
        # 	print('-----------------------------------------------------')
        # 	print(time[index])
        # 	print(content[index])
        
        # time = response.xpath('//*[@id="companyTable"]/tr[2]/td[3]/text()').extract_first()
        # content = response.xpath('//*[@id="companyTable"]/tr[3]/td[2]/a/em/text()').extract_first()
        # url = response.xpath('//*[@id="companyTable"]/tr[3]/td[2]/a/@href').extract_first()
        # base = 'http://www.neeq.com.cn'
        # url = base+url
        # print(content)
        
        for x in range(20):
        	time = response.xpath('//*[@id="companyTable"]/tr[$cnt]/td[3]/text()', cnt=x+1).extract_first()
        	content = response.xpath('//*[@id="companyTable"]/tr[$num]/td[2]/a/em/text()',num = x + 1).extract_first()
        	url = response.xpath('//*[@id="companyTable"]/tr[$cnt]/td[2]/a/@href', cnt=x+1).extract_first()
        	base = 'http://www.neeq.com.cn'
        	url = base+url
        	print('-----------------------------------')
        	print(time)
        	print(content)
        	print(url)
        	client = MongoClient()
        	client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
        	db = client.admin
        	count = db.sina.find({"content":content}).count()
        	self.logger.info(count)
        	if count == 0:
        		print('data is not exist!')
        		totalCount = db.sina.find().count()
        		db.sina.insert({"source":"全国中小企业股份转让系统","time": time,"url": url, "content": content,"count":totalCount+1})
        	else:
        		print('data is exist!')
        	pass
