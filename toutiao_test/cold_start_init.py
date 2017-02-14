# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 11:19:48 2017

@author: ligong

@description:这是模拟冷启动，添加到冷启动队列中去
"""
import time
import json
from MsgClient import MsgClient

def add_to_cold_start_queue(article_limit = 0):
    config = json.load(open(r'E:\github\toutiao\toutiao_processor\config.json'))
    msg_client = MsgClient(config['mq_address'])
    stages = [0,1,2,3]
    column = 'GLOBAL'
    for i in range(article_limit,article_limit+1000):
        t = {'article_id':i,'column':column,'create_time':int(time.time()),'stages':stages}
        msg_client.add_to_mq(config['cold_start_queue'],t)
    
        
if __name__ == '__main__':
    add_to_cold_start_queue()