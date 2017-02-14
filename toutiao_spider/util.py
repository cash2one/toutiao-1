# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 09:51:42 2017

@author: ligong

@description:这是一个爬取网页常用的函数
"""
import hashlib
import json
import urllib2
import urllib
import re
import traceback

def load_config(config_path):
    """
    加载配置路径
    配置都是用json格式的
    """
    data = open(config_path,'r').read()
    config = json.loads(data,encoding='utf8')
    return config
    
#from bs4 import BeautifulSoup
def dele_style(node):
    """
    删除节点和子节点的样式
    """
    if node == None:
        return
    if node.name == 'img':
        keys = node.attrs.keys()
        keys.remove('src')
        for key in keys:
            del node.attrs[key]
    else:
        node.attrs = {}
    for child in node.findChildren():
        dele_style(child)

def md5(src):
    """
    生成md5
    """
    m = hashlib.md5()   
    src = src.encode('utf8','ignore') if isinstance(src,unicode) else src
    m.update(src)   
    return str(m.hexdigest())

def is_md5(src):
    pattern = re.compile('[a-z0-9]{32}')
    q = pattern.findall(src)
    if len(q) == 1 and q[0] == src:
        return True
    return False
    
def modify_tag(node):
    """
    把节点中的所有链接去掉，把所有的img类型的链接找到，并替换
    """
    result = {}
    '''
    if node.name == 'a':
        node.decompose()
    '''
    if node.name == 'img':
        src = node.attrs['src']
        if is_md5(src):
            return result
        else:
            src_md5 = md5(src)
           
            index = src.find('?')
            if index >= 0:
                src = src[:index]
            result.update({src_md5:{'url':src}})
            node.attrs['src'] = src_md5
            return result
    for child in node.findChildren():
        result.update(modify_tag(child))
    return result

def update_image(node,image_dict):
    """
    根据图片是否下载成功，更新图片的src信息，如果图片下载失败，就把这个图片节点去掉
    """
    if node.name == 'script':
        node.decompose()
        return
    if node.name == 'img':
        src = node.attrs['src']
        index = src.find('?')
        if index >= 0:
            src = src[:index]
        #下载成功
        try:
            if image_dict[src]['status'] == 0:
                node.decompose()
                return
        except:
            #traceback.print_exc()
            #print node,image_dict
            return
    
    for child in node.findChildren():
       update_image(child,image_dict)
       
def request_ajax_data(url,data=None,referer=None,encoding='utf8',**headers):
    '''
    发起ajax请求
    '''
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('X-Requested-With','XMLHttpRequest')
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116')
    if referer:
        req.add_header('Referer',referer)
    if headers:
        for k in headers.keys():
            req.add_header(k,headers[k])
    if data:
        params = urllib.urlencode(data)
        response = urllib2.urlopen(req, params)
    else:
        response = urllib2.urlopen(req)
    json_text = response.read()
    json_text = json_text.decode(encoding,'ignore')
    return json.loads(json_text)
