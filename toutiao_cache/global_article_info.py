# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 13:41:42 2017

@author: ligong

@description:这是全局的article_info类
"""
from article_info import article_info
class global_article_info(article_info):
    def __init__(self,config):
        super(global_article_info,self).__init__('global',config)
        
        #push文章的前缀
        self.push_stage_prefix = 'ARTICLE_PUSH_%s_%s_%s'
        
        #read文章的前缀
        self.read_stage_prefix = 'ARTICLE_READ_%s_%s_%s'
        
        #ratio文章的前缀
        self.ratio_stage_prefix = 'ARTICLE_RATIO_%s_%s_%s'
    
    def update_stage_article_ratio(self,article_id,stage):
        """
        更新文章的点击率
        """
        push_key = self.push_stage_prefix % (self.name,stage,article_id)
        read_key = self.read_stage_prefix % (self.name,stage,article_id)
        
        push_num = self.article_info_redis_conn.pfcount(push_key)
        read_num = self.article_info_redis_conn.pfcount(read_key)
        #有一个值是空，则不做任何（没有值）
        if push_num == None or read_num == None or int(push_num) == 0 or int(read_num) == 0:
            return
        
        ratio_key = self.ratio_stage_prefix % (self.name,stage,article_id)
        self.article_info_redis_conn.set(ratio_key,float(read_num)/float(push_num))
        
        
    def update_article_push(self,article_id,usid,stage=None):
        """
        更新文章的推送
        """
        if stage != None:
            push_key = self.push_stage_prefix % (self.name,stage,article_id)
            self.article_info_redis_conn.pfadd(push_key,usid)
            self.update_stage_article_ratio(article_id,stage)
        
        #更新全局的push值
        super(global_article_info,self).update_article_push(article_id,usid)
    
    def update_article_read(self,article_id,usid,stage=None):
        """
        更新文章的阅读
        """
        if stage != None:
            read_key = self.read_stage_prefix % (self.name,stage,article_id)
            self.article_info_redis_conn.pfadd(read_key,usid)
            self.update_stage_article_ratio(article_id,stage)
        
        #更新全局的read值
        super(global_article_info,self).update_article_read(article_id,usid)
    
    def read_stage_ratio(self,article_id,stage):
        """
        点击率
        """
        ratio_key = self.ratio_stage_prefix % (self.name,stage,article_id)
        ratio = self.article_info_redis_conn.get(ratio_key)
        if ratio:
            return float(ratio)
        return 0
        
    def push_stage_num(self,article_id,stage):
        """
        推荐次数
        """
        push_key = self.push_stage_prefix % (self.name,stage,article_id)
        push_num = self.article_info_redis_conn.get(push_key)
        if push_num:
            return int(push_num)
        return 0
        
if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1}}
    ati = global_article_info(config)
    import time,random
    for i in range(1000):
        t = i
        ati.update_article_info(i,'create_time',int(time.time())-8640*i)
        ati.update_article_push(t,i,1)
        ati.update_article_read(t,i,1)
        