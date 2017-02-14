# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:48:54 2017

@author: ligong

@description:这是从消息队列中获得冷启动的文章，添加进去
"""
import time
import sys
import json
import traceback

sys.path.append('..')
from MsgClient import MsgClient
from toutiao_cache.toutiao_article_info import toutiao_article_info
from toutiao_cache.toutiao_cold_start import toutiao_cold_start

class toutiao_cold_start_processor(object):
    def __init__(self,config):
        self.config = config
        
        #初始化
        self.toutiao_article_info = toutiao_article_info(config)
        self.toutiao_cold_start = toutiao_cold_start(config)
        
        self.cold_start_queue = config['cold_start_queue']
        self.msg_client = MsgClient(config['mq_address'])

    def process(self):
        max_sleep_time = 60
        now_sleep_time = 1
        #usid,view_time,article_id,column
        #每一个消息至少要包含这几个字段

        while True:
            try:
                result = self.msg_client.get_from_mq(self.cold_start_queue)
                
                if result == None:
                    now_sleep_time += now_sleep_time
                    if now_sleep_time >= max_sleep_time:
                        now_sleep_time = max_sleep_time
                    time.sleep(now_sleep_time)
                    continue
                article_id = result['article_id']
                column = result.get('column','GLOBAL')
                create_time = result.get('create_time',int(time.time()))
                stages = result.get('stages',[])
                stages.append(None)
                stages = list(set(stages))
                if column == 'None':
                    column = 'GLOBAL'
                if column != 'GLOBAL':
                    stages = [None]
                #一个个阶段遍历，一般只有一个，但不排除多个的
                for stage in stages:
                    #更新阅读信息
                    try:
                        self.toutiao_article_info.update_article_info(article_id,'create_time',create_time)
                        self.toutiao_article_info.update_article_info(article_id,'column',column)
                    except:
                        pass
                    #添加到冷启动表
                    try:
                        self.toutiao_cold_start.add_to_cold_start_cache(article_id,column,stage)
                    except:
                        pass

                now_sleep_time = 1
            except:
                traceback.print_exc()
                
if __name__ == '__main__':
    config_path = r'E:\github\toutiao\toutiao_processor\config.json'
    tcsp = toutiao_cold_start_processor(json.load(open(config_path)))
    tcsp.process()
        

