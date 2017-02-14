# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 17:43:50 2017

@author: ligong

@description:这是头条相似文章的类
"""
import Queue
import sys
sys.path.append('..')

from toutiao_similar.similarity_cache import similarity_cache
import threading

class toutiao_similarity_processor(object):
    def __init__(self,config):
        #运行similarity_cache的线程数量
        self.similarity_thread_no = config['similarity_thread_no']
        
        self.job_queue = Queue.Queue()
        self.my_similarity_caches = []
        for i in xrange(self.similarity_thread_no):
            self.my_similarity_caches.append(similarity_cache(config))
        self.my_similarity_cache = similarity_cache(config)
        
    def add_job(self,view_data):
        """
        添加用户阅读信息到job中去
        """
        self.job_queue.put(view_data)
     
    def process(self,idx):
        print 'thread %s is running...' % idx
        while not self.job_queue.empty():
            try:
                view_data = self.job_queue.get()
                print 'thread %s' % idx
                self.my_similarity_caches[idx].add_to_cache(view_data)
            except:
                pass
        print 'thread %s ends!' % idx
        
    def run(self):
        #最终结果保存
        threads = []
        for i in xrange(self.similarity_thread_no):
            threads.append(threading.Thread(target = self.process, args = (i,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.my_similarity_cache.result_to_db()



if __name__ == '__main__':
    config = {}
    config['similarity_redis'] = {'host':'127.0.0.1','port':6379,'db':4}
    config['similarity_mongo'] = {'host':'127.0.0.1:27017','db':'toutiao','table_for_calcu':'similarty_calcu','table':'similarity_score'}
    config['article_pair_max_cache_no'] = 100000
    config['similarity_thread_no'] = 3
    
    ts = toutiao_similarity_processor(config)
    for i in range(10):
        t = {}
        for j in range(10):
            t[j] = 1
        ts.add_job(t)
    #申明类
    #process(config)
    ts.run()
    
    