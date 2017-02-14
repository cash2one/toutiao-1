# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 17:19:28 2017

@author: ligong

@description:这是spider的interface，所有的爬虫都要实现这些interface
"""

from zope.interface import Interface

class ProtoSpider(Interface):
    def download_detail(name,url,kw=None):
        """
        下载详情页面的信息
        name:爬虫的名字
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g. 
        {'name':`爬虫名字`,'text':`文本`,'title':`标题`,'crawl_time':`下载时间`
        'image':`图像列表`,'source':`来源`,'time':`文章时间`}
        """
    
    def download_list(name,url,kw=None):
        """
        name:爬虫的名字
        下载详情页面的信息
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g.{'details':`详情页地址列表`,'next':`下一页地址`}
        """
    def download_navigation(name,url,kw=None):
        """
        下载导航页面的信息
        name:爬虫的名字
        url:需要下载的地址
        kw:其他可能需要的参数
        return:返回字典格式
        e.g. 
        {'name':`爬虫名字`,'list':`各个列表页的链接列表`}
        """
    def is_implemented():
        """
        是否实现了该接口
        """

