# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 09:49:30 2017

@author: ligong

@description:这是用来做请求转发的程序
"""
import traceback
from util import init_redis
class user_request_dispatch(object):
    def __init__(self,config):
        host,port,db = config['user_request_dispatch_redis']['host'],config['user_request_dispatch_redis']['port'],config['user_request_dispatch_redis']['db']
        self.user_request_dispatch_conn = init_redis(host,port,db)
        self.user_request_dispatch_key = 'USER_REQUEST_DISPATCH'
    
    def get_dispatcher(self,usid):
        """
        根据usid的末尾【0-9】来分派
        """
        try:
            utype = int(usid[-1])
            dispatch_address = self.user_request_dispatch_conn.hget(self.user_request_dispatch_key,utype)
            if dispatch_address == None:
                return 'DEFAULT'#self.user_request_dispatch_conn.hget(self.user_request_dispatch_key,'DEFAULT')
            return dispatch_address
        except:
            traceback.print_exc()
            return self.user_request_dispatch_conn.hget(self.user_request_dispatch_key,'DEFAULT')
    
if __name__ == '__main__':
    config = {'user_request_dispatch_redis':{'host':'127.0.0.1','port':6379,'db':4}}
    urd = user_request_dispatch(config)
    print urd.get_dispatcher('u_1')
