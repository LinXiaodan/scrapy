#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2017 Tungee, Inc
# use proxy

import base64
import logging
import random
import re
import time

import requests

logger = logging.getLogger()


class GreenPoolProxyDownloaderMiddleware(object):
    """Use proxy for exact cookiejar"""

    def __init__(self, settings):
        self.host = settings.get('PROXY_POOL_HOST', '10.116.97.95')  # 代理池内网地址
        self.port = settings.get('PROXY_POOL_PORT', '10650')  # 代理池端口号
        self.size = settings.getint('GLOBAL_SIZE', 100)  # 每次获取代理的数量
        self.stability = settings.getint('GLOBAL_STABILITY', 90)  # 稳定性(若没有特别指定,将全部使用稳定代理).默认90%的稳定代理
        self.proxy_pool_url = [
            'http://{host}:{port}/getProxy?size={size}&stability={stability}'.format(
                host=self.host,
                port=self.port,
                size=self.size,
                stability=self.stability
            )
        ]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    proxies = []
    fullset = []

    def _get_proxies_sync(self):
        self.fullset = []
        for api in self.proxy_pool_url:
            try:
                res = requests.get(api, timeout=30)
                if res.status_code < 300:
                    data = res.json()
                    if 'proxyes' in data:
                        logger.info(msg='Request proxy pool: {}'.format(api))  # noqa
                        logger.info(msg='Proxyes are {}'.format(data))
                        for ip in data['proxyes']:
                            if 'user' in ip:
                                self.proxies.append('http://{}:{}@{}:{}'
                                                    .format(ip['user'], ip['password'], ip['host'], ip['port']))
                                self.fullset.append('http://{}:{}@{}:{}'
                                                    .format(ip['user'], ip['password'], ip['host'], ip['port']))
                            else:
                                self.proxies.append('http://{}:{}'.format(ip['host'], ip['port']))
                                self.fullset.append('http://{}:{}'.format(ip['host'], ip['port']))
            except Exception as e:
                logger.exception(e)

    def get_random_proxy(self):
        if len(self.proxies) == 0:
            self._get_proxies_sync()

        if len(self.proxies) == 0:
            return None
        else:
            index = random.randint(0, len(self.proxies) - 1)
            return self.proxies.pop(index)

    def process_response(self, request, response, spider):
        start_time = request.meta.get('_start_time', time.time())
        logger.debug('url: %s time: %f' % (request.url, time.time() - start_time))
        if 'change_proxy' in request.meta:
            del request.meta['change_proxy']

        if '_proxy' in request.meta:
            request.meta['proxy'] = request.meta['_proxy']
            del request.meta['_proxy']
        return response

    def process_request(self, request, spider):
        request.meta.update({
            '_start_time': time.time()
        })

        if 'autoproxy' in request.meta and request.meta['autoproxy'] is True:

            add_proxy_meta = True
            proxy = request.meta['proxy'] if 'proxy' in request.meta else None

            if re.search('api/names/province/', request.url) \
                or re.search('api/model/', request.url) \
                or re.search('api/common/', request.url):  # noqa
                add_proxy_meta = False
            elif ('change_proxy' in request.meta and request.meta['change_proxy']) or proxy is None or proxy not in self.fullset:  # noqa
                logger.debug('change proxy')
                proxy = self.get_random_proxy()

            if add_proxy_meta:
                if proxy:
                    logger.debug('proxy:%s cookiejar:%s' % (proxy, request.meta.get('cookiejar', None)))
                    request.meta['proxy'] = proxy
                    match_auth = re.match('^.*://([^:/]*:[^:/]*)@[^/]*$', proxy)
                    if match_auth:
                        request.headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(match_auth.group(1))
                elif 'proxy' in request.meta:
                    logger.debug('no valid proxy')
                    del request.meta['proxy']
            else:
                if 'proxy' in request.meta:
                    request.meta['_proxy'] = proxy
                    del request.meta['proxy']
