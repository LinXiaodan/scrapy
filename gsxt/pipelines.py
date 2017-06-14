# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import md5
import os


class GsxtPipeline(object):
    def __init__(self):
        self.file = codecs.open('content.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        if 'zhizhao' not in item:
            line = json.dumps(dict(item), ensure_ascii=False)+"\n"
            self.file.write(line)
            return item
        else:
            d = dict(item)
            cname = d['cname']
            zhizhao = d['zhizhao']
            filename = md5.new(cname.encode('utf-8')).hexdigest()
            if not os.path.exists('details'):
                os.mkdir('details')
            with codecs.open('details/'+filename+'.txt', 'w', 'utf-8') as f:
                f.write(zhizhao)
            print 'save detail in file success'

    def spider_closed(self, spider):
        self.file.close()
