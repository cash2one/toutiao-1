# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 14:48:36 2017

@author: ligong

@description:这是返回用户请求数据的程序，从mongo中获取
"""
from util import init_mongo
import pymongo
import time
from MsgClient import MsgClient

class feeds_mongo(object):
    def __init__(self,config):
        #初始化链接
        self.config = config
        self.feeds_mongo_conn = init_mongo(config['feeds_mongo']['host'])
        self.db = config['feeds_mongo']['db']
        self.table = config['feeds_mongo']['table']
        
        #添加到push的队列中去
        self.msg_client = MsgClient(config['mq_address'])
        self.push_queue = config['push_queue']

    def get_data(self,usid,column,start=0,limit=9):
        """
        从mongo中获取数据
        """
        if column == None:
            column = 'GLOBAL'
        column = column.upper()
        result = []
        for item in self.feeds_mongo_conn[self.db][self.table].find({'usid':usid,'column':column}).sort([('insertTime',pymongo.DESCENDING)]).skip(start).limit(limit):
            #stages = item.get('stages',[-1])
            #stages = map(lambda x:x if x != -1 else None,stages)
            #item.update({'stages':stages})
            del item['_id']
            self.msg_client.add_to_mq(self.push_queue,item)
            #del item['stages']
            result.append(item)
        return result
    
    def insert_data(self,items):
        """
        插入数据
        """
        #self.feeds_mongo_conn[self.db][self.table].remove({})
        for item in items:
            try:
                item.update({'insertTime':time.time()})
                usid = item['usid']
                article_id = item['article_id']
                self.feeds_mongo_conn[self.db][self.table].update({'usid':usid,'article_id':article_id},{'$setOnInsert':item},upsert=True)
            except:
                pass

