# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 13:34:29 2017

@author: ligong

@description:这个获得用户最近阅读文章的信息的程序
"""
from util import init_mongo
import pymongo

class user_view_history(object):
    def __init__(self,config):
        self.config = config
        
        #用户阅读的mongo
        user_view_mongo = config['user_view_mongo']
        self.user_view_mongo_conn = init_mongo(user_view_mongo['host'])
        self.user_view_db = user_view_mongo['db']
        self.user_view_table = user_view_mongo['table']
   

    def get_user_view_history(self,usid,read_no):
        """
        获得用户阅读的历史信息
        """
        result = []
        
        #获得用户最近阅读的若干个文章
        for item in self.user_view_mongo_conn[self.user_view_db][self.user_view_table].find({'usid':usid}).sort([('view_time',pymongo.DESCENDING)]).limit(read_no):
            result.append(item['article_id'])
        return result
        