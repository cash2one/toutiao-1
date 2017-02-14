# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=89&spec=&type=&ch=01&k=&offset_page=0&offset_num=0&num=60&asc=&page=1`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import time
from util import dele_style,modify_tag,update_image,md5
#import uniout
#import json

@implementer(ProtoSpider)
class SinaSpider(BaseSpider):
    def __init__(self,config):
        super(SinaSpider,self).__init__(config)
        self.url = 'http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=89&spec=&type=&ch=01&k=&offset_page=0&offset_num=0&num=60&asc=&page=1'
        self.config = config
        self.name = 'SinaSpider'

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

    def __download_detail_item__(self,url):
        """
        下载每个详情页的分页信息
        """
        try:
            #data = self.spider.__get_data_after_error__(url,'utf8')
            data = self.spider.get_data(url,encode='utf8')
            soup = BeautifulSoup(data,'lxml')
            read_txt = soup.find('div',attrs={'id':'artibody'})
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
            #data = self.spider.__get_data_after_error__(url,'utf8')
            data = self.spider.get_data(url,encode='utf8')
            soup = BeautifulSoup(data,'lxml')
            title = soup.find('meta',attrs={'property':'og:title'}).attrs['content']
            
            ptime = soup.find('meta',attrs={'property':'article:published_time'}).attrs['content']
            
            source = soup.find('meta',attrs={'property':'article:author'}).attrs['content']
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':'','tags':[]}
            
            item = self.__download_detail_item__(url)
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
            page_num = int(url[url.find('&page=')+len('&page='):])
            details = []
            data = self.spider.get_data(url,'gb2312')
            #用于生成json格式
            replace_set = []
            replace_set.append({'channel :':'"channel" :'})
            replace_set.append({'title :':'"title" :'})
            replace_set.append({',id :':',"id" :'})
            replace_set.append({',cType :':',"cType" :'})
            replace_set.append({',type :':',"type" :'})
            replace_set.append({',url :':',"url" :'})
            replace_set.append({',pic :':',"pic" :'})
            replace_set.append({',time :':',"time" :'})
            data = data[data.find(u'list : ')+len(u'list : '):].strip()[:-2]
            for r in replace_set:
                for k,v in r.iteritems():
                    data = data.replace(k,v)
            data_dict = eval(data)
            for d in data_dict:
                tmp = {'url':d['url'],'column':[d['channel']['title'].decode('utf8','ignore')]}
                details.append(tmp)
            
            if page_num >= 200:
                next_url = None
            else:
                next_url = url[:url.find('&page=')] + '&page='+str(page_num+1)
                
            answer = {'name':name,'details':details,'next':next_url}
            return answer
        except:
            traceback.print_exc()
            return {}
    
    def is_implemented(self):
        """
        是否实现了该接口
        """
        return ProtoSpider.implementedBy(SinaSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = SinaSpider(config)
    result = mn.__download_detail__(mn.name,'http://sports.sina.com.cn/others/volleyball/2017-01-18/doc-ifxzqnim4880997.shtml')
    #print result