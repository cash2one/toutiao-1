# -*- coding: utf-8 -*-
"""
Created on Wed Feb 08 15:30:33 2017

@author: ligong

@description:这是用来计数article的阅读uv，推送uv，以及点击率的uv
"""
from util import init_redis

class article_info(object):
    def __init__(self,name,config):
        """
        name:对应的名字
        """
        self.name = name.upper()
        article_info_redis = config['article_info_redis']
        host,port,db = article_info_redis['host'],article_info_redis['port'],article_info_redis['db']
        
        #初始化redis链接
        self.article_info_redis_conn = init_redis(host,port,db)
        
        #push文章的前缀
        self.push_prefix = 'ARTICLE_PUSH_%s_%s'
        
        #read文章的前缀
        self.read_prefix = 'ARTICLE_READ_%s_%s'
        
        #ratio文章的前缀
        self.ratio_prefix = 'ARTICLE_RATIO_%s_%s'
        
        #article信息
        self.article_info_prefix = 'ARTICLE_INFO_%s'
    
    def update_article_info(self,article_id,key,value):
        """
        更新文章信息
        """
        self.article_info_redis_conn.hset(self.article_info_prefix % article_id,key,value)
        
    def update_article_ratio(self,article_id):
        """
        更新文章的点击率
        """
        push_key = self.push_prefix % (self.name,article_id)
        read_key = self.read_prefix % (self.name,article_id)
        
        push_num = self.article_info_redis_conn.pfcount(push_key)
        read_num = self.article_info_redis_conn.pfcount(read_key)
        #有一个值是空，则不做任何（没有值）
        if push_num == None or read_num == None or int(push_num) == 0 or int(read_num) == 0:
            return
        
        ratio_key = self.ratio_prefix % (self.name,article_id)
        self.article_info_redis_conn.set(ratio_key,float(read_num)/float(push_num))
        
    def update_article_push(self,article_id,usid):
        """
        更新文章的推送
        """
        push_key = self.push_prefix % (self.name,article_id)
        self.article_info_redis_conn.pfadd(push_key,usid)
        self.update_article_ratio(article_id)
        
    def update_article_read(self,article_id,usid):
        """
        更新文章的阅读
        """
        read_key = self.read_prefix % (self.name,article_id)
        self.article_info_redis_conn.pfadd(read_key,usid)
        self.update_article_ratio(article_id)

    def read_ratio(self,article_id):
        """
        点击率
        """
        ratio_key = self.ratio_prefix % (self.name,article_id)
        ratio = self.article_info_redis_conn.get(ratio_key)
        if ratio:
            return float(ratio)
        return 0
    
    def push_num(self,article_id):
        """
        推荐次数
        """
        push_key = self.push_prefix % (self.name,article_id)
        push_num = self.article_info_redis_conn.pfcount(push_key) 
        if push_num:
            return int(push_num)
        return 0

if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1}}
    ati = article_info('test',config)
    import time,random
    for i in range(10000):
        ati.update_article_info(i,'create_time',int(time.time())-8640*i)
        t = random.randint(0,9999)
        ati.update_article_push(i,i*3)
        ati.update_article_read(t,i*2)

