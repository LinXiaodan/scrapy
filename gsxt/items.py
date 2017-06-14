# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GsxtItem(scrapy.Item):
    # define the fields for your item here like:
    cname = scrapy.Field()#公司名
    status = scrapy.Field()#状态
    ccode = scrapy.Field()#统一社会信用代码
    lawuser = scrapy.Field()#法定代表人
    etime = scrapy.Field()#成立日期
    zhizhao = scrapy.Field()#营业执照信息

    pass

class testItem(scrapy.Item):
    a = scrapy.Field()