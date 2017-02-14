# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 10:08:31 2016

@author: gong

@description: 这是一个下载网页内容的程序
"""
import zlib
import StringIO
import gzip
import urllib2,urllib,cookielib
import urlparse
from urllib2 import Request,HTTPError
from urllib2 import build_opener
from urllib2 import HTTPRedirectHandler
from urllib2 import HTTPCookieProcessor
import traceback
import requests

#解决自动重定向问题
class RedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        m = req.get_method()
        if (not (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
        or code in (301, 302, 303, 307) and m == "POST")):
            raise HTTPError(req.full_url, code, msg, headers, fp)
        newurl = newurl.replace(' ', '%20')
        CONTENT_HEADERS = ("content-length", "content-type")
        newheaders = dict((k, v) for k, v in req.headers.items()
            if k.lower() not in CONTENT_HEADERS)
        return Request(newurl,headers=newheaders,
                       origin_req_host=req.origin_req_host,unverifiable=True)

class WebCrawler(object):
    def __init__(self,timeout=10):
        self.mycookie = ''
        self.headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            #"Accept-Encoding":"",
            "Accept-Language":"zh-CN,zh;q=0.8,ja;q=0.6,en;q=0.4,zh-TW;q=0.2",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
            "Cookie":""
        }
        urllib2.socket.setdefaulttimeout(timeout)
        self.cookies = cookielib.CookieJar()
        self.opener = build_opener(HTTPRedirectHandler,HTTPCookieProcessor(self.cookies))
        #self.opener = build_opener(HTTPRedirectHandler)
        urllib2.install_opener(self.opener)
        self.Referer = None
        
    
    def gen_postdata(self,data_dict):
        '''生成post data'''
        return urllib.urlencode(data_dict).encode('utf-8')
    
    def get_cookies(self):
        '''获得cookies'''
        cookies_str = ''
        for cookie in self.cookies:
            cookies_str += cookie.name+'='+cookie.value+';'
        return cookies_str
        
    #解压gzip  
    def __gzdecode__(self,data) :
        compressedstream = StringIO.StringIO(data)
        try:
            gziper = gzip.GzipFile(fileobj=compressedstream) 
            decode_data = gziper.read()   # 读取解压缩后数据   
            return decode_data 
        except:
            return zlib.decompress(data, zlib.MAX_WBITS|16)
       
        
    def get_data(self,url,encode='utf8',gzip = False,post_data=None,retries=3):
        '''返回数据，包括解压gzip'''
        if gzip:
            self.headers['Accept-Encoding'] = "gzip,deflate"
        else:
            self.headers['Accept-Encoding'] = ""

        data = self.get_htmldata(url,post_data,retries).decode(encode,'ignore')
        
        if gzip:
            try:
                return self.__gzdecode__(data)
            except:
                result = self.__get_data_after_error__(url,encode)
                return result
        return data
    
    def __get_data_after_error__(self,url,encoding):
        """
        当出现错误的时候就调用这个函数来下载数据
        """
        
        r = requests.get(url,self.headers)
        r.encoding = encoding
        return r.text
        
    def get_htmldata(self,url,post_data=None,retries=3):
        '''返回HTML的数据'''
        result = None
        
        #设置http请求头
        self.headers['Cookie'] = self.get_cookies()
        if self.Referer:
            #检查域名是否相同，不同就不设置
            url_domain = urlparse.urlsplit(url)[1].split(':')[0]
            refer_domain = urlparse.urlsplit(self.Referer)[1].split(':')[0]
            if url_domain == refer_domain:
                self.headers['Referer'] = self.Referer
            
            
        self.opener.addheaders = [(k,v) for k,v in self.headers.iteritems()]
        try:
            if post_data:
                result = self.opener.open(url,self.gen_postdata(post_data)).read()
            else:
                response = self.opener.open(url)
                result = response.read()
            self.Referer = url
            #url += '&security_verify_data=313932302c31303830'
            return result
        except Exception as err:
            if retries == 0:
                raise err
            return self.get_htmldata(url,post_data,retries-1)
