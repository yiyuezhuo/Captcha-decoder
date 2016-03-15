# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 13:17:16 2016

@author: yiyuezhuo
"""
import os    
from PIL import Image
import numpy as np
import pickle
import random

from UI_model import PD_Model


class Tag(object):
    def __init__(self,pdd,tag_path,base_size,cache_name='tag_cache'):
        self.pdd=pdd
        self.tag_path=tag_path
        self.base_size=base_size
        self.cache_name=cache_name
    def flow(self):
        id_to_path=pdd.id_to_path
        base_size=self.base_size
        tag_path=self.tag_path
        
        df=pdd.read()
        
        for iid,record in df.iterrows():
            if record['value']!='!':
                try:
                    if not os.path.exists(tag_path+'/'+record['value']):
                        os.mkdir(tag_path+'/'+record['value'].encode('utf8'))
                    #f=open(id_to_path(str(record['id'])),'rb')
                    im=Image.open(id_to_path(str(record['id'])))
                    im=im.resize(base_size)
                    im.save(os.path.join(tag_path,record['value'],str(record['id'])+'.png'))
                except :
                    print 'skip',record['id']
    def get_dict(self):
        tag_path=self.tag_path
        
        rd={}
        for key in os.listdir(tag_path):
            im_l=[]
            for name in os.listdir(os.path.join(tag_path,key)):
                f=open(os.path.join(tag_path,key,name),'rb')
                im=Image.open(f)
                im_l.append(np.array(im))
                f.close()
            rd[key]=im_l
        return rd
    def dump(self):
        rd=self.get_dict()
        f=open(self.cache_name,'wb')
        pickle.dump(rd,f)
        f.close()
    def load(self):
        f=open(self.cache_name,'rb')
        obj=pickle.load(f)
        f.close()
        return obj


        
class Database(object):
    def __init__(self,tag):
        self.cache_path=tag.cache_name
        self.data=None
        self.tag=tag
    def load(self):
        self.data=self.tag.load()
    def code(self):
        id_to_key={}
        key_to_id={}
        for index,key in enumerate(self.data.keys()):
            key_to_id[key]=index
            id_to_key[index]=key
        self.id_to_key=id_to_key
        self.key_to_id=key_to_id
    def select(self,test_percent=0.1):
        self.load()
        self.code()
        X=[]
        y=[]
        for char,mat_list in self.data.items():
            for mat in mat_list:
                X.append(mat)
                y.append(self.key_to_id[char])
        data=zip(X,y)
        random.shuffle(data)
        wall=int(len(data)*test_percent)
        test_data,train_data=data[:wall],data[wall:]
        X_train,y_train=zip(*train_data)
        X_test,y_test=zip(*test_data)
        X_train=map(lambda x:[x],X_train)
        X_test=map(lambda x:[x],X_test)
        X_train,y_train,X_test,y_test=map(np.array,(X_train,y_train,X_test,y_test))
        return (X_train,y_train),(X_test,y_test)


pdd=PD_Model('crop_map.db','crop','.png')
tag=Tag(pdd,'tag',(30,49))
db=Database(tag)