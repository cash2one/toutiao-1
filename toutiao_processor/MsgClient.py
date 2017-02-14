# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 17:21:06 2017

@author: ligong

@description:这是将下载好的数据放到消息队列中去
"""
import pika
import json
class MsgClient(object):
    def __init__(self,mq_addr):
        #初始化消息队列
        self.connection = pika.BlockingConnection(pika.URLParameters(mq_addr))
        self.channel = self.connection.channel()
        self.queue_name = ''
        
    def add_to_mq(self,queue_name,msg):
        """
        添加到mq中
        """
        message = {'data':msg}
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_publish(exchange='',routing_key=queue_name,body=json.dumps(message))
    
    def get_from_mq(self,queue_name):
        """
        从mq中获得数据
        """
        self.channel.queue_declare(queue=queue_name)
        method,properties,body = self.channel.basic_get(queue=queue_name)
        if method:
            self.channel.basic_ack(method.delivery_tag)
            return json.loads(body)['data']
        return None

if __name__ == '__main__':
    mc = MsgClient('ampq://127.0.0.1:5672')
    mc.add_to_mq('test',{'a':1})
    print mc.get_from_mq('test')
