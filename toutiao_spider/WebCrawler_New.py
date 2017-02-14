# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 10:08:31 2016

@author: gong

@description: 这是一个下载网页内容的程序
"""
import traceback
import requests
          
class WebCrawler(object):
    def __init__(self):
        self.headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding":"gzip,deflate,compress",
            "Accept-Language":"zh-CN,zh;q=0.8,ja;q=0.6,en;q=0.4,zh-TW;q=0.2",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
        }
        
    def get_htmldata(self,url,post_data=None,retries=3):
        '''返回HTML的数据'''
        session = requests.Session()
        session.headers.update(self.headers)
        #设置http请求头
        request_fun = None
        if post_data:
            method = 'post'
        else:
            method = 'get'
        
        if method == 'post':
            request_fun = session.post
        else:
            request_fun = session.get
        while retries > 0:
            retries -= 1
            try:
                r = request_fun(url,data=post_data)
                return r.content
            except Exception as err:
                if retries == 0:
                    traceback.print_exc()
                    raise err
        
    def get_data(self,url,encode='utf8',gzip = False,post_data=None,retries=3):
        '''返回HTML的数据'''
        session = requests.Session()
        session.headers.update(self.headers)
        #设置http请求头
        request_fun = None
        if post_data:
            method = 'post'
        else:
            method = 'get'
        method = method.lower()
        if method == 'post':
            request_fun = session.post
        else:
            request_fun = session.get
        while retries > 0:
            retries -= 1
            try:
                r = request_fun(url,data=post_data)
                r.encoding = encode
                return r.text
            except Exception as err:
                if retries == 0:
                    traceback.print_exc()
                    raise err
