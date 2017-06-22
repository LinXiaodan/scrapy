# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GsxtItem(scrapy.Item):
    # define the fields for your item here like:
    content = scrapy.Field()
    url = scrapy.Field()
    path = scrapy.Field()

    @classmethod
    def get_result_from_response(cls, response):
        result = GsxtItem(
            content=response.body,
            url=response.url
        )
        return result