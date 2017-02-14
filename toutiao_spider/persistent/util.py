# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 14:06:21 2017

@author: ligong
"""
import redis
import pymongo
import hashlib

#初始化redis
def init_redis(host,port,db):
    pool = redis.ConnectionPool(host=host, port=int(port),db=int(db))
    return redis.Redis(connection_pool=pool)
    
#初始化mongo
def init_mongo(host_and_port):
    return pymongo.MongoClient('mongodb://%s' %(host_and_port))

    
def md5(src):
    """
    生成md5
    """
    m = hashlib.md5()   
    m.update(src)   
    return str(m.hexdigest())
