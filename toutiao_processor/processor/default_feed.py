# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:56:18 2017

@author: ligong

@description:这是获得默认推荐下的所有的文章
包括：冷启动的文章，热帖的文章，相似推荐的文章
"""
import sys
sys.path.append('..')
sys.path.append('../../')

import random
from toutiao_cache.toutiao_hot_article import toutiao_hot_article
from toutiao_cache.toutiao_cold_start import toutiao_cold_start
from toutiao_similar.toutiao_similarity import toutiao_similarity
from user_view_history import user_view_history
from util import gen_score
import traceback

class default_feed(object):
    def __init__(self,config):
        """
        初始化
        """
        self.config = config
        
        #生成需要的类对象
        self.toutiao_similarity = toutiao_similarity(config)
        self.toutiao_cold_start = toutiao_cold_start(config)
        self.toutiao_hot_article = toutiao_hot_article(config)
        self.user_view_history = user_view_history(config)
        
    
    def get_similarity_articles(self,usid,article_no):
        """
        获得文章
        """
        recent_view = self.user_view_history.get_user_view_history(usid,article_no*3)
        result = []
        for article_id in recent_view:
            try:
                result.extend(self.toutiao_similarity.get_similarity_articles(article_id))
            except:
                traceback.print_exc()
        
        #result.sort(key=lambda x:x['score'],reverse=True)
        result = list(set(result))
        length = len(result)
        answer = set()
        
        #如果要的数据太多，则全部返回
        if length <= article_no:
            return result
        
        while len(answer) <= article_no:
            answer.add(result[gen_score(length)])
        return list(answer)
    
    def get_cold_start_articles(self,article_no,column=None,stage=None):
        """
        获得文章
        column:栏目
        stage:对应的阶段
        """
        if column == None:
            column = 'GLOBAL'
        return self.toutiao_cold_start.get_cold_start_articles(article_no,column,stage)
    
    def get_hot_articles(self,article_no,column=None,stage=None):
        """
        获得文章
        column:栏目
        stage:对应的阶段
        """
        if column == None:
            column = 'GLOBAL'
        return self.toutiao_hot_article.get_hot_articles(article_no,stage,column)
    
    def get_articles(self,usid,article_no,column=None,stages=None):
        """
        获得文章
        column:栏目
        stage:对应的阶段
        """
        
        similarity = self.get_similarity_articles(usid,article_no)
        hot = []
        cold = []
        for stage in stages:
            hot.extend(self.get_hot_articles(article_no,column,stage))
            cold.extend(self.get_cold_start_articles(article_no,column,stage))
        
        #print 's',similarity
        #print 'h',hot
        #print 'c',cold
        result = []
        result.extend(similarity)
        result.extend(hot)
        result.extend(cold)
        result = list(result)
        
        length = len(result)
        #随机挑选若干篇
        if article_no >= length:
            return result
        answer = set()
        while len(answer) < article_no:
            answer.add(result[random.randint(0,length-1)])
        return list(answer)
