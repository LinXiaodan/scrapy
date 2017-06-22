# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
import time
import yaml
from copy import deepcopy
from urllib import urlencode

import scrapy
from bs4 import BeautifulSoup
from scrapy import FormRequest, Request

import slide_offline
from gsxt.items import GsxtItem


class QH_gsxtSpider(scrapy.Spider):
    name = 'QH_gsxt'

    host_url = 'http://qh.gsxt.gov.cn/'
    base_url = 'http://qh.gsxt.gov.cn/index.jspx'
    validate_register_url = 'http://qh.gsxt.gov.cn/registerValidate.jspx?t={}'
    validate_sec_url = 'http://qh.gsxt.gov.cn/validateSecond.jspx'
    detail_url = 'http://qh.gsxt.gov.cn/company/detail.jspx?id={}&jyzk={}'
    detail_basic_url = 'http://qh.gsxt.gov.cn/company/basic.jspx?id={}'  # 基本信息
    detail_JCXX_url = 'http://qh.gsxt.gov.cn/business/JCXX.jspx?id={}&date={}'  # 基础信息
    detail_XZXK_url = 'http://qh.gsxt.gov.cn/business/XZXK.jspx?id={}'    # 行政许可信息

    default_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Referer': base_url
    }

    spider_settings = yaml.load(open('./spider_settings/{}.yml'.format(name), 'r')) \
        if os.path.exists('./spider_settings/{}.yml'.format(name)) else {}

    custom_settings = {
        'DOWNLOAD_DELAY': spider_settings.get('DOWNLOAD_DELAY', 0.05),
        'CONCURRENT_REQUESTS_PER_DOMAIN': spider_settings.get('CONCURRENT_REQUESTS_PER_DOMAIN', 10),
        'CONCURRENT_REQUESTS': spider_settings.get('CONCURRENT_REQUESTS', 10),
        'RETRY_TIMES': spider_settings.get('RETRY_TIMES', 0),
        'PROXY_POOL_HOST': spider_settings.get('PROXY_POOL_HOST', '10.116.97.95'),  # 代理池主机地址
        'GLOBAL_SIZE': spider_settings.get('GLOBAL_SIZE', 50),
        'GLOBAL_STABILITY': spider_settings.get('GLOBAL_STABILITY', 100),  # 代理稳定性
    }

    max_retry_time = 10
    retry_time = 0

    @staticmethod
    def get_time():
        return str(int(time.time() * 1000))

    @staticmethod
    def get_GMT_time():
        GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT 0800 (CST)'
        return datetime.datetime.utcnow().strftime(GMT_FORMAT)

    def start_requests(self):
        self.logger.info('start_requests')

        file_path = 'information/'+self.name
        with open(file_path) as f:
            for line in f.readlines():
                name = line.strip()
                meta = {
                    'name': name,
                    'autoproxy': True,
                }
                # 请求获取challenge,gt
                yield Request(
                    url=self.validate_register_url.format(self.get_time()),
                    dont_filter=True,
                    meta=meta,
                    callback=self.parse,
                    headers=self.default_headers,
                    errback=self.retry,
                    priority=5,
                )

    def parse(self, response):
        meta = deepcopy(response.meta)
        self.logger.info('parse name:' + meta['name'])
        try:
            data = json.loads(response.body)
            if data['success'] == 0:
                challenge = data['challenge']
                validate = slide_offline.ajax(challenge)
                seccode = validate + '|jordan'

                formdata = {
                    'searchText': meta['name'],
                    'geetest_challenge': challenge,
                    'geetest_validate': validate,
                    'geetest_seccode': seccode
                }

                meta.update({
                    'formdata': formdata
                })

                yield FormRequest(
                    method='POST',
                    formdata=formdata,
                    meta=meta,
                    url=self.validate_sec_url,
                    callback=self.validate_sec,
                    dont_filter=True,
                    headers=self.default_headers,
                    priority=10,
                    errback=self.retry,
                )
            else:
                self.logger.info('go to man_retry in parse, name:' + meta['name'])
                yield self.man_retry(response)
        except Exception as e:
            self.logger.exception(e)
            yield self.man_retry(response)

    def validate_sec(self, response):
        meta = deepcopy(response.meta)
        self.logger.info('validate_sec name:' + meta['name'])
        try:
            data = json.loads(response.body)

            if data['success']:
                yield Request(
                    url=self.host_url + data['obj'] + '&' + urlencode({
                        'searchType': 1,
                        'entName': meta['name']
                    }),
                    meta=meta,
                    callback=self.parse_list,
                    errback=self.retry,
                    dont_filter=True,
                    priority=15,
                    headers=self.default_headers,
                )

            else:
                print 'fail in second validate'
                self.logger.info('validate_sec failed')
                yield self.man_retry(response)

        except Exception as e:
            self.logger.exception(e)
            yield self.man_retry(response)

    def parse_list(self, response):
        meta = deepcopy(response.meta)
        self.logger.info('get the list, name:'+meta['name'])
        try:
            bs = BeautifulSoup(response.body, "lxml")
            if u'正常' in bs.select('title')[0].get_text():
                bs1 = bs.select('div.gggscpnamebox')

                if len(bs1) == 0:
                    self.logger.info('no found name:'+meta['name'])

                else:
                    match = re.search('jyzk="(.*)"', response.body)
                    jyzk = match.group(1)

                    for a in bs1:
                        list_name = a.select('p.gggscpnametitle span.qiyeEntName')[0].get_text().strip()
                        print 'list_name', list_name
                        id = a.get('data-label')
                        print 'id', id
                        meta.update({
                            'list_name': list_name.encode('utf-8')
                        })
                        headers = self.default_headers
                        headers.update({
                            'Referer': self.detail_url.format(id, jyzk)
                        })

                        # 基本信息
                        meta.update({
                            'info': 'basic'
                        })
                        yield Request(
                            meta=meta,
                            url=self.detail_basic_url.format(id),
                            callback=self.save_content,
                            errback=self.retry,
                            priority=20,
                            headers=headers,
                        )

                        # 基础信息
                        meta.update({
                            'info': 'JCXX'
                        })
                        yield Request(
                            url=self.detail_JCXX_url.format(id, self.get_GMT_time()),
                            callback=self.save_content,
                            meta=meta,
                            errback=self.retry,
                            priority=20,
                            headers=headers
                        )

                        # 行政许可信息
                        meta.update({
                            'info': 'XZXK'
                        })
                        yield Request(
                            url=self.detail_XZXK_url.format(id),
                            callback=self.save_content,
                            meta=meta,
                            errback=self.retry,
                            priority=20,
                            headers=headers
                        )

            else:
                self.logger.info('list error name:'+meta['name'])
                yield self.man_retry(response)

        except Exception as e:
            self.logger.exception(e)
            yield self.man_retry(response)

    def save_content(self, response):
        meta = response.meta

        if meta['info'] == 'basic':
            if 'company_detail_basic.html' in response.body:
                self.logger.info('get content basic, name:{} list_name:{}'.format(meta['name'], meta['list_name']))
            else:
                self.logger.info('not get basic, name:{} list_name:{}'.format(meta['name'], meta['list_name']))
                print response.body
                yield self.man_retry(response)
                return

        if meta['info'] == 'JCXX':
            if '营业执照信息' in response.body:
                self.logger.info('get content JCXX, name:{} list_name:{}'.format(meta['name'], meta['list_name']))
            else:
                self.logger.info('not get JCXX, name:{} list_name:{}'.format(meta['name'], meta['list_name']))
                print response.body
                yield self.man_retry(response)
                return

        if meta['info'] == 'XZXK':
            if '行政许可信息' in response.body:
                self.logger.info(
                    'get content XZXK, name:{} list_name:{}'.format(meta['name'], meta['list_name']))
            else:
                self.logger.info('not get XZXK, name:{} list_name:{}'.format(meta['name'], meta['list_name']))
                print response.body
                yield self.man_retry(response)
                return

        result = GsxtItem.get_result_from_response(response)
        result['content'] = '%s %s\n%s' % (meta['name'], meta['list_name'], response.body)
        yield result

    # 重新开始
    def man_retry(self, response):
        meta = deepcopy(response.meta)
        retry_time_count = meta.get('retry_time_count', 0)
        max_retry_time = self.max_retry_time

        self.retry_time = self.retry_time + 1
        self.logger.info('total retry time:{}'.format(self.retry_time))

        if retry_time_count < max_retry_time:
            meta.update({
                'retry_time_count': retry_time_count + 1,
                'change_proxy': True,
            })

            self.logger.info('man_retry name:{} retry_time_count:{}'.
                             format(meta.get('name', ''), meta.get('retry_time_count', '')))

            return Request(
                url=self.validate_register_url.format(self.get_time()),
                dont_filter=True,
                meta=meta,
                callback=self.parse,
                headers=self.default_headers,
                errback=self.retry,
                priority=5,
            )
        else:
            self.logger.info('failed! man_retry name:' + meta.get('name', ''))

    def retry(self, failure):
        self.logger.error(repr(failure))
        request = failure.request
        meta = deepcopy(request.meta)
        retry_time_count = meta.get('retry_time_count', 0)
        max_retry_time = self.max_retry_time

        self.retry_time = self.retry_time + 1
        self.logger.info('total retry time:{}'.format(self.retry_time))

        if retry_time_count < max_retry_time:
            meta.update({
                'retry_time_count': retry_time_count + 1,
                'change_proxy': True,
            })

            self.logger.info('retry name:{} retry_time_count:{}'.
                             format(meta.get('name', ''), meta.get('retry_time_count', '')))
            # 直接回到开头开始
            return Request(
                url=self.validate_register_url.format(self.get_time()),
                dont_filter=True,
                meta=meta,
                callback=self.parse,
                headers=self.default_headers,
                errback=self.retry,
                priority=5,
            )
        else:
            self.logger.info('failed! retry name:' + meta.get('name', ''))