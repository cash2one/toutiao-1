# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:48:54 2017

@author: ligong

@description:这是从消息队列中获得用户push数据
"""
import time
import sys
import traceback
import json

sys.path.append('..')
from MsgClient import MsgClient
from toutiao_cache.toutiao_article_info import toutiao_article_info
from user_info import user_info
from util import get_baby_stage

class toutiao_push_event_processor(object):
    def __init__(self,config):
        self.config = config
        
        #初始化
        self.toutiao_article_info = toutiao_article_info(config)
        self.push_queue = config['push_queue']
        self.msg_client = MsgClient(config['mq_address'])
        user_info.init(config)

    def process(self):
        max_sleep_time = 60
        now_sleep_time = 1
        #usid,view_time,article_id,column
        #每一个消息至少要包含这几个字段
        iter_num = 0
        while True:
            try:
                iter_num += 1
                result = self.msg_client.get_from_mq(self.push_queue)
                
                if result == None:
                    now_sleep_time += now_sleep_time
                    if now_sleep_time >= max_sleep_time:
                        now_sleep_time = max_sleep_time
                    time.sleep(now_sleep_time)
                    continue
                usid = result['usid']
                tmp = usid.split('^')
                if tmp[0] == 'u':
                    user_id = tmp[1]
                    sid = ''
                else:
                    user_id = ''
                    sid = tmp[1]
                article_id = result['article_id']
                column = result.get('column','GLOBAL')
                if column == 'None':
                    column = 'GLOBAL'
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
                    stages = []
                stages = list(set(stages))
                stages.append(None)
    
                #一个个阶段遍历，一般只有一个，但不排除多个的
                for stage in stages:
                    #更新阅读信息
                    try:
                        self.toutiao_article_info.update_article_push(article_id,usid,stage,column)
                    except:
                        pass

                now_sleep_time = 1
            except:
                traceback.print_exc()
        

if __name__ == '__main__':
    config_path = r'E:\github\toutiao\toutiao_processor\config.json'
    tpep = toutiao_push_event_processor(json.load(open(config_path)))
    tpep.process()