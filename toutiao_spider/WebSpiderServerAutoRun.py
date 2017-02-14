# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 18:15:04 2017

@author: ligong
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 10:58:14 2017

@author: ligong

@description:这是提供爬虫的程序
"""
import time
import os
from persistent.util import init_redis
from util import load_config
import traceback
from WebSpiderServer import WebSpiderServer
from MsgClient import MsgClient
from multiprocessing import Process
import signal

class WebSpiderServerAutoRun(object):
    def __init__(self,config):
        self.spiders = {}
        self.config = config
        self.WebSpiderServer = WebSpiderServer(config)
        
        #消息队列
        self.msg_client = MsgClient(config['mq_address'])
        
        #迭代次数
        self.iter_num = 0

        #用来实时获取需要爬取的网站名字
        spider_name_redis_info = self.config['spider_name_redis']
        self.spider_name_redis = init_redis(spider_name_redis_info['host'],spider_name_redis_info['port'],spider_name_redis_info['db'])
        self.spider_name_key = 'spider_name_set'
   
    def update_iter_num(self):
        """
        更新迭代次数
        """
        self.iter_num += 1
        self.iter_num %= 9999
    
    def pre_iter_num(self):
        """
        前一次迭代次数
        """
        if self.iter_num == 0:
            return 9999
        return self.iter_num - 1

    def gen_jobs(self,spider_name,kw=None):
        """
        获得下载的链接
        """
        result = self.WebSpiderServer.download_navigation(spider_name,kw)
       
        for item in result['list']:
            try:
                max_url_num,next_num = 0,0
                next_url = item['url']
                column = item['column']
                print next_url
                #为了限制下载的网页过于老
                while next_num <= 10 and max_url_num <= 1000:
                    d_list = self.WebSpiderServer.download_list(spider_name,next_url,{'column':column})
                    for each in d_list['details']:
                        try:
                            t_url = each['url']
                            column = column if each.get('column',None) == None else each.get('column',None)
                            
                            #判断是否已经下载过了
                            if self.WebSpiderServer.is_need_to_add_to_mq(spider_name,self.pre_iter_num(),t_url) and self.WebSpiderServer.is_need_to_add_to_mq(spider_name,self.iter_num,t_url):
                                self.msg_client.add_to_mq('spider_to_download',{'name':spider_name,'url':t_url,'column':column,'kw':kw})
                                self.WebSpiderServer.add_to_mq_redis(spider_name,self.iter_num,t_url)
                        except:
                            traceback.print_exc()
                    next_url = d_list['next']
                    if next_url == None:
                        break
                    next_num += 1
                    max_url_num += 1
            except:
                traceback.print_exc()
    
    def process_job(self):
        """
        获得需要爬取的链接
        """
        while True:
            self.update_iter_num()
            sname = None
            for name in self.spider_name_redis.smembers(self.spider_name_key):
                try:
                    if name != 'BudejieSpider':
                        continue
                    self.gen_jobs(name)
                    sname = name
                except:
                    traceback.print_exc()
                    print name
            self.WebSpiderServer.dele_mq_redis(sname,self.pre_iter_num())
            time.sleep(600)
    
    def process_detail(self):
        max_sleep_time = 60
        now_sleep_time = 1
        while True:
            try:
                result = self.msg_client.get_from_mq('spider_to_download')
                print result
                if result == None:
                    now_sleep_time += now_sleep_time
                    if now_sleep_time >= max_sleep_time:
                        now_sleep_time = max_sleep_time
                    time.sleep(now_sleep_time)
                    continue
            
               
                spider_name,url,kw,column = result['name'],result['url'],result['kw'],result['column']
                print 'download %s...' % url
                if kw == None:
                    kw = {'column':column}
                else:
                    kw.update({'column':column})
                print spider_name 
                spider_result = self.WebSpiderServer.download_detail(spider_name,url,kw)
                #返回，(是否成功，id)
                print spider_result
                if spider_result[0]:
                    self.msg_client.add_to_mq('artical_to_cutword',{'_id':spider_result[1]})
                now_sleep_time = 1
            except:
                traceback.print_exc()


def run_detail(config): 
    """
    运行程序
    """
    print 'Web Detail Spider %s is running...' % os.getpid() 
    wssa = WebSpiderServerAutoRun(config)
    wssa.process_detail()
    
def run_job(config):
    """
    运行程序
    """
    print 'Web Job Spider %s is running...' % os.getpid()
    wssa = WebSpiderServerAutoRun(config)
    wssa.process_job()

def term(sig_num, addtion):
    print 'current pid is %s, group id is %s' % (os.getpid(), os.getpgrp())
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM,term)
    config = load_config('/home/toutiao/config/webspider.json')
    process_job_num = config['process_job_num']
    process_detail_num = config['process_detail_num']
    process_pool = []

    for i in xrange(process_job_num):
        p = Process(target=run_job, args=(config,))
        process_pool.append(p)
        
    for i in xrange(process_detail_num):
        p = Process(target=run_detail, args=(config,))
        process_pool.append(p)
        
    for p in process_pool:
        p.daemon = True
        p.start()
    for p in process_pool:
        p.join()
