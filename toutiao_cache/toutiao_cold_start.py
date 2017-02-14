# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 09:21:37 2017

@author: ligong

@description:这是头条的冷启动类
"""
from cold_start import cold_start

class toutiao_cold_start(object):
    def __init__(self,config):
        self.config = config
        self.cold_start_dict = {}
        
    
    def add_new_cold_start(self,name):
        """
        添加一个栏目的文章
        """
        name = name.upper()
        if name in self.cold_start_dict:
            return '%s already in!' % name
        self.cold_start_dict[name] = cold_start(name,self.config)
    
    def add_to_cold_start_cache(self,article_id,name,stage=None):
        """
        添加到冷启动缓存表中去
        """
        name = name.upper()
        self.add_new_cold_start(name)
        if name != 'GLOBAL':
            stage = None
        self.cold_start_dict[name].add_to_cold_start_cache(article_id,stage)
    
    def is_cold(self,article_id,name,stage=None):
        """
        判断是不是冷启动的文章
        """
        name = name.upper()
        self.add_new_cold_start(name)
        if name != 'GLOBAL':
            stage = None
        return self.cold_start_dict[name].is_cold(article_id,stage)
    
    def update_cold_start_item(self,article_id,name,stage=None):
        """
        更新到冷启动的缓存里面
        """
        name = name.upper()
        self.add_new_cold_start(name)
        if name != 'GLOBAL':
            stage = None
        self.cold_start_dict[name].update_cold_start_item(article_id,stage)
        
    def update_cold_start(self,name,stage=None):
        """
        全部更新冷启动
        """
        name = name.upper()
        self.add_new_cold_start(name)
        if name != 'GLOBAL':
            stage = None
        self.cold_start_dict[name].update_cold_start(stage)
    
    def get_cold_start_articles(self,article_no,name,stage=None):
        """
        获得需要推荐的文章
        """
        name = name.upper()
        self.add_new_cold_start(name)
        if name != 'GLOBAL':
            stage = None
        return self.cold_start_dict[name].get_cold_start_articles(article_no,stage)
       
if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1},
              'hot_article_redis':{'host':'127.0.0.1','port':6379,'db':2},
                'cold_start_redis':{'host':'127.0.0.1','port':6379,'db':3},
            'cold_start_max_no':10,'hot_article_threshold':0.4}

    cs = toutiao_cold_start(config)
   
    print cs.get_cold_start_articles(2,'GLOBAL')