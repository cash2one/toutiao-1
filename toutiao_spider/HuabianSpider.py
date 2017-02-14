# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://www.huabian.com/`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import time
import urlparse
from util import dele_style,modify_tag,update_image,md5
import re

@implementer(ProtoSpider)
class HuabianSpider(BaseSpider):
    def __init__(self,config):
        super(HuabianSpider,self).__init__(config)
        self.url = 'http://www.huabian.com/'
        self.config = config
        self.name = 'HuabianSpider'

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
            result.append({'url':'http://www.huabian.com/yule/','column':[u'娱乐']})
            return {'name':name,'list':result}
        except:
            traceback.print_exc()
            return {}

    def __download_detail_item__(self,name,url,kw=None):
        """
        下载每个详情页的分页信息
        """
        try:
            data = self.spider.get_data(url,'utf8')
            soup = BeautifulSoup(data,'lxml')
            read_txt = soup.find('div',attrs={'class':'article_content'})
            
            img_dict = modify_tag(read_txt)
            
            #下载图片
            imgs = img_dict.keys()
            for img in imgs:
                #下载图片
                img_url = urlparse.urljoin(url,img_dict[img]['url'])
                img_dict[img]['status'] = 1 if self.download_images(img_url,img) else 0
            
            dele_style(read_txt)
            update_image(read_txt,img_dict)
            text = read_txt.prettify()
            result = {}
            result['text'] = text
            #判断有没有结束
            next_url = soup.find('div',attrs={'class':'box04_left yema'}).find('a',text=u'下一页')
            if next_url and 'href' in next_url.attrs:
                next_url = urlparse.urljoin(url,next_url.attrs['href'])
                if next_url == url:
                    next_url = None
            else:
                next_url = None
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
            data = self.spider.get_data(url,'utf8')
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'box_left'})
            title = div.find('h1').get_text().strip()
            ptime = div.find('span',attrs={'class':'arctime'}).get_text().strip()
            source = u'互联网改编'
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':'','tags':[]}
            
            while True:
                print url
                item = self.__download_detail_item__(name,url)
                result['image'].update(item.get('imgs',{}))
                result['text'] += item['text']
                url = item['next_page']
                if url == None:
                    break
            
            if kw  != None and isinstance(kw,dict):
                result.update(kw)
            result['text'] = result['text'].replace(u'（下一页更精彩）','')
            #result = self.dele_empty_tag(result)
            result['success'] = True
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
            pattern = re.compile(unicode('http://www.huabian.com/[a-z]+/\d{8}/\d+.html'))
            data = self.spider.get_data(url,'utf8')
            
            details = map(lambda x:{'url':x},pattern.findall(data))
            soup = BeautifulSoup(data,'lxml')

            next_url = soup.find('div',attrs={'id':'pages'}).find('a',text=u'下一页')
            if next_url and 'href' in next_url.attrs:
                next_url = urlparse.urljoin(url,next_url.attrs['href'])
                if next_url == url:
                    next_url = None
            else:
                next_url = None
                
            for detail in details:
                if kw  != None and isinstance(kw,dict):
                    detail.update(kw)
            answer = {'name':name,'details':details,'next':next_url}
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(HuabianSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = HuabianSpider(config)
    result = mn.__download_detail__(mn.name,'http://www.huabian.com/baoliao/20170105/155752.html')
    print 'tr',result['text']
