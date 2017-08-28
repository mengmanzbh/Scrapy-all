# -*- coding: utf-8 -*-
import scrapy
import csv
import json
from pymongo import MongoClient
# import pika

class EastSpider(scrapy.Spider):
    name = 'east'
    allowed_domains = ['kuaixun.eastmoney.com']
    start_urls = ['http://kuaixun.eastmoney.com/']

    def parse(self, response):
        time = response.css('span.time::text').extract_first()
        content = response.css('a.media-title::text').extract_first()
        self.logger.info(time)
        self.logger.info(content)
        client = MongoClient()
        client = MongoClient("mongodb://admin:c665f7a5@118.190.117.167:27017")
        # client = MongoClient("mongodb://root:988920Zbh@s-bp1a0e773f546404.mongodb.rds.aliyuncs.com:3717")
        db = client.admin
        count = db.sina.find({"content":content}).count()
        self.logger.info(count)
        if count == 0:
          print('data is not exist!')
          totalCount = db.sina.find().count()
          db.sina.insert({"source":"东方财富网","time": time, "content": content,"count":totalCount+1})
          # print("---------------noticeDjangoUpdate--------------")
          # credentials = pika.PlainCredentials('admin', 'admin')
          # #链接rabbit服务器（localhost是本机，如果是其他服务器请修改为ip地址）
          # connection = pika.BlockingConnection(pika.ConnectionParameters('120.27.6.116',5672,'/',credentials))
          # channel = connection.channel()
          # # 定义交换机，exchange表示交换机名称，type表示类型
          # channel.exchange_declare(exchange='logs_fanout',
          #                          type='fanout')
          # message = 'Hello Python'
          # # 将消息发送到交换机
          # channel.basic_publish(exchange='logs_fanout',  # 指定exchange
          #                       routing_key='',  # fanout下不需要配置，配置了也不会生效
          #                       body=message)
          # print(" [x] Sent %r" % message)
          # connection.close()          
        else:
          print('data is exist!')
        pass
