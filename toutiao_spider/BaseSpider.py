# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 14:26:53 2017

@author: ligong

@description:这是爬虫的基类
"""
import os
import traceback
from WebCrawler_New import WebCrawler
from persistent.DataPersist import DataPersist
import re
import arrow
class BaseSpider(object):
    def __init__(self,config):
        self.name = 'BaseSpider'
        self.spider = WebCrawler()
        self.data_persist = DataPersist(config)
        self.image_path = config['image_path']
    
    def download_images(self,url,image_id):
        """
        下载图片
        url:图片链接
        image_name:图片名字
        image_path:图片保存的路径
        """
        try:
            if not self.data_persist.is_need_to_download_ok(url):
                return True
            if not self.data_persist.is_need_to_download_fail(url):
                return False
            
            data = self.spider.get_htmldata(url)
            if len(data) == 0:
                self.fail_to_redis(url)
                return False

            tmp = url.split('/')[-1]
            if tmp.find(u'.') >= 0:
                suffix = u'.'+tmp.split(u'.')[-1].strip()
            else:
                suffix = '.jpg'
            suffix = suffix.lower()
            if suffix not in ['.jpg','.bmp','.png','.jpeg']:
                suffix = '.jpg'
            filename = os.path.join(self.image_path,image_id+suffix)
            f = open(filename,'wb')
            f.write(data)
            f.close()
            #添加到redis,mongo
            self.add_image_to_mongo(url,image_id,image_id+suffix)
            self.ok_to_redis(url)
            return True
        except:
            traceback.print_exc()
            self.fail_to_redis(url)
            return False
    
    def fail_to_redis(self,url):
        #下载失败，写到redis
        self.data_persist.add_to_redis(url,False)
    
    def ok_to_redis(self,url):
        #写到redis
        self.data_persist.add_to_redis(url)
    
    def time_value_process(self,time_value):
        """
        时间字符串的处理，变成统一的格式
        """
        return arrow.get(time_value).format('YYYY-MM-DD HH:mm:ss')
        
    def clean(self,data_dict):
        #删除空白的tag
        pattern = re.compile(unicode('<[a-zA-Z0-9]+>\s*</[a-zA-Z0-9]+>'))
        pre_p = re.compile(unicode('<[a-zA-Z0-9]+>'))
        post_p = re.compile(unicode('</[a-zA-Z0-9]+>'))
        pattern_mark = re.compile(unicode('<!--.*-->'))
        if 'text' in data_dict:
            text = data_dict['text']
            text = pattern_mark.sub(u'',text)
            #连续替换多次
            for i in xrange(3):
                for txt in pattern.findall(text):
                    try:
                        if pre_p.findall(txt)[0][1:-1] == post_p.findall(txt)[0][2:-1]:
                            text = text.replace(txt,u'')
                    except:
                        pass
            data_dict['text'] = text
        #时间格式处理
        if 'time' in data_dict:
            try:
                data_dict['time'] = self.time_value_process(data_dict['time'])
            except:
                pass
        return data_dict
        
    def add_artical_to_mongo(self,url,data):
        """
        保存到数据库
        """
        self.data_persist.add_artical_to_mongo(url,self.clean(data))
    
    def add_image_to_mongo(self,url,image_id,image_name):
        """
        保存到数据库
        """
        self.data_persist.add_image_to_mongo(url,image_id,image_name)
    
    def is_need_to_download(self,url):
        """
        判断是否需要下载
        """
        return self.data_persist.is_need_to_download(url)
    
    def is_need_to_add_to_mq(self,iter_num,url):
        """
        判断是否需要添加到队列
        """
        return self.data_persist.is_need_to_add_to_mq(iter_num,url)
    
    def add_to_mq_redis(self,iter_num,url):
        """
        添加到mq的缓存里面
        """
        self.data_persist.add_to_mq_redis(iter_num,url)
    
    def dele_mq_redis(self,iter_num):
        """
        删除
        """
        self.data_persist.dele_mq_redis(iter_num)

if __name__ == '__main__':
    config = {
	"finish_redis":{"host":"127.0.0.1","port":6379,"db":0},
	"toutiao_mongo":{"host":"127.0.0.1:27017"},
	"artical":{"db":"toutiao","table":"toutiao_artical"},
	"image":{"db":"toutiao","table":"toutiao_image"},
	"image_path":"E:/download_image",
	"server_info":["tcp://127.0.0.1:11111","tcp://127.0.0.1:11112","tcp://127.0.0.1:11113","tcp://127.0.0.1:11114","tcp://127.0.0.1:11115","tcp://127.0.0.1:11116"]
    }
    bs = BaseSpider(config)
    print bs.time_value_process('2017-01-14 10:11')

