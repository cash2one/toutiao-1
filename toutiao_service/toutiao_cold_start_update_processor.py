# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:48:54 2017

@author: ligong

@description:定时更新冷启动数据
"""
import time
import sys
import json
import traceback
sys.path.append('..')
from toutiao_cache.toutiao_cold_start import toutiao_cold_start
from util import init_redis

class toutiao_cold_start_update_processor(object):
    def __init__(self,config):
        self.config = config
        basic_info_redis = config['basic_info_redis']
        self.basic_info_conn = init_redis(basic_info_redis['host'],basic_info_redis['port'],basic_info_redis['db'])
        
        #初始化
        self.toutiao_cold_start = toutiao_cold_start(config)
        
        #获得阶段
        self.stages = map(lambda x:int(x) if int(x) != -1 else None,self.basic_info_conn.smembers('stages'))

        #获得colum
        self.columns = map(lambda x:x.upper(),self.basic_info_conn.smembers('columns'))
        
    def process(self):
        max_sleep_time = 60
        print 'toutiao cold start update processor is running...'
        while True:
            try:
                for column in self.columns:
                    for stage in self.stages:
                        self.toutiao_cold_start.update_cold_start(column,stage)
                time.sleep(max_sleep_time)
            except:
                traceback.print_exc()
                
if __name__ == '__main__':
    config_path = r'E:\github\toutiao\toutiao_processor\config.json'
    tcsp = toutiao_cold_start_update_processor(json.load(open(config_path)))
    tcsp.process()
        

