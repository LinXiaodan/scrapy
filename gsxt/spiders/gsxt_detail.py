# -*- coding: utf-8 -*-
import scrapy
import json
import time
from copy import deepcopy
import re
from urllib import urlencode
from scrapy import FormRequest, Request
import random
import slide_method
from pyquery import PyQuery
from gsxt.items import GsxtItem
from scrapy.utils.log import configure_logging


class GsxtDetailSpider(scrapy.Spider):
    name = "gsxt-detail"
    start_urls = ['http://www.gsxt.gov.cn/SearchItemCaptcha?']

    searchItem_url = 'http://www.gsxt.gov.cn/SearchItemCaptcha?'
    gettype_url = 'http://api.geetest.com/gettype.php?gt={}&callback={}'
    slideGet_url = 'http://api.geetest.com/get.php?'
    slideCheck_url = 'http://api.geetest.com/ajax.php?gt={}&challenge={}&userresponse={}&passtime={}&imgload={}&a={}&callback={}'
    teddy_url = 'http://119.23.121.156:4067/api/model/slide'
    searchcontent_url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
    detail_url = 'http://www.gsxt.gov.cn'
    # default_headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    #     'Accept-Encoding': 'gzip, deflate, sdch',
    #     'Accept-Language': 'zh-CN,zh;q=0.8',
    # }

    PROXY_POOL = '120.25.242.242:10650/getProxy?size=10&stability=100'

    @staticmethod
    def get_time():
        return str(int(time.time() * 1000))

    def return_begin(self,response):
        print 'retry!'
        self.logger.info("retry!")
        yield Request(
            method='GET',
            url=self.searchItem_url,
            errback=self.return_begin,
            callback=self.parse,
            dont_filter=True,
        )

    def parse(self, response):
        print 'parse now'
        data = json.loads(response.body)
        success = data['success']
        if success == 0:
            print 'fail in start_url'
            yield self.return_begin(response).next()
        else:
            gt = data['gt']
            # recent_headers = deepcopy(self.default_headers)
            # recent_headers.update({
            #     'Accept': '*/*',
            #     'Referer': 'http://www.gsxt.gov.cn/index.html',
            # })
            yield Request(
                method='GET',
                meta={
                    'gt':gt,
                    'challenge': data['challenge'],
                },
                url=self.gettype_url.format(gt, 'geetest_'+self.get_time()),
                callback=self.parse_gettype,
                dont_filter=True,
                # headers=recent_headers
            )
        pass

    def parse_gettype(self, response):
        try:
            print 'parse_gettype now'
            match = re.match('^geetest_\d+\((.*)\)$', response.body)
            data = json.loads(match.group(1))
            gt = response.meta['gt']
            challenge = response.meta['challenge']
            status = data['status']
            if status == 'success':
                yield Request(
                    method='GET',
                    meta=response.meta,
                    url=self.slideGet_url+urlencode({
                        'gt': gt,
                        'challenge': challenge,
                        'product': 'popup',
                        'offline': 'false',
                        'type': 'slide',
                        'path': '/static/js/geetest.5.10.10.js',
                        'callback': 'geetest_'+self.get_time(),
                    }),
                    callback=self.parse_slideget,
                    dont_filter=True,
                )
            else:
                print 'Get type error!'
        except Exception as e:
            print 'error parse_gettype'
            return
        pass

    def parse_slideget(self,response):
        #获取验证码，请求teddy
        try:
            match = re.match('^geetest_\d+\((.*)\)$', response.body)
            data = json.loads(match.group(1))
            host = 'http://'+data['static_servers'][0]
            fullbg = host+data['fullbg']
            bg = host+data['bg']
            slice = host+data['slice']
            xpos = data['xpos']
            ypos = data['ypos']
            gt = data['gt']
            challenge = data['challenge']
            start_time = self.get_time()
            meta = deepcopy(response.meta)
            meta.update({
                'gt': gt,
                'challenge': challenge,
                'start_time': start_time,
            })
            yield FormRequest(
                method='POST',
                meta=meta,
                url = self.teddy_url,
                formdata={
                    'originUrl': fullbg,
                    'shadowUrl': bg,
                    'chunkUrl': slice,
                    'left': str(xpos),
                    'top': str(ypos)
                },
                callback=self.parse_teddy,
                dont_filter=True,
            )
        except Exception as e:
            print 'error parse_slideget'
            return
        pass

    def parse_teddy(self, response):
        #teddy解码结果验证发送
        print 'parse_teddy now'
        try:
            data = json.loads(response.body)
            stat = data['stat']
            target_pos = data['target_pos']
            trail = data['trail']
            gt = response.meta['gt']
            challenge = response.meta['challenge']
            userresponse = slide_method.get_userresponse(target_pos, challenge)
            passtime = trail[-1][-1]
            imgload = random.randint(10, 100)
            a = slide_method.get_a(trail)
            start_time = response.meta['start_time']
            now_time = self.get_time()
            sleep_time = float(int(passtime)-int(now_time)+int(start_time))/1000
            if sleep_time > 0:
                print 'sleep for :'+str(sleep_time)+'s'
                time.sleep(sleep_time)
            callback = 'geetest_'+self.get_time()

            if stat == 1:
                yield Request(
                    method='GET',
                    meta=response.meta,
                    url=self.slideCheck_url.format(
                        gt,
                        challenge,
                        userresponse,
                        passtime,
                        imgload,
                        a,
                        callback,
                    ),
                    callback=self.parse_getsearch,
                    dont_filter=True,
                )
            else:
                print 'get slide result error'
        except Exception as e:
            print 'error parse_teddy'
            return
        pass

    def parse_getsearch(self, response):
        #得到validate,跳转到搜素得到的页面
        try:
            print 'parse_getsearch now!'
            match = re.match('^geetest_\d+\((.*)\)$', response.body)
            data = json.loads(match.group(1))
            success = data['success']
            if success == 1:
                validate = data['validate']
                seccode = validate + '|jordan'
                meta = deepcopy(response.meta)
                formdata = {
                    'tab': 'ent_tab',
                    'searchword': '中心',
                    'geetest_challenge': meta['challenge'],
                    'geetest_validate': validate,
                    'geetest_seccode': seccode,
                }
                yield FormRequest(
                    method='POST',
                    meta=meta,
                    url=self.searchcontent_url,
                    formdata=formdata,
                    callback=self.parse_getcontent,
                    errback=self.return_begin,
                    dont_filter=True,
                )
            else:
                print 'failed to getcontent! success = 0'
                message = data['message']
                print 'message : '+message
                yield self.return_begin(response).next()

        except Exception as e:
            print 'error parse_getsearch'
            return

    def parse_getcontent(self, response):
        #解析搜索界面，得到详情页地址，跳转
        print 'getcontent now'
        try:
            p = PyQuery(response.body)
            meta = deepcopy(response.meta)
            if p('div.main-layout a.search_list_item'):
                '该搜索名能够得到公司信息'
                print '成功搜索到公司'
                #跳转到该公司对应的页面获取详情
                for i in p('div.main-layout a.search_list_item').items():
                    href = self.detail_url+i.attr('href')
                    a = PyQuery(i)
                    meta.update({'company_name': ''.join(a('h1').text().split())})
                    yield Request(
                        method='GET',
                        meta=meta,
                        url=href,
                        callback=self.parse_detail,
                        dont_filter=True,
                    )

                #保存公司简略信息
                for content in p('div.main-layout a.search_list_item').items():
                    item = GsxtItem()
                    a = PyQuery(content)
                    item['cname'] = ''.join(a('h1').text().split())
                    item['status'] = a('div.wrap-corpStatus span').text()
                    item['ccode'] = a('div.div-map2 span').text()
                    item['lawuser'] = a('div.div-user2 span').text()
                    item['etime'] = a('div.div-info-circle2 span').text()
                    yield item
            else:
                print '没有符合的公司'

        except Exception as e:
            self.logger.exception(e)
            # print 'error parse_getcontent'

    def parse_detail(self, response):
        print 'parse_detail now'
        p = PyQuery(response.body)

        content = PyQuery(p('div.details'))
        s = ''
        for a in content('dl').items():
            b = PyQuery(a)
            s = s+b('dt').text()+b('dd').text()+'\n'
        item = GsxtItem()
        item['zhizhao'] = s
        item['cname'] = response.meta['company_name']
        yield item
        pass

