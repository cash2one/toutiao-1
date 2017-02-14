# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 16:49:41 2017

@author: ligong

@description:这是其他feed的处理类
主要是用来做测试用的
"""
class other_feed_processor:
    DEFAULT_FEED = None
    __INIT__ = False
    
    @staticmethod
    def process(signal_id,config,usid,article_no,column=None,stages=None,kw=None):
        """
        处理请求
        """
        request_addr = kw
        #通过该地址去请求，获得结果
        return None