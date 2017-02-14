# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://www.chinanews.com/scroll-news/news1.html`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import time
import urlparse
from util import dele_style,modify_tag,update_image,md5
#import uniout

@implementer(ProtoSpider)
class ChinanewsSpider(BaseSpider):
    def __init__(self,config):
        super(ChinanewsSpider,self).__init__(config)
        self.url = 'http://www.chinanews.com/scroll-news/news1.html'
        self.config = config
        self.name = 'ChinanewsSpider'

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
            result = {'name':name,'list':[{'url':self.url,'column':[u'新闻']}]}
            return result
        except:
            traceback.print_exc()
            return {}

    def __download_detail_item__(self,name,url,kw=None):
        """
        下载每个详情页的分页信息
        """
        try:
            data = self.spider.get_data(url,'gb2312')
            soup = BeautifulSoup(data,'lxml')
            read_txt = soup.find('div',attrs={'class':'content'})
            mytext = '<div class="tmp">'
            for div in read_txt.find_all('div'):
                css = div.attrs.get('class',[])
                if css in [['left_zw'],['left_ph']]:
                    mytext += div.prettify()
            mytext += '</div>'
            read_txt = BeautifulSoup(mytext,'lxml')
            
            read_txt = read_txt.find('div',attrs={'class':'tmp'})
            
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
            data = self.spider.get_data(url,'gb2312',retries=4)
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'content'})
            title = div.find('h1').get_text().strip()
            tmp = div.find('div',attrs={'class':'left-t'}).get_text().strip()
            ptime = tmp[:tmp.find(u'来源：')].strip()
            source = tmp[tmp.find(u'来源：')+len(u'来源：'):tmp.find(u'参与互动')].strip()
            
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':'','tags':[]}

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
            details = []
            
            for i in range(1,11):
                url = 'http://www.chinanews.com/scroll-news/news'+str(i)+'.html'
                print url
                try:
                    data = self.spider.get_data(url,'gb2312')
                    soup = BeautifulSoup(data,'lxml')
                    div = soup.find('div',attrs={'class':'content_list'})
                    for li in div.find_all('li'):
                        if 'class' in li.attrs:
                            continue
                        try:
                            column = li.find('div',attrs={'class':'dd_lm'}).get_text().strip()[1:-1]
                            if column in [u'视频',u'图片']:
                                continue
                            link = li.find('div',attrs={'class':'dd_bt'}).find('a').attrs['href']
                            details.append({'url':link,'column':[column]})
                        except:
                            pass
                except:
                    pass
                
            answer = {'name':name,'details':details,'next':None}
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(ChinanewsSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = ChinanewsSpider(config)
    result = mn.__download_detail__(mn.name,'http://www.chinanews.com/yl/2017/01-16/8125553.shtml')
    print result