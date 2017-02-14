# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 14:47:18 2017

@author: ligong

@description:这是全部的article类
"""
from hot_article import hot_article
from global_hot_article import global_hot_article

class toutiao_hot_article(object):
    def __init__(self,config):
        self.config = config
        self.hot_article_dict = {}
        self.add_new_hot_article('GLOBAL')

    def add_new_hot_article(self,name):
        """
        添加一个栏目的文章
        """
        name = name.upper()
        if name in self.hot_article_dict:
            return '%s already in!' % name
        #判断是不是全局的
        if name == 'GLOBAL':
            self.hot_article_dict[name] = global_hot_article(self.config)
        else:
            self.hot_article_dict[name] = hot_article(name,self.config)
    
    def is_hot(self,article_id,stage=None,name=None):
        """
        判断是不是热帖
        """
        if name == None:
            name = 'GLOBAL'
        name = name.upper()
        if name == 'GLOBAL':
            return self.hot_article_dict[name].is_hot(article_id,stage)
        else:
            return self.hot_article_dict[name].is_hot(article_id)
        
    def update_score(self,article_id,stage=None,name=None):
        """
        更新文章分数
        """
        self.hot_article_dict['GLOBAL'].update_stage_score(article_id,stage)
        if name != None and name != 'GLOBAL':
            name = name.upper()
            self.add_new_hot_article(name)
            self.hot_article_dict[name].update_score(article_id)
    
    def remove_not_hot(self,stage,max_num=5000,name=None):
        """
        把不那么热的帖子删掉
        """
        self.hot_article_dict['GLOBAL'].remove_not_hot(stage,max_num)
        
        if name != None and name.upper() != 'GLOBAL':
            name = name.upper()
            self.add_new_hot_article(name)
            self.hot_article_dict[name].remove_not_hot(max_num)
        
    def get_hot_articles(self,out_num,stage=None,name=None):
        """
        获得hot articles
        """
        if name == None or name == 'GLOBAL':
            if stage == None:
                return self.hot_article_dict['GLOBAL'].get_hot_articles(out_num)
            else:
                return self.hot_article_dict['GLOBAL'].get_stage_hot_articles(out_num,stage)
        else:
            name = name.upper()
            self.add_new_hot_article(name)
            return self.hot_article_dict[name].get_hot_articles(out_num)

if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1},
              'hot_article_redis':{'host':'127.0.0.1','port':6379,'db':2}}
    tai = toutiao_hot_article(config)
    tai.add_new_hot_article('test_1')
    tai.add_new_hot_article('test_2')
    import time
    
    for i in range(10):
        tai.update_score(i,'stage_1','test_1')
        tai.update_score(i,'stage_1','test_2')
    
    print tai.is_hot(10)
    print tai.is_hot(10,'stage_1')
    print tai.is_hot(10,name = 'test_1')
        
        