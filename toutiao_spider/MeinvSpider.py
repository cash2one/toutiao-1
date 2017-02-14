# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://www.meinv.com/`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import urlparse
import time
from util import dele_style,modify_tag,update_image,md5

@implementer(ProtoSpider)
class MeinvSpider(BaseSpider):
    def __init__(self,config):
        super(MeinvSpider,self).__init__(config)
        self.url = 'http://www.meinv.com'
        self.config = config
        self.name = 'MeinvSpider'

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
            navigate = soup.find('div',attrs={'class':'nav_box'})
            for dl in navigate.find_all('dl'):
                dt = dl.find('dt')
                name = dt.find('a').attrs['title']
                link = dt.find('a').attrs['href']
                
                #添加到列表中去
                tmp_dict = {}
                tmp_dict['url'] = link
                tmp_dict['column'] = [name]
                result.append(tmp_dict)
                for dd in dl.find_all('dd'):
                    try:
                        href = dd.find('a').attrs['href']
                        title = dd.find('a').attrs['title']
                        tmp_dict = {}
                        tmp_dict['url'] = href
                        tmp_dict['column'] = [name,title]
                        result.append(tmp_dict)
                    except:
                        pass
            return {'name':self.name,'list':result}
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
            div = soup.find('div',attrs={'class':'man_l'}).find('div',attrs={'class':'display_red'})
            read_txt = div.find('div',attrs={'class':'read_txt'})
            img_dict = modify_tag(read_txt)
            
            #下载图片
            imgs = img_dict.keys()
            for img in imgs:
                #下载图片
                img_dict[img]['status'] = 1 if self.download_images(img_dict[img]['url'],img) else 0
            
            dele_style(read_txt)
            update_image(read_txt,img_dict)
            text = read_txt.prettify()
            next_page = div.find('div',attrs={'class':'page'}).find('a',attrs={'title':'下一页'}).attrs['href']
            result = {}
            result['text'] = text
            
            #判断有没有结束
            if next_page == url:
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
            return (False,'Downloaded')
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
        'image':`图像列表`,'source':`来源`,'time':`文章时间`,'introduction ':`导言`}
        """
        if name != self.name:
            print '该网址与该爬虫不匹配'
            return {}
        try:
            data = self.spider.get_data(url)
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'man_l'}).find('div',attrs={'class':'display_red'})
            title = div.find('h1').get_text()
            info_txts = div.find('div',attrs={'class':'info_txt'})
            source = info_txts.find('a').get_text()
            p_time = info_txts.get_text()
            p_time = p_time[p_time.find(u'下一页')+len(u'下一页'):p_time.find(u'来源')].strip()
            
            txt_box = div.find('div',attrs={'class':'txt_box'})
            dele_style(txt_box)
            introduction = txt_box.prettify()
            
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':p_time,'introduction ':introduction}
            while True:
                print url
                item = self.__download_detail_item__(url)
                result['image'].update(item.get('imgs',{}))
                result['text'] += item['text']
                url = item['next_page']
                if url == None or url == 'http://www.meinv.com/hot.html':
                    break
            result['tags'] = []
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
            result = []
            data = self.spider.get_data(url)
            soup = BeautifulSoup(data,'lxml')
            passages = soup.find('div',attrs={'class':'p_box'}).find('ul',attrs={'class':'pic_box_1'})
            for passage in passages.find_all('li'):
                try:
                    #img = passage.find('div',attrs={'class':'pic'}).find('img').attrs['src']
                    text_info = passage.find('div',attrs={'class':'txt_info'}).find('a')
                    link = text_info.attrs['href']
                    #title = text_info.get_text()
                    tmp_dict = {}
                    #tmp_dict['small_img'] = img
                    tmp_dict['url'] = link
                    #tmp_dict['title'] = title
                    if kw  != None and isinstance(kw,dict):
                        tmp_dict.update(kw)
                    result.append(tmp_dict)
                except:
                    pass
                
            next_page = soup.find('div',attrs={'class':'p_box'}).find('div',attrs={'class':'page'})
            link = next_page.find('a',attrs={'class':'next'}).attrs['href']
            next_page = urlparse.urljoin(url,link)
            if next_page == url:
                next_page = None
            answer = {'name':name,'details':result,'next':next_page}
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(MeinvSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = MeinvSpider(config)
    result = mn.download_navigation(mn.name,'http://www.meinv.com/')
    print result
    print mn.is_implemented()