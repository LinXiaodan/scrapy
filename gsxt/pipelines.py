# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import md5
import os
import re

result_output_path = 'result'


class GsxtPipeline(object):
    def __init__(self):
        pass
        # self.file = codecs.open('content.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        # if 'zhizhao' not in item:
        #     line = json.dumps(dict(item), ensure_ascii=False)+"\n"
        #     self.file.write(line)
        #     return item
        # else:
        #     d = dict(item)
        #     cname = d['cname']
        #     zhizhao = d['zhizhao']
        #     filename = md5.new(cname.encode('utf-8')).hexdigest()
        #     if not os.path.exists('details'):
        #         os.mkdir('details')
        #     with codecs.open('details/'+filename+'.txt', 'w', 'utf-8') as f:
        #         f.write(zhizhao)
        #     print 'save detail in file success'
        # url = item['url']
        # match = re.match('^http|https://(.*).*\.$')
        content = item['content']
        if re.match('^https?://[^/]+$', item['url']):
            item['url'] += '/'
        match = re.match('https?://([^\?]*/)([^/\?]*)(\?.*)?$', item['url'])
        base_dir = os.path.join(result_output_path, spider.name)
        file_dir = os.path.join(base_dir, match.group(1))

        # replace illegal path char
        file_name = match.group(2)
        query_string = match.group(3)

        # if path not given, use url(without protocal) as path
        if 'path' not in item:
            item['path'] = os.path.join(match.group(1), file_name)

            # for POST and PUT formdata, add md5 hash to path
            if 'formdata' in item:
                if query_string:
                    item['path'] = os.path.join(
                        item['path'], md5.new(
                            query_string + item['formdata']).hexdigest())
                else:
                    item['path'] = os.path.join(
                        item['path'], md5.new(item['formdata']).hexdigest())
            elif query_string:
                item['path'] = os.path.join(
                    item['path'], md5.new(query_string).hexdigest())

        # for '/' ended path, add index.html file
        if re.match('.*/$', item['path']):
            item['path'] += 'index.html'

        file_path = os.path.join(base_dir, item['path'])
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        if not os.path.exists(file_dir.encode('utf8')):
            os.makedirs(file_dir.encode('utf8'))

        if item.get('append', False):
            output = open(file_path.encode('utf8'), 'a+')
        else:
            output = open(file_path.encode('utf8'), 'w+')

        if isinstance(content, unicode):
            output.write(content.encode('utf8'))
        else:
            output.write(content)
        output.close()

        return item

    def spider_closed(self, spider):
        pass
        # self.file.close()
