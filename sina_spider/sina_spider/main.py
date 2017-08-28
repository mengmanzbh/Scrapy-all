# -*- coding: utf-8 -*-
import time
import os

while True:
    os.system("scrapy crawl sina")
    os.system("scrapy crawl east")
    time.sleep(60)  #每隔一天运行一次 24*60*60=86400s
