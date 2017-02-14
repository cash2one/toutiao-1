# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://www.huanqiu.com/`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import time
#import re
from util import dele_style,modify_tag,update_image,md5
#import uniout

@implementer(ProtoSpider)
class HuanQiuSpider(BaseSpider):
    def __init__(self,config):
        super(HuanQiuSpider,self).__init__(config)
        self.url = 'http://www.huanqiu.com/'
        self.config = config
        self.name = 'HuanQiuSpider'

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
            result.append({'url':'http://china.huanqiu.com/article/','column':[u'国内']})
            result.append({'url':'http://world.huanqiu.com/article/','column':[u'国际']})
            result.append({'url':'http://taiwan.huanqiu.com/article/','column':[u'台海']})
            result.append({'url':'http://women.huanqiu.com/beauty/','column':[u'美容']})
            result.append({'url':'http://women.huanqiu.com/xzml/','column':[u'星座']})
            result.append({'url':'http://women.huanqiu.com/loseweight/','column':[u'瘦身']})
            result.append({'url':'http://fashion.huanqiu.com/nxfs/','column':[u'乐活']})
            result.append({'url':'http://oversea.huanqiu.com/article/','column':[u'海外']})
            result.append({'url':'http://society.huanqiu.com/article/','column':[u'社会']})
            result.append({'url':'http://women.huanqiu.com/beauty/','column':[u'女人']})
            return {'name':name,'list':result}
        except:
            traceback.print_exc()
            return {}

    def __download_detail_item__(self,url):
        """
        下载每个详情页的分页信息
        """
        try:
            data = self.spider.get_data(url)
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'conText'})
            read_txt = div.find('div',attrs={'id':'text'})
            next_url = None
            try:
                tmps = div.find('div',attrs={'id':'pages'}).find_all('a',attrs={'class':'a1'})
                for t in tmps:
                    if t.get_text().find(u'下一页') >= 0:
                        next_url = t.attrs['href']
                if url == next_url:
                    next_url = None
                div.find('div',attrs={'id':'pages'}).decompose()
            except:
                #traceback.print_exc()
                pass
                
            
            
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

            result['next_page'] = next_url
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
            
            div = soup.find('div',attrs={'class':'conText'})
            ptime = div.find('strong',attrs={'class':'timeSummary'}).get_text().strip()
            
            title = div.find('h1').get_text().strip()
            source = soup.find('strong',attrs={'class':'fromSummary'}).get_text()          
            tags = []
            
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':'','tags':tags}


            while True:
                print url
                item = self.__download_detail_item__(url)
                result['image'].update(item.get('imgs',{}))
                result['text'] += item.get('text','')

                url = item['next_page']
                if url == None:
                    break
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
            details = []
            data = self.spider.get_data(url)
           
            soup = BeautifulSoup(data,'lxml')
            for li in soup.find('div',attrs={'class':'fallsFlow'}).find_all('li',attrs={'class':'item'}):
                details.append({'url':li.find('a').attrs['href']})
            
            for detail in details:
                if kw  != None and isinstance(kw,dict):
                    detail.update(kw)
            tmps = soup.find('div',attrs={'id':'pages'}).find_all('a',attrs={'class':'a1'})
            next_url = None
            for t in tmps:
                if t.get_text().find(u'下一页') >= 0:
                    next_url = t.attrs['href']
            if url == next_url:
                next_url = None
            answer = {'name':name,'details':details,'next':next_url}
            
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(HuanQiuSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = HuanQiuSpider(config)
    result = mn.download_detail(mn.name,'http://china.huanqiu.com/hot/2017-02/10072846.html',{'column':[u'首页']})
    #print result