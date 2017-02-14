# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:39:49 2017

@author: ligong

@description:这是维护计算相似度结构的程序
"""
import itertools
import time
import traceback
import math
from util import init_redis,init_mongo

class similarity_cache(object):
    def __init__(self,config):
        """
        初始化
        """
        self.config = config
        similarity_redis = config['similarity_redis']
        host,port,db = similarity_redis['host'],similarity_redis['port'],similarity_redis['db']
        
        #连接到内存的链接        
        self.similarity_redis_conn = init_redis(host,port,db)
        
        #链接到mongo
        self.mongo_conn = init_mongo(config['similarity_mongo']['host'])
        self.mongo_db = config['similarity_mongo']['db']
        
        #计算时候用的table
        self.mongo_table_for_calcu = config['similarity_mongo']['table_for_calcu']
        
        #保存结果用的table
        self.mongo_table = config['similarity_mongo']['table']
        
        #文章两两配对，最大的内存缓存数量
        self.article_pair_max_cache_no = config['article_pair_max_cache_no']
        
        #最近更新时间的zset前缀
        self.lastuse = 'ARTICLE_PAIR_LASTUSE'
        
        #记录每个话题的阅读次数（每个用户算一次，这里不去重，在外部输入的保证去重）
        self.article_view_no ='ARTICLE_VIEW_NO'
        

    def add_to_cache(self,view_data):
        """
        redis只存增量的部分，刷到mongo的时候要加上mongo原来的值
        添加到内存中去，这里是用户N天内的阅读行为
        user_view_data的结构是字典
        1表示正常阅读，-1表示讨厌
        {'article_1':1,'article_2':-1,...}
        """
        keys = view_data.keys()
        
        
        tmp_dict = {}
        for (article_1,article_2) in itertools.permutations(keys, 2):
            try:
                #过滤掉一半
                if article_1 >= article_2:
                    continue
                v = view_data[article_1]*view_data[article_2]
                key = '%s_%s' % (article_1,article_2)
                tmp_dict[key] = tmp_dict.get(key,0)+v
            except:
                pass
        pipe = self.similarity_redis_conn.pipeline()
        
        #更新文章阅读次数
        for article_id in view_data:
            pipe.hincrby(self.article_view_no,article_id,amount=1)
        
        #写到内存
        for (key,v) in tmp_dict.iteritems():
            try:
                pipe.incrby(key,amount=v)
                pipe.zadd(self.lastuse,key,int(time.time()))
            except:
                traceback.print_exc()
        pipe.execute()
        self.check_cache()
    
    def flush_to_mongo(self,key):
        """
        写到mongo中去
        """
        score = int(self.similarity_redis_conn.get(key))
        update_time = self.similarity_redis_conn.zscore(self.lastuse,key)
        self.mongo_conn[self.mongo_db][self.mongo_table_for_calcu].update({'_id':key},{'$set':{'update_time':int(update_time)},'$inc':{'score':score}},upsert = True)
        
        #self.mongo_conn[self.mongo_db][self.mongo_table_for_calcu].save({'_id':key,'score':score,'update_time':int(update_time)})
       
    def load_from_mongo(self,key):
        """
        从mongo中加载
        """
        item = self.mongo_conn[self.mongo_db][self.mongo_table_for_calcu].find_one({'_id':key})
        if item != None and isinstance(item,dict):
            return item['score']
        return 0
            
    def dele_from_cache(self,key):
        """
        从cache中删除
        """
        self.similarity_redis_conn.zrem(self.lastuse,key)
        self.similarity_redis_conn.delete(key)
    
    def check_cache(self):
        """
        检查使用内存是否超标，如果超标就刷到mongo
        """
        if self.similarity_redis_conn.dbsize() >= self.article_pair_max_cache_no:
            #内存使用太大了，就刷到mongo
            for key in self.similarity_redis_conn.zrange(self.lastuse,int(self.article_pair_max_cache_no*0.7),-1):
                self.flush_to_mongo(key)
                self.dele_from_cache(key)
        
    def result_to_db(self):
        """
        将最后的结果写到mongo
        """
        #self.mongo_conn[self.mongo_db][self.mongo_table].remove({})
        #内存到mongo
        for key in self.similarity_redis_conn.zrange(self.lastuse,0,-1):
            self.flush_to_mongo(key)
            #从内存中删除
            self.dele_from_cache(key)
        
        
        #mongo到mongo
        for item in self.mongo_conn[self.mongo_db][self.mongo_table_for_calcu].find():
            try:
                key = item['_id']
                score= item['score']
                article_1,article_2 = key.split('_')
                norm_1 = int(self.similarity_redis_conn.hget(self.article_view_no,article_1))
                norm_2 = int(self.similarity_redis_conn.hget(self.article_view_no,article_2))
                item.update({'score':float(score)/math.sqrt(norm_1*norm_2)})
                item.update({'article_pair':[article_1,article_2]})
                self.mongo_conn[self.mongo_db][self.mongo_table].save(item)
            except:
                pass
        
        #删除计算的mongo中的信息
        self.mongo_conn[self.mongo_db][self.mongo_table_for_calcu].remove({})
        #删除文章阅读次数缓存
        self.similarity_redis_conn.delete(self.article_view_no)
        


if __name__ == '__main__':
    config = {}
    config['similarity_redis'] = {'host':'127.0.0.1','port':6379,'db':4}
    config['similarity_mongo'] = {'host':'127.0.0.1:27017','db':'toutiao','table_for_calcu':'similarty_calcu','table':'similarity_score'}
    config['article_pair_max_cache_no'] = 30

    sc = similarity_cache(config)
    for i in range(10):
        t = {}
        for j in range(9):
            t[j] = 1
        sc.add_to_cache(t)
    sc.result_to_db()