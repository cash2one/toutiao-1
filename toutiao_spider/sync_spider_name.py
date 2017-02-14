# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 18:12:45 2017

@author: ligong

@description:这是同步爬取的网址名字到redis的程序
"""
from persistent.util import init_redis
from util import load_config
def sync_spider_name(config):
    spider_name_redis_info = config['spider_name_redis']
    filename = config['spider_names']
    spider_name_redis = init_redis(spider_name_redis_info['host'],spider_name_redis_info['port'],spider_name_redis_info['db'])
    spider_name_key = 'spider_name_set'
    pipe = spider_name_redis.pipeline()
    
    #获得spider name
    f = open(filename,'r')
    line = f.readline()
    while line:
        try:
            pipe.sadd(spider_name_key,line.strip())
        except:
            pass
        line = f.readline()
    f.close()
    pipe.execute()
    
if __name__ == '__main__':
    config = load_config('/home/toutiao/config/webspider.json')
    sync_spider_name(config)

