# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 14:47:18 2017

@author: ligong

@description:这是全部的article类
"""
from article_info import article_info
from global_article_info import global_article_info

class toutiao_article_info(object):
    def __init__(self,config):
        self.config = config
        self.article_info_dict = {}
        self.add_new_article_info('GLOBAL')

    def add_new_article_info(self,name):
        """
        添加一个栏目的文章
        """
        name = name.upper()
        if name in self.article_info_dict:
            return '%s already in!' % name
        #判断是不是全局的
        if name == 'GLOBAL':
            self.article_info_dict[name] = global_article_info(self.config)
        else:
            self.article_info_dict[name] = article_info(name,self.config)
    
    def update_article_info(self,article_id,key,value):
        """
        更新文章信息
        """
        self.article_info_dict['GLOBAL'].update_article_info(article_id,key,value)
    
    def update_article_read(self,article_id,usid,stage=None,name=None):
        """
        更新文章的推送
        """
        self.article_info_dict['GLOBAL'].update_article_read(article_id,usid,stage)
        if name != None:
            name = name.upper()
            self.add_new_article_info(name)
            self.article_info_dict[name].update_article_read(article_id,usid)
    
    def update_article_push(self,article_id,usid,stage=None,name=None):
        """
        更新文章的推送
        """
        self.article_info_dict['GLOBAL'].update_article_push(article_id,usid,stage)
        if name != None:
            name = name.upper()
            self.add_new_article_info(name)
            self.article_info_dict[name].update_article_push(article_id,usid)
    
    def read_ratio(self,article_id,stage=None,name=None):
        """
        点击率
        """
        if name == None:
            if stage == None:
                return self.article_info_dict['GLOBAL'].read_ratio(article_id)
            else:
                return self.article_info_dict['GLOBAL'].read_stage_ratio(article_id,stage)
        else:
            name = name.upper()
            self.add_new_article_info(name)
            return self.article_info_dict[name].read_ratio(article_id)
    
    def push_num(self,article_id,stage=None,name=None):
        """
        点击率
        """
        if name == None:
            if stage == None:
                return self.article_info_dict['GLOBAL'].push_num(article_id)
            else:
                return self.article_info_dict['GLOBAL'].push_stage_num(article_id,stage)
        else:
            name = name.upper()
            self.add_new_article_info(name)
            return self.article_info_dict[name].push_num(article_id)
            
            
if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1}}
    tai = toutiao_article_info(config)
    tai.add_new_article_info('test_1')
    tai.add_new_article_info('test_2')
    import time
    '''
    for i in range(10):
        tai.update_article_push(i,'ligong_%s' % (i%100),'stage_1','test_1')
        tai.update_article_push(i,'ligong_%s' % (i%100),'stage_1','test_2')
        tai.update_article_read(i,'ligong_%s' % (i%100),'stage_1','test_1')
        tai.update_article_read(i,'ligong_%s' % (i%100),'stage_1','test_2')
    '''
    print tai.read_ratio(0)
    print tai.read_ratio(0,'stage_1')
    print tai.read_ratio(0,name = 'test_1')
        
        