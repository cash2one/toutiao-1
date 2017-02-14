# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 17:01:47 2017

@author: ligong

@description:冷启动的缓存类
"""
from util import init_redis
from toutiao_article_info import toutiao_article_info
from toutiao_hot_article import toutiao_hot_article


class cold_start(object):
    #读取文章的点击率
    TOUTIAO_ARTICEL_INFO = None
    
    #添加到热帖中去
    TOUTIAO_HOT_ARTICLE = None
    
    def __init__(self,name,config):

        if cold_start.TOUTIAO_ARTICEL_INFO == None:
            cold_start.TOUTIAO_ARTICEL_INFO = toutiao_article_info(config)
        
        if cold_start.TOUTIAO_HOT_ARTICLE == None:
            cold_start.TOUTIAO_HOT_ARTICLE = toutiao_hot_article(config)
        
        """
        缓存的名字
        """
        self.name = name.upper()
        
        #冷启动最大次数，热帖的点击率的阈值
        self.cold_start_max_no = config['cold_start_max_no']
        self.hot_article_threshold = config['hot_article_threshold']

        #冷启动的redis地址
        cold_start_redis = config['cold_start_redis']
        host,port,db = cold_start_redis['host'],cold_start_redis['port'],cold_start_redis['db']
        #初始化链接
        self.cold_start_redis_conn = init_redis(host,port,db)
        self.cold_start_prefix = 'COLD_START_%s_%s'
    
    
    def delete_from_cold_start_cache(self,article_id,stage=None):
        """
        从冷启动缓存表中删除
        """
        #除了全局，其他的没有阶段分类
        if self.name != 'GLOBAL':
            stage = None
        
        key = self.cold_start_prefix % (self.name,'NO' if stage == None else stage)
        self.cold_start_redis_conn.zrem(key,article_id)
    
    def add_to_cold_start_cache(self,article_id,stage=None):
        """
        添加到冷启动缓存表中去
        """
        #除了全局，其他的没有阶段分类
        if self.name != 'GLOBAL':
            stage = None
        #获得push次数，一般情况应该是0，但是不排除其他情况，所有还要从缓存里面读取一遍
        push_num = cold_start.TOUTIAO_ARTICEL_INFO.push_num(article_id,stage,self.name)
        key = self.cold_start_prefix % (self.name,'NO' if stage == None else stage)
        self.cold_start_redis_conn.zadd(key,article_id,push_num)
        
    def update_cold_start_item(self,article_id,stage=None):
        """
        更新到冷启动的缓存里面
        """
        if stage != None and self.name != 'GLOBAL':
            stage = None
        key = self.cold_start_prefix % (self.name,'NO' if stage == None else stage)
        read_ratio = cold_start.TOUTIAO_ARTICEL_INFO.read_ratio(article_id,stage,self.name)
        push_num = cold_start.TOUTIAO_ARTICEL_INFO.push_num(article_id,stage,self.name)
        
        #冷启动达到次数，但是点击率不行，从冷启动表删除
        if push_num >= self.cold_start_max_no and read_ratio < self.hot_article_threshold:
            self.delete_from_cold_start_cache(article_id,stage)
            return
        
        #冷启动达到次数，点击率满足热帖需求阈值，从冷启动表删除，添加到热帖表中去
        if push_num >= self.cold_start_max_no and read_ratio >= self.hot_article_threshold:
            cold_start.TOUTIAO_HOT_ARTICLE.update_score(article_id,stage,self.name)
            self.delete_from_cold_start_cache(article_id,stage)
            return
        
        #剩下的情况更新push次数
        self.cold_start_redis_conn.zadd(key,article_id,push_num)
        
    def update_cold_start(self,stage=None):
        """
        全部更新冷启动
        """
        if stage != None and self.name != 'GLOBAL':
            stage = None
        key = self.cold_start_prefix % (self.name,'NO' if stage == None else stage)
        #遍历所有的等待启动的文章
        for article_id in self.cold_start_redis_conn.zrange(key,0,-1):
            try:
                #更新
                self.update_cold_start_item(article_id,stage)
            except:
                pass
    
    def get_cold_start_articles(self,article_no,stage=None):
        """
        获得需要推荐的文章
        """
        if stage != None and self.name != 'GLOBAL':
            stage = None
        
        key = self.cold_start_prefix % (self.name,'NO' if stage == None else stage)
        
        #zrangebyscore是从小到大来返回的
        return list(self.cold_start_redis_conn.zrange(key,0,article_no-1))

if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1},
              'hot_article_redis':{'host':'127.0.0.1','port':6379,'db':2},
                'cold_start_redis':{'host':'127.0.0.1','port':6379,'db':3},
            'cold_start_max_no':0,'hot_article_threshold':0.4}

    cs = cold_start('test_1',config)
    
    for i in range(10):
        cs.add_to_cold_start_cache(i)
    
    