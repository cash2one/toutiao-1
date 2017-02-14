# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 10:58:14 2017

@author: ligong

@description:这是提供爬虫的程序
"""
import zerorpc
import sys
from util import load_config
import traceback
import os
#from multiprocessing import Pool
from multiprocessing import Process

class WebSpiderServer(object):
    def __init__(self,config):
        self.spiders = {}
        self.config = config

    def load_spider(self,module):
        """
        加载爬虫
        """
        if module not in sys.modules:
            print 'from %s import %s' %(module,module)
            try:
                exec 'from %s import %s' %(module,module)
                self.spiders[module] = eval('%s(self.config)' % module)
            except:
                traceback.print_exc()
    
    def download_detail(self,name,url,kw=None):
        """
        下载详情页面的信息
        name:爬虫的名字
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g. 
        {'name':`爬虫名字`,'text':`文本`,'title':`标题`,'crawl_time':`下载时间`
        'image':`图像列表`,'source':`来源`,'time':`文章时间`}
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                return t_spider.download_detail(name,url,kw)
            except:
                traceback.print_exc()
        else:
            print 'This spider: %s is not available!' % name
            return {}
    
    def download_list(self,name,url,kw=None):
        """
        name:爬虫的名字
        下载详情页面的信息
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g.{'details':`详情页地址列表`,'next':`下一页地址`}
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                return t_spider.download_list(name,url,kw)
            except:
                traceback.print_exc()
        else:
            print 'This spider: %s is not available!' % name
            return {}

    def is_need_download(self,name,url):
        """
        判断是否需要下载
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                return t_spider.is_need_to_download(url)
            except:
                traceback.print_exc()
                return True
        else:
            print 'This spider: %s is not available!' % name
            return False
    
    def is_need_to_add_to_mq(self,name,iter_num,url):
        """
        判断是否需要下载
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                return t_spider.is_need_to_add_to_mq(iter_num,url)
            except:
                traceback.print_exc()
                return True
        else:
            print 'This spider: %s is not available!' % name
            return False

    def add_to_mq_redis(self,name,iter_num,url):
        """
        判断是否需要下载
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                t_spider.add_to_mq_redis(iter_num,url)
            except:
                traceback.print_exc()
        else:
            print 'This spider: %s is not available!' % name

    def dele_mq_redis(self,name,iter_num):
        """
        删除
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                t_spider.dele_mq_redis(iter_num)
            except:
                traceback.print_exc()
        else:
            print 'This spider: %s is not available!' % name

    def download_navigation(self,name,kw=None):
        """
        下载导航页面的信息
        name:爬虫的名字
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g. 
        {'name':`爬虫名字`,'list':`各个列表页的链接列表`}
        """
        self.load_spider(name)
        t_spider = self.spiders[name]
        if t_spider.is_implemented():
            try:
                return t_spider.download_navigation(name,t_spider.url,kw)
            except:
                traceback.print_exc()
        else:
            print 'This spider: %s is not available!' % name
            return {}
        

#这是运行server的程序
def run(config,info_index): 
    """
    info_index:对应的第index个地址
    """
    print 'Web Spider %s is running...' % config['server_info'][info_index]
    server = zerorpc.Server(WebSpiderServer(config))
    server.bind(config['server_info'][info_index])
    server.run()
    
if __name__ == '__main__':
    config = load_config(r'E:\machine_code\spider\downloader\webspider.json')
    process_num = len(config['server_info'])
    
    print 'Web Spider Server Parent Running: PID %s.' % os.getpid()
    process_pool = []#Pool(processes =process_num)
    for i in range(process_num):
        p = Process(target=run, args=(config,i))
        process_pool.append(p)
    for p in process_pool:
        p.start()
    for p in process_pool:
        p.join()
  
    print 'Waiting for all subprocesses done...'
    print 'All subprocesses done.'
    
