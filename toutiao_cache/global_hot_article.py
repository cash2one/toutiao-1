# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 09:16:03 2017

@author: ligong

@description:这是hot article的
"""
import time
from hot_article import hot_article
from util import gen_score


class global_hot_article(hot_article):
    def __init__(self,config):
        """
        name:对应的名字
        """
        super(global_hot_article,self).__init__('global',config)
        
        #article的点击率
        self.ratio_stage_prefix = 'ARTICLE_RATIO_%s_%s_%s'
        
        #article的score
        self.hot_stage_article_prefix = 'HOT_ARTICLE_SCORE_%s_%s'
        
    def gen_stage_hot_score(self,article_id,stage):
        """
        获得分数
        """
        create_time = self.article_info_redis_conn.hget(self.article_info_prefix % article_id,'create_time')
        read_ratio = self.article_info_redis_conn.get(self.ratio_stage_prefix % (self.name,stage,article_id))
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
    
    def is_hot(self,article_id,stage=None):
        """
        判断是不是热帖
        """
        if stage != None:
            score = self.hot_article_redis.zscore(self.hot_stage_article_prefix % (stage,self.name),article_id)
            if score == None:
                return False
            else:
                return True
        else:
            return super(global_hot_article,self).is_hot(article_id)
            
    def update_stage_score(self,article_id,stage=None):
        """
        更新hot文章的分数
        """
        
        #添加到zset中去
        if stage != None:
            score = self.gen_stage_hot_score(article_id,stage)
            self.hot_article_redis.zadd(self.hot_stage_article_prefix % (stage,self.name),article_id,score)
        super(global_hot_article,self).update_score(article_id)
        
    def remove_not_hot(self,stage,max_num=5000):
        """
        把不那么热的帖子删掉
        """
        if stage != None:
            self.hot_article_redis.zremrangebyrank(self.hot_stage_article_prefix % (stage,self.name),max_num,-1)
        super(global_hot_article,self).remove_not_hot(max_num)
        
    def get_stage_hot_articles(self,out_num,stage):
        """
        获得hot articles
        """
        #获得数据长度
        key = self.hot_stage_article_prefix % (stage,self.name)
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
    hat = global_hot_article(config)
    print hat.is_hot(9,'stage_1')
        

