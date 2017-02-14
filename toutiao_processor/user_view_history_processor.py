# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 13:38:15 2017

@author: ligong
@description:这个获得用户最近阅读文章的信息的程序
"""
from util import init_mongo
from MsgClient import MsgClient
import time
import traceback

class user_view_history_processor(object):
    def __init__(self,config):
        self.config = config
        
        #这是从消息队列中获取用户阅读信息
        #然后写到mongo中去
        msg_queue = config['mq_address']
        self.msg_client = MsgClient(msg_queue)
        
        #user view mongo
        user_view_mongo = config['user_view_mongo']
        self.user_view_mongo_conn = init_mongo(user_view_mongo['host'])
        self.user_view_db = user_view_mongo['db']
        self.user_view_table = user_view_mongo['table']
        self.user_view_queue = config['user_view_history_queue']

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
            
                #usid,view_time,article_id,column = result['usid'],result['view_time'],result['article_id'],result['column']
                self.user_view_mongo_conn[self.user_view_db][self.user_view_table].save(result)
                
                now_sleep_time = 1
            except:
                traceback.print_exc()
                

if __name__ == '__main__':
    config = None
    uvhp = user_view_history_processor(config)
    uvhp.process()


