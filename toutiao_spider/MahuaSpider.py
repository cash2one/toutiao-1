# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://www.mahua.com/`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
import bs4
from bs4 import BeautifulSoup
import time
import re
import urlparse
from util import dele_style,modify_tag,update_image,md5
#import uniout

@implementer(ProtoSpider)
class MahuaSpider(BaseSpider):
    def __init__(self,config):
        super(MahuaSpider,self).__init__(config)
        self.url = 'http://www.mahua.com/'
        self.config = config
        self.name = 'MahuaSpider'

    def download_navigation(self,name,url,kw=None):
        """
        下载导航页面的信息
        name:爬虫的名字
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g. 
        {'name':`爬虫名字`,'list':`各个列表页的链接列表`}
        """
        if name != self.name:
            print '该网址与该爬虫不匹配'
            return {}
        try:
            result = []
            result.append({'url':'http://www.mahua.com/','column':[u'段子']})
            return {'name':name,'list':result}
        except:
            traceback.print_exc()
            return {}

    def __download_detail_item__(self,name,url,kw=None):
        """
        下载每个详情页的分页信息
        """
        try:
            data = self.spider.get_data(url)
            soup = BeautifulSoup(data,'lxml')
            read_txt = soup.find('div',attrs={'class':'joke-content'})
            
            img_dict = modify_tag(read_txt)
            
            #下载图片
            imgs = img_dict.keys()
            for img in imgs:
                #下载图片
                img_dict[img]['status'] = 1 if self.download_images(img_dict[img]['url'],img) else 0
            
            dele_style(read_txt)
            update_image(read_txt,img_dict)
            text = read_txt.prettify()
            
            result = {}
            result['text'] = text
            
            #判断有没有结束
            result['next_page'] = None
            result['imgs'] = img_dict
            self.ok_to_redis(url)
            return result
        except:
            traceback.print_exc()
            return {}

    def download_detail(self,name,url,kw=None):
        #下载详情
        if not self.is_need_to_download(url):
            return (False,None)
        result = self.__download_detail__(name,url,kw)
        if result['success']:
            self.add_artical_to_mongo(url,result)
            return (True,md5(url))
        else:
            self.fail_to_redis(url)
            return (False,None)
        
    def __download_detail__(self,name,url,kw=None):
        """
        下载详情页面的信息
        name:爬虫的名字
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g. 
        {'name':`爬虫名字`,'text':`文本`,'title':`标题`,'crawl_time':`下载时间`
        'image':`图像列表`,'source':`来源`,'time':`文章时间`,'introduction ':`导言`,'tags':`标签`}
        """
        if name != self.name:
            print '该网址与该爬虫不匹配'
            return {}
        try:
            data = self.spider.get_data(url)
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'left'})
            ptime = div.find('p',attrs={'class':'joke-uname'}).find('span').get_text().strip()
            title  = div.find('h1',attrs={'class':'joke-title'}).get_text()
            source = u'快乐麻花'
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':'','tags':[]}
            print url
            item = self.__download_detail_item__(name,url)
            result['image'].update(item.get('imgs',{}))
            result['text'] += item['text']
            result['success'] = True
            if kw  != None and isinstance(kw,dict):
                result.update(kw)
            return result
        except:
            traceback.print_exc()
            return {'success':False}
            
    
    def download_list(self,name,url,kw=None):
        """
        name:爬虫的名字
        下载详情页面的信息
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g.{'details':`详情页地址列表`,'next':`下一页地址`}
        """
        if name != self.name:
            print '该网址与该爬虫不匹配'
            return []
        try:
            data = self.spider.get_data(url)
            pattern = re.compile(unicode('http://www.mahua.com/xiaohua/\d+.htm'))
            
            urls = pattern.findall(data)
            details = map(lambda x:{'url':x},urls)
            for detail in details:
                if kw  != None and isinstance(kw,dict):
                    detail.update(kw)
            
            soup =BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'left'})
            href = div.find('div',attrs={'class':'page'}).find('a',text=u'下一页')
            next_url = None
            if href:
                next_url = href.attrs['href']
            answer = {'name':name,'details':details,'next':next_url}
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(MahuaSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = MahuaSpider(config)
    result = mn.__download_detail__(mn.name,'http://www.mahua.com/xiaohua/1660721.htm',{'column':[u'首页']})
    print result
    print mn.is_implemented()