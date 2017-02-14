# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 09:16:03 2017

@author: ligong

@description:这是hot article的
"""
from util import init_redis,gen_score
import time

class hot_article(object):
    def __init__(self,name,config):
        """
        name:对应的名字
        """
        self.name = name.upper()
        
        hot_article_redis = config['hot_article_redis']
        host,port,db = hot_article_redis['host'],hot_article_redis['port'],hot_article_redis['db']
        
        #初始化redis链接
        self.hot_article_redis = init_redis(host,port,db)
        
        article_info_redis = config['article_info_redis']
        host,port,db = article_info_redis['host'],article_info_redis['port'],article_info_redis['db']
        
        #初始化文章信息的redis链接
        self.article_info_redis_conn = init_redis(host,port,db)
        
        #article的点击率
        self.ratio_prefix = 'ARTICLE_RATIO_%s_%s'
        
        #article的score
        self.hot_article_prefix = 'HOT_ARTICLE_SCORE_%s'
        
        #article信息
        self.article_info_prefix = 'ARTICLE_INFO_%s'
        
    def gen_hot_score(self,article_id):
        """
        获得分数
        """
        create_time = self.article_info_redis_conn.hget(self.article_info_prefix % article_id,'create_time')
        read_ratio = self.article_info_redis_conn.get(self.ratio_prefix % (self.name,article_id))
        #不存在信息
        if create_time == None or read_ratio == None:
            return 0
        time_length = int(time.time()) - int(create_time)
        
        #计算分数
        ##################################################################
        score = float(read_ratio)/((time_length / 86400 + 1)*(time_length / 86400 + 1))
        #这里可以进一步修改
        ##################################################################
        return score
    
    def is_hot(self,article_id):
        """
        判断是不是热帖
        """
        score = self.hot_article_redis.zscore(self.hot_article_prefix % self.name,article_id)
        if score == None:
            return False
        else:
            return True
        
    def update_score(self,article_id):
        """
        更新hot文章的分数
        """
        
        #添加到zset中去
        score = self.gen_hot_score(article_id)
        self.hot_article_redis.zadd(self.hot_article_prefix % self.name,article_id,score)
    
    def remove_not_hot(self,max_num=5000):
        """
        把不那么热的帖子删掉
        """
        self.hot_article_redis.zremrangebyrank(self.hot_article_prefix % self.name,max_num,-1)
        
    def get_hot_articles(self,out_num):
        """
        获得hot articles
        """
        #获得数据长度
        key = self.hot_article_prefix % self.name
        data_length = self.hot_article_redis.zcard(key)
        #要的数据太多，直接返回
        if out_num >= data_length:
            return list(set(self.hot_article_redis.zrange(key,0,-1)))
        
        result = set()
        while len(result) < out_num:
            try:
                start = gen_score(data_length)
                result.add(self.hot_article_redis.zrange(key,start,start)[0])
            except:
                pass
        return list(result)
        
if __name__ == '__main__':
    config = {'article_info_redis':{'host':'127.0.0.1','port':6379,'db':1},
              'hot_article_redis':{'host':'127.0.0.1','port':6379,'db':2}}
    hat = hot_article('test_2',config)
    print hat.is_hot(10)
        

