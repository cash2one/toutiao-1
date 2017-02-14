# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 11:35:04 2017

@author: ligong

@description:获得推荐的数据
"""
import sys
sys.path.append('..')

from toutiao_processor.user_request_processor import user_request_processor

urp = user_request_processor('./',r'E:\github\toutiao\toutiao_processor\config.json')

def get_feeds(user_id,sid,num=10):
    global urp
    t = {'user_id':user_id,'sid':sid,'column':'GLOBAL','limit':num}
    print urp.process(t)
    
if __name__ == '__main__':
    get_feeds(1,1)



