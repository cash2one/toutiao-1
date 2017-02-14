# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 16:49:41 2017

@author: ligong
"""
from default_feed import default_feed
class default_feed_processor:
    DEFAULT_FEED = None
    __INIT__ = False
    
    @staticmethod
    def process(signal_id,config,usid,article_no,column=None,stages=None,kw=None):
        """
        处理请求
        """
        #初始化
        if default_feed_processor.__INIT__ == False:
            default_feed_processor.DEFAULT_FEED = default_feed(config)
            default_feed_processor.__INIT__ = True
        return default_feed_processor.DEFAULT_FEED.get_articles(usid,article_no,column,stages)