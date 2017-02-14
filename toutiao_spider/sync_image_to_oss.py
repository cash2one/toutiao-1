# -*- coding: utf-8 -*-
"""
Created on Tue Feb 07 11:35:52 2017

@author: ligong

@description:这是用来将图片同步到阿里云oss中去的程序
"""
import oss2
import os
import traceback
import time
from util import load_config
class SyncImg(object):
    def __init__(self,config):
        """
        初始化配置
        """
        access_key_id = config['access_key_id']
        access_key_secret = config['access_key_secret']
        bucket_name = config['bucket_name']
        endpoint = config['endpoint']
        #文件路径的配置
        self.toutiao_oss_image_path = config['oss_img_path']
        self.toutiao_local_image_path = config['image_path']

        #判断是否存在bucket_name
        auth = oss2.Auth(access_key_id, access_key_secret)
        service = oss2.Service(auth, endpoint)
        exists_bucket_name = False
        for info in oss2.BucketIterator(service):
            if info.name == bucket_name:
                exists_bucket_name = True
                break
        if not exists_bucket_name:
            #创建一个
            bucket = oss2.Bucket(auth, endpoint, bucket_name)
            bucket.create_bucket(oss2.BUCKET_ACL_PUBLIC_READ)
        self.bucket = oss2.Bucket(auth,endpoint,bucket_name)
    
    def process(self):
        """
        将文件上传到oss上去
        """
        while True:
            try:
                total_files = []
                
                for home,dirs,files in os.walk(self.toutiao_local_image_path):
                    for filename in files:
                        total_files.append((os.path.join(home,filename),filename))
                for (full_f,f) in total_files:
                    try:
                        #上传文件然后把本地的文件删除
                        key = self.toutiao_oss_image_path+'/'+f
                        self.bucket.put_object_from_file(key,full_f)
                        os.remove(full_f)
                        print 'http://mmb-toutiao.oss-cn-shanghai.aliyuncs.com/toutiaoImage/%s' % f
                    except:
                        print full_f
                time.sleep(60)
            except:
               traceback.print_exc()
    
    def test_one(self,image_name):
        """
        测试将文件上传到oss上去
        """
        key = self.toutiao_oss_image_path+'/'+image_name
        self.bucket.put_object_from_file(key,self.toutiao_local_image_path+'/'+image_name)
   
    def delete_files(self):
        """
        删除文件
        """
        for obj in oss2.ObjectIterator(self.bucket):
            if not obj.is_prefix():
                print obj.key
                self.bucket.delete_object(obj.key)

if __name__ == '__main__':
    config = load_config('/home/toutiao/config/webspider.json')
    sync_img = SyncImg(config)
    #sync_img.delete_files()
    sync_img.process()
