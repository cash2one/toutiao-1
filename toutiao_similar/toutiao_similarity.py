# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:27:24 2017

@author: ligong

@description:这是获得相似文章的代码
"""
import pymongo
from util import init_mongo

class toutiao_similarity(object):
    def __init__(self,config):
        self.config = config
        self.mongo_conn = init_mongo(config['similarity_mongo']['host'])
        #保存结果用的table,db
        self.mongo_db = config['similarity_mongo']['db']
        self.mongo_table = config['similarity_mongo']['table']

    def get_similarity_articles(self,article_id,similarity_no=10):
        """
        获得相似的文本
        """
        result = []
        article_id = str(article_id)
        for item in self.mongo_conn[self.mongo_db][self.mongo_table].find({'article_pair':article_id}).sort([('score',pymongo.DESCENDING)]).limit(similarity_no):
            try:
                result.extend(item['article_pair'])
            except:
                pass
        result = filter(lambda x:x!=article_id,result)
        return result


if __name__ == '__main__':
    config = {}
    config['similarity_redis'] = {'host':'127.0.0.1','port':6379,'db':4}
    config['similarity_mongo'] = {'host':'127.0.0.1:27017','db':'toutiao','table_for_calcu':'similarty_calcu','table':'similarity_score'}
    config['article_pair_max_cache_no'] = 100000
    config['similarity_thread_no'] = 3
    ts = toutiao_similarity(config)
    print ts.get_similarity_articles(0,10)

