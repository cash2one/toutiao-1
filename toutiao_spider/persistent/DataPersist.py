# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 10:20:37 2017

@author: ligong

@description:这是将爬虫下载的数据写到数据库或磁盘中去的程序
"""

from util import init_redis,init_mongo,md5

class DataPersist(object):
    def __init__(self,config):
        self.config = config
        
        self.redis_key_ok = 'FINISH_DOWNLOAD'
        self.redis_key_error = 'FAIL_DOWNLOAD'
        self.redis_key_mq = 'ADDED_TO_MQ_%s'

        #数据库保存的db和table
        self.artical_db,self.artical_table = config['artical']['db'],config['artical']['table']
        self.image_db,self.image_table = config['image']['db'],config['image']['table']
        
        finish_redis = config['finish_redis']
        #创建redis链接
        self.redis_conn = init_redis(finish_redis['host'],finish_redis['port'],finish_redis['db'])

        data_address = config['toutiao_mongo']
        #创建mongo链接
        self.data_conn = init_mongo(data_address['host'])
    
    def is_need_to_download(self,url):
        """
        判断是否需要下载
        """
        return not (self.redis_conn.sismember(self.redis_key_ok,url) or self.redis_conn.sismember(self.redis_key_error,url))
    
    def is_need_to_add_to_mq(self,iter_num,url):
        """
        判断是否要添加到队列中去
        """
        key = self.redis_key_mq % iter_num
        return not self.redis_conn.sismember(key,url)
    
    def add_to_mq_redis(self,iter_num,url):
        """
        添加到mq的缓存里面
        """
        key = self.redis_key_mq % iter_num
        self.redis_conn.sadd(key,url)
        
    def dele_mq_redis(self,iter_num):
        """
        删除旧的缓存
        """
        key = self.redis_key_mq % iter_num
        self.redis_conn.expire(key,1000)

    def is_need_to_download_ok(self,url):
        return not (self.redis_conn.sismember(self.redis_key_ok,url))
        
    def is_need_to_download_fail(self,url):
        return not (self.redis_conn.sismember(self.redis_key_error,url)) 
    
    def add_to_redis(self,url,status = True):
        """
        添加到redis
        """
        if status:
            self.redis_conn.sadd(self.redis_key_ok,url)
        else:
            self.redis_conn.sadd(self.redis_key_error,url)
    
    def add_artical_to_mongo(self,url,data):
        """
        保存到数据库
        """
        data.update({'_id':md5(url)})
        self.data_conn[self.artical_db][self.artical_table].save(data)
        self.add_to_redis(url)
    
    def add_image_to_mongo(self,url,image_id,image_name):
        """
        保存到数据库
        """
        item = {'_id':image_id,'name':image_name,'url':url}
        self.data_conn[self.image_db][self.image_table].save(item)
        self.add_to_redis(url)
    
