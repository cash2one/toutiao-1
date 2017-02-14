# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 10:17:04 2016

@author: ligong

@description:这是`聚合页推荐`分发程序
"""
from blinker import signal
import os
import logging
import logging.handlers
import traceback
import json
import random

#import 需要的两个
import processor.default_feed_processor
from processor.default_feed_processor import default_feed_processor

import processor.other_feed_processor
from processor.other_feed_processor import other_feed_processor

from util import get_baby_stage
from user_info import user_info
from user_request_dispatch import user_request_dispatch
from feeds_mongo import feeds_mongo

class user_request_processor(object):
    def __init__(self,work_dir,config_path):
        self.work_dir = work_dir
        self.process_id = os.getpid()
        
        #设置日志记录
        formatter = logging.Formatter(''.join(('[%(lineno)d @ ', str(os.getpid()), '] - %(message)s')))
        self.mylogger = logging.getLogger()
        hdlr = logging.handlers.TimedRotatingFileHandler('%s/log/user_request_processor_%d.log' % (self.work_dir, self.process_id),
                                                         when='D', interval=1, backupCount=7)
        hdlr.setFormatter(formatter)
        self.mylogger.addHandler(hdlr)
        self.mylogger.setLevel(logging.INFO)
        
        #读取配置文件
        #config_path = config_path
        self.config = json.load(open(config_path))
        
        #用户信息缓存加载
        user_info.init(self.config)
        
        #加载用户请求分发类
        self.user_request_dispatcher = user_request_dispatch(self.config)
        
        #读写的mongo
        self.feeds_mongo = feeds_mongo(self.config)
        
        #子模块的配置加载
        dispatch_module_config_file = self.config['user_request_processor']['dispatch_module_config_file']
        self.dispatch_module_config = json.load(open(dispatch_module_config_file))
        
        #记录所有的信号
        self.signals = {}

        #类型
        self.dispatch_type = {}
      
    #添加一个信号
    #process_function:包含module的名字
    #e.g:
    #module:new_user_processor
    #funciton process `是一个字符串`
    def add_signal(self,signal_name,process_function,module,package):
        if signal_name in self.signals:
            print 'Signal:%s already in!' % signal_name
            return False
        
        new_signal = signal(signal_name)
        try:
            #exec 'from %s.%s import %s' % (package,module,module)
            eval('new_signal.connect(%s.%s)' % (module,process_function))
        except:
            #traceback.print_exc()
            pass
        self.signals[signal_name] = new_signal
        return True

    '''
    #写到日志里面去
    def append_to_log(self,usid,length,recommend_type):
        open('%s/data/unsolved_list_%s' %(self.work_dir,time.strftime("%Y%m%d", time.localtime())),'a').write('%s,%s,%s,%s,%s\n' %(recommend_type,user_id,sid,length,int(time.time())))
    '''
    
    #加载用户分类配置
    def load_dispatch_config(self):
        keys = self.dispatch_module_config.keys()
        for k in keys:
            v = self.dispatch_module_config[k]
            tmp_type_id = int(v['type_id'])
            tmp_module = v['module']
            tmp_function = v['function']
            tmp_package = v['package']
            tmp_name = v['name']
            self.dispatch_type[tmp_type_id] = tmp_name
            #print tmp_name,tmp_function,tmp_module,tmp_package
            self.add_signal(tmp_name,tmp_function,tmp_module,tmp_package)

            
    #处理一次请求
    def process_one(self,signal_name,param):
        try:
            if signal_name not in self.signals:
                
                self.mylogger.error('Process_one error: No Such a signal:%s' % signal_name)
                print 'No Such a signal:%s' % signal_name
                return {'success':False,'message':'Not Found!','code':404} 
            
            usid = param['usid']
            stages = param['stages']
            article_no = param.get('limit',9)
            column = param.get('column','GLOBAL')
            request_address = param['request_address']
            kw = {'config':self.config,'usid':usid,'column':column,'stages':stages,'article_no':article_no,'kw':request_address}
            
            result = self.signals[signal_name].send(signal_name,**kw)
            
            return result[0][1]
        except:
            traceback.print_exc()
            self.mylogger.error('process_one catch an exception: %s' % (traceback.format_exc()))
            return {'success':False,'message':'Not Found!','code':404}   
    
    #获得signal id
    def get_dispatch_path_info(self,dispatch_type):
        dispatch_type = str(dispatch_type)
        if 'DEFAULT' == dispatch_type:
            return 0
        else:
            return 1

    #处理刷新
    def process_refresh(self,param):
        user_id = param.get('user_id','')
        sid = param.get('sid','')
        limit = param.get('limit',9)
        column = param.get('column','GLOBAL')
        if user_id in ['','0'] and sid in ['','0']:
            print 'user id and session id are all empty, use default!'
            user_id = ''
            sid = '111111'
        #生成usid
        if user_id not in ['','0']:
            usid = 'u^%s' % user_id
        else:
            usid = 's^%s' % sid
        
        #获取babies的信息
        try:
            babies = user_info.get_user_info(user_id,sid)
            stages = map(lambda x:get_baby_stage(x),babies)
        except:
            #traceback.print_exc()
            stages = []
        stages.append(None)
        stages = list(set(stages))
        
        
        #获得分派的类型
        dispatcher = self.user_request_dispatcher.get_dispatcher(usid)
        signal_id = self.get_dispatch_path_info(dispatcher)
        signal_name = self.dispatch_type.get(signal_id)
        
        myparam = {}
        myparam['stages'] = stages
        myparam['usid'] = usid
        myparam['limit'] = limit
        myparam['request_address'] = dispatcher
        myparam['column'] = column
        result = self.process_one(signal_name,myparam)
        answer = []
        #stages = map(lambda x:x if x != None else -1,stages)
        for r in result:
            answer.append({'usid':usid,'column':column,'article_id':r})
        self.feeds_mongo.insert_data(answer)
        
    def process(self,param):
        """
        处理请求
        """
        
        #是否刷新
        is_refresh = param.get('refresh',0)
        if is_refresh == 1:
            self.process_refresh(param)
            
        user_id = param.get('user_id','')
        sid = param.get('sid','')
        limit = param.get('limit',9)
        start = param.get('start',0)
        column = param.get('column','GLOBAL')
        if user_id in ['','0'] and sid in ['','0']:
            print 'user id and session id are all empty, use default!'
            user_id = ''
            sid = str(random.randint(1,10000000))
        #生成usid
        if user_id not in ['','0']:
            usid = 'u^%s' % user_id
        else:
            usid = 's^%s' % sid
        return self.feeds_mongo.get_data(usid,column,start,limit)
        

if __name__ == '__main__':
    urp = user_request_processor('./','config.json')
    urp.load_dispatch_config()
    t = {'user_id':1,'column':'GLOBAL','limit':10,'refresh':1}
    for item in urp.process(t):
        print item['article_id']


