# -*- coding: utf-8 -*-
"""
Created on Wed Feb 08 15:36:26 2017

@author: ligong

@description:这是cache常用的一些函数
"""
import redis
import random
import math
import time

#为了防止redis链接数量太多而设置缓存
global REDIS_CONNS_DICT
REDIS_CONNS_DICT = None

#这是用来算分数的来找热帖的函数
def gen_score(data_length,power = 4):
    """
    data_length:列表总长度
    """
    #random.seed(int(time.time()))
    tmp = random.random()
    score = int((1 - math.pow(tmp,power))*data_length)
    if score == 0:
        return 0
    else:
        return score
        
#初始化redis
def init_redis(host,port,db):
    global REDIS_CONNS_DICT
    
    if REDIS_CONNS_DICT == None:
        REDIS_CONNS_DICT = {}

    key = '%s_%s_%s' % (host,port,db)
    if key in REDIS_CONNS_DICT:
        return REDIS_CONNS_DICT[key]
    pool = redis.ConnectionPool(host=host, port=int(port),db=int(db))
    REDIS_CONNS_DICT[key] = redis.Redis(connection_pool=pool)
    return REDIS_CONNS_DICT[key]
