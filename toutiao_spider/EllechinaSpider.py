# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://www.ellechina.com/`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import time
import re
from util import dele_style,modify_tag,update_image,md5
#import uniout

@implementer(ProtoSpider)
class EllechinaSpider(BaseSpider):
    def __init__(self,config):
        super(EllechinaSpider,self).__init__(config)
        self.url = 'http://www.ellechina.com/'
        self.config = config
        self.name = 'EllechinaSpider'

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
            data = self.spider.get_data(url)
            soup = BeautifulSoup(data,'lxml')
            result = []
            navigate = soup.find('div',attrs={'class':'nav'}).find('ul',attrs={'class':'clearfixed menubar'})
            for li in navigate.find_all('li'):
                a = li.find('a')
                link = a.attrs['href']
                name = a.get_text().strip()
                #添加到列表中去
                tmp_dict = {}
                tmp_dict['url'] = link
                tmp_dict['column'] = [name]
                result.append(tmp_dict)
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
            read_txt = soup.find('div',attrs={'class':'c-article_content'})
            
            img_dict = modify_tag(read_txt)
            
            #下载图片
            imgs = img_dict.keys()
            for img in imgs:
                #下载图片
                img_dict[img]['status'] = 1 if self.download_images(img_dict[img]['url'],img) else 0
            
            dele_style(read_txt)
            update_image(read_txt,img_dict)
            text = read_txt.prettify()
            next_page = soup.find('span',attrs={'class':'c-pager-next'}).find('a').attrs['href']
            result = {}
            result['text'] = text
            
            #判断有没有结束
            tmp_1 = url.split('/')[-1]
            tmp_2 = next_page.split('/')[-1]
            tmp_1 = tmp_1[:tmp_1.find('.')]
            tmp_2 = tmp_2[:tmp_2.find('.')]
            if '-'.join(tmp_1.split('-')[:2]) != '-'.join(tmp_2.split('-')[:2]):
                next_page = None
            result['next_page'] = next_page
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
            
            title = soup.find('h1',attrs={'class':'c-article_h1 c-article_title'}).get_text().strip()
            source = soup.find('span',attrs={'class':'c-article_source_source'}).get_text()
            source = source[source.find(u'来源：')+len(u'来源：'):].strip()
            introduction = soup.find('div',attrs={'class':'panel panel-grey'})
            dele_style(introduction)
            introduction = introduction.prettify()
            t_tags = soup.find('div',attrs={'class':'c-article_tag'})
            tags = []
            for tag in t_tags.find_all('a',attrs={'class':'f-l mar-l-5 inline ov'}):
                tags.append(tag.get_text().strip())
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':'','introduction ':introduction,'tags':tags}


            while True:
                print url
                item = self.__download_detail_item__(name,url)
                result['image'].update(item.get('imgs',{}))
                result['text'] += item['text']
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
            data = self.spider.get_data(url)
           
            if url == self.url:
                pattern = re.compile(unicode(url+'[a-zA-Z0-9]+/[a-zA-Z0-9]+/\d{8}-\d+.shtml'))
            else:
                pattern = re.compile(unicode(url+'[a-zA-Z0-9]+/\d{8}-\d+.shtml'))
            urls = pattern.findall(data)
            details = map(lambda x:{'url':x},urls)
            for detail in details:
                if kw  != None and isinstance(kw,dict):
                    detail.update(kw)
            answer = {'name':name,'details':details,'next':None}
            
            
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(EllechinaSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = EllechinaSpider(config)
    result = mn.download_list(mn.name,'http://www.ellechina.com/fashion/',{'column':[u'首页']})
    print result
    print mn.is_implemented()