# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`网易新闻`上的信息的程序
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
class NetEasySpider(BaseSpider):
    def __init__(self,config):
        super(NetEasySpider,self).__init__(config)
        self.url = 'http://www.163.com/'
        self.config = config
        self.name = 'NetEasySpider'
        
        #对用的api的链接
        self.__info_dict__ = {'http://news.163.com/':'http://temp.163.com/special/00804KVA/cm_yaowen.js?callback=data_callback',
                     'http://ent.163.com/':'http://ent.163.com/special/000380VU/newsdata_index.js?callback=data_callback',
                     'http://fashion.163.com/':'http://fashion.163.com/special/002688FE/fashion_datalist.js?callback=data_callback',
                     'http://travel.163.com/':'http://travel.163.com/special/00067VEJ/newsdatas_travel.js?callback=data_callback',
                     'http://ent.163.com/movie/':'http://ent.163.com/special/000381Q1/newsdata_movieidx.js?callback=data_callback',
                     'http://ent.163.com/music/':'http://ent.163.com/special/000381AH/newsdata_music_index.js?callback=data_callback',
                     'http://ent.163.com/tv/':'http://ent.163.com/special/000381P3/newsdata_tv_index.js?callback=data_callback',
                     'http://lady.163.com/':'http://lady.163.com/special/00264OOD/data_nd_fashion.js?callback=data_callback',
                     'http://edu.163.com/':'http://edu.163.com/special/002987KB/newsdata_edu_hot.js?callback=data_callback',
                     'http://baby.163.com/':'http://baby.163.com/special/003687OS/newsdata_hot.js?callback=data_callback'
                     }

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
            result.append({'url':'http://news.163.com/','column':[u'新闻']})
            result.append({'url':'http://ent.163.com/','column':[u'娱乐']})
            result.append({'url':'http://fashion.163.com/','column':[u'时尚']})
            result.append({'url':'http://travel.163.com/','column':[u'旅游']})
            result.append({'url':'http://ent.163.com/movie/','column':[u'娱乐',u'电影']})
            result.append({'url':'http://ent.163.com/music/','column':[u'娱乐',u'音乐']})
            result.append({'url':'http://ent.163.com/tv/','column':[u'娱乐',u'电视']})
            result.append({'url':'http://lady.163.com/','column':[u'女人']})
            result.append({'url':'http://edu.163.com/','column':[u'教育']})
            result.append({'url':'http://baby.163.com/','column':[u'亲子']})
            return {'name':name,'list':result}
        except:
            traceback.print_exc()
            return {}

    def __download_detail_item__(self,url):
        """
        下载每个详情页的分页信息
        """
        try:
            data = self.spider.get_data(url,'gbk')
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'post_content_main'})
            read_txt = div.find('div',attrs={'class':'post_text'})
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
            data = self.spider.get_data(url,'gbk')
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'post_content_main'})
            title = div.find('h1').get_text().strip()
            source = div.find('div',attrs={'class':'post_time_source'}).get_text()
            ptime = source[:source.find(u'来源')].strip()
            source = source[source.find(u'来源:')+len(u'来源:'):].strip()
         
            introduction = u''
            
            tags = []
            
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':introduction,'tags':tags}

            item = self.__download_detail_item__(url)
            result['text'] += item['text']
            result['image'].update(item.get('imgs',{}))
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
            #链接不合法
            if url not in self.__info_dict__:
                return {}
            api_url = self.__info_dict__[url]
            max_page = 5
            
            #页面的url
            def gen_page_url(index):
                if index == 0:
                    return api_url
                return api_url[:api_url.find('.js?callback=data_callback')]+'_0'+str(index+1)+'.js?callback=data_callback' 
            items = []
        
            #获得所有的详情
            for i in xrange(max_page):
                iter_url = gen_page_url(i)
                data = self.spider.get_data(iter_url,'utf8').strip()
                data = data[len(u'data_callback('):-1]
                items.extend(eval(data))
            details = []
            pattern = re.compile(unicode(url+'\d{2}/\d{4}/\d{2}/[A-Z0-9]+.html'))
            for item in items:
                try:
                    url = item['docurl']
                    tmp = pattern.findall(url)
                    label = item.get('label','')
                    if label != '':
                        label = label.decode('gbk','ignore')
                    if len(tmp) >= 1:
                        url = tmp[0]
                    else:
                        continue
                    detail = {'url':url}
                    if kw  != None and isinstance(kw,dict):
                        detail.update(kw)
                    details.append(detail)
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
        return ProtoSpider.implementedBy(NetEasySpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = NetEasySpider(config)
    result = mn.download_detail(mn.name,'http://lady.163.com/17/0113/13/CALPVPPH00267VQQ.html',{'column':[u'首页']})
    #print mn.is_implemented()
    print result