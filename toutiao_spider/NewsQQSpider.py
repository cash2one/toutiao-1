# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:53:13 2017

@author: ligong

@description:这是下载`NewsQQSpider`上的信息的程序
"""
import traceback
from ProtoSpider import ProtoSpider
from zope.interface import implementer
from BaseSpider import BaseSpider
from bs4 import BeautifulSoup
import time
from util import dele_style,modify_tag,update_image,md5,request_ajax_data
#import uniout

@implementer(ProtoSpider)
class NewsQQSpider(BaseSpider):
    def __init__(self,config):
        super(NewsQQSpider,self).__init__(config)
        self.url = 'http://roll.news.qq.com/'
        self.config = config
        self.name = 'NewsQQSpider'

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
            data = self.spider.get_data(url,'gb2312')
            soup = BeautifulSoup(data,'lxml')
            read_txt = soup.find('div',attrs={'class':'Cnt-Main-Article-QQ'})
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
            data = self.spider.get_data(url,'gb2312',retries=100)
            soup = BeautifulSoup(data,'lxml')
            div = soup.find('div',attrs={'class':'qq_article'})
            info = div.find('div',attrs={'class':'hd'})
            title = info.find('h1').get_text().strip()
            
            source = info.find('span',attrs={'class':'a_source'}).get_text().strip()
            
            ptime = info.find('span',attrs={'class':'a_time'}).get_text().strip()
            tags = [info.find('span',attrs={'class':'a_catalog'}).get_text().strip()]
            result = {'name':self.name,'text':u'','title':title,'crawl_time':int(time.time()),
            'image':{},'source':source,'time':ptime,'introduction ':'','tags':tags}

            max_num = 10
            num = 0
            while num <= max_num:
                try:
                    item = self.__download_detail_item__(url)
                    result['image'].update(item.get('imgs',{}))
                    result['text'] += item['text']
            
                    result['success'] = True
                    if kw  != None and isinstance(kw,dict):
                        result.update(kw)
                    break
                except:
                    num += 1
                    time.sleep(0.1)
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
            reffer = 'http://roll.news.qq.com/index.htm?site=news&mod=1&date=2017-01-01&cata='
            news_dict = request_ajax_data('http://roll.news.qq.com/interface/roll.php?0.005883038924627826&cata=&site=news&date=&page=1&mode=1&of=json',
                                    None,reffer,
                                    encoding='gb2312')
            
            count = news_dict['data']['count']
            tmp_info = []
            page = news_dict['data']['page']
            tmp_info.append(news_dict['data']['article_info'])
            
            for i in xrange(page+1,count+1):
                url = 'http://roll.news.qq.com/interface/roll.php?0.005883038924627826&cata=&site=news&date=&page=%s&mode=1&of=json' % i
                news_dict = request_ajax_data(url,None,reffer,encoding='gb2312')
                tmp_info.append(news_dict['data']['article_info'])
            
            details = []
            for article_info in tmp_info:
                soup = BeautifulSoup(article_info,'lxml')
                for li in soup.find_all('li'):
                    try:
                        tmp = {}
                        tmp['url'] = li.find('a').attrs['href']
                        tmp['title'] = li.find('a').get_text().strip()
                        tmp['column'] = [li.find('span',attrs={'class':'t-tit'}).get_text().strip()[1:-1]]
                        details.append(tmp)
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
        return ProtoSpider.implementedBy(NewsQQSpider)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    
    mn = NewsQQSpider(config)
    result = mn.download_detail(mn.name,'http://news.qq.com/a/20170114/009441.htm')
    print result