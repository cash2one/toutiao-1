# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:48:54 2017

@author: ligong

@description:这是从消息队列中获得用户阅读数据，然后更新对应的数据库（redis和mongo）
"""
import time
import sys
import traceback

sys.path.append('..')
from MsgClient import MsgClient
from toutiao_cache.toutiao_article_info import toutiao_article_info
from toutiao_cache.toutiao_hot_article import toutiao_hot_article

from user_info import user_info
from util import get_baby_stage

class toutiao_view_event_processor(object):
    def __init__(self,config):
        self.config = config
        self.toutiao_article_info = toutiao_article_info(config)
        self.toutiao_hot_article = toutiao_hot_article(config)
        
        self.user_view_queue = config['user_view_queue']
        self.msg_client = MsgClient('mq_address')
        user_info.init(config)

    def process(self):
        max_sleep_time = 60
        now_sleep_time = 1
        #usid,view_time,article_id,column
        #每一个消息至少要包含这几个字段
        while True:
            try:
                result = self.msg_client.get_from_mq(self.user_view_queue)
                if result == None:
                    now_sleep_time += now_sleep_time
                    if now_sleep_time >= max_sleep_time:
                        now_sleep_time = max_sleep_time
                    time.sleep(now_sleep_time)
                    continue
                user_id = result['user_id']
                sid = result['sid']
                article_id = result['article_id']
                column = result['column']
                #生成usid
                if user_id not in ['','0']:
                    usid = 'u^%s' % user_id
                else:
                    usid = 's^%s' % sid
                
                try:
                    babies = user_info.get_user_info(user_id,sid)
                    stages = map(lambda x:get_baby_stage(x),babies)
                except:
                    #traceback.print_exc()
                    stages = [0]


                #一个个阶段遍历，一般只有一个，但不排除多个的
                for stage in stages:
                    #更新阅读信息
                    try:
                        self.toutiao_article_info.update_article_read(article_id,usid,stage,column)
                    except:
                        pass
                    
                    #更新热帖信息
                    try:
                        #判断是不是热帖，是热帖就更新分数
                        if self.toutiao_hot_article.is_hot(article_id,stage,column):
                            self.toutiao_hot_article.update_score(article_id,stage,column)
                    except:
                        pass
                    
                now_sleep_time = 1
            except:
                traceback.print_exc()
        

