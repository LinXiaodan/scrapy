# -*- coding: utf-8 -*-
import scrapy


class QqmusicSpider(scrapy.Spider):
    name = 'qqMusic'
    start_urls = ['http://dl.stream.qqmusic.qq.com/C400000eskGX0ijIFi.m4a?vkey=322C89ECA38009F0AB6BB504847E8E2FC365287BA015567C9DF0F97824653AAD33E2C3BD472E96DCDF841292E8DD1AF3D13C0784F0A2D04C&guid=3181863611&uin=0&fromtag=66']
    music_name = 'aiqingfeichai'

    def parse(self, response):
        with open('/home/linxiaodan/music/{}.m4a'.format(self.music_name), 'wb') as f:
            f.write(response.body)
