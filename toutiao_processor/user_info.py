# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 10:50:11 2017

@author: ligong

@description:这是用户信息的获取和更新类
"""
from util import init_mongo,init_redis

class user_info(object):
    CACHE_EXPIRE_DAYS = 1                       #cache的保存时间
    user_list_redis = None                      #链接到用户的redis
    mongo_conn = None                          
    __INIT__ = False                            #是否初始化
    
    @staticmethod
    def init(config):
        if user_info.__INIT__ == False:
            #redis，mongo初始化
            user_info.mongo_conn = init_mongo(config['user_info_mongo']['host'])
            user_info.user_list_redis = init_redis(config['user_info_redis']['host'], config['user_info_redis']['port'],config['user_info_redis']['db'])
            user_info.__INIT__ = True
    
    @staticmethod
    def is_leagl_id(usd_id):
        """
        判断是否是合法id
        """
        if usd_id == None or str(usd_id).strip() in ['','0']:
            return False
        return True
    
    
    #获得用户信息
    @staticmethod
    def get_user_info_from_mongo(user_id):
        if not user_info.is_leagl_id(user_id):
            return None
        #user_info.init()
        item = user_info.mongo_conn['users']['users'].find_one({'_id':int(user_id)})
        if item == None:
            return None
     
        total_babies = set()
        if 'nobaby_flag' in item and item['nobaby_flag'] == 1:
            total_babies.add('nobaby')
        
        babies = item.get('babies',[])
        
        if 'unborn_baby_id' in item:
            unborn_baby_id = item['unborn_baby_id']
            total_babies.add(str(unborn_baby_id))
        for baby in babies:
            if '_id' in baby:
                total_babies.add(baby['_id'])
            if 'birthday' in baby:
                total_babies.add(str(baby['birthday']))
                
        return list(total_babies)
    
    #获得用户信息
    @staticmethod
    def get_session_info_from_mongo(sid):
        if not user_info.is_leagl_id(sid):
            return None
        #user_info.init()
        item = user_info.mongo_conn['users']['sessions'].find_one({'_id':int(sid)})
        if item == None:
            return None
     
        babies = item.get('babies',[])
        total_babies = set()
        for baby in babies:
            if '_id' in baby:
                total_babies.add(baby['_id'])
            if 'birthday' in baby:
                total_babies.add(str(baby['birthday']))
        
        return list(total_babies)
    
    #添加到用户列表中
    @staticmethod
    def add_to_cache(usid,babies):
        if not user_info.is_leagl_id(usid):
            return False,'illegal user_id'
        #user_info.init()
        if user_info.user_list_redis.exists(usid):
            return False,'Already in'
        pipe = user_info.user_list_redis.pipeline()
        #添加到redis中去
        for b in babies:
            pipe.lpush(usid,b)
        pipe.execute()
        
        user_info.user_list_redis.expire(usid,86400*user_info.CACHE_EXPIRE_DAYS)
        return True,'OK'

    #获得用户信息
    @staticmethod
    def get_user_info(user_id,sid):
        #user_info.init()
        if user_info.is_leagl_id(user_id):
            usid = 'u^%s' % user_id
        elif user_info.is_leagl_id(sid):
            usid = 's^%s' % sid
        else:
            return None
        
        #如果redis里没有，就从mong中取，取好后放到redis中
        if user_info.user_list_redis.exists(usid):
            babies = user_info.user_list_redis.lrange(usid,0,-1)
            return babies
        else:
            babies = None
            if usid.startswith('u^'):
                babies = user_info.get_user_info_from_mongo(user_id)
            else:
                babies = user_info.get_session_info_from_mongo(sid)
            if babies != None:
                user_info.add_to_cache(usid,babies)
            return babies

if __name__ == '__main__':
    config = {'user_info_redis':{'host':'127.0.0.1','port':6379,'db':4}}
    user_info.init(config)
    #print user_info.add_to_cache('u^1',['nobaby','201611','201612'])
    print user_info.get_user_info(1,None)
    




