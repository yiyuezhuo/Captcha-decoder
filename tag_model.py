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


class StandardImage(object):
    def __init__(self,base_size):
        self.base_size=base_size
    def to_array(self,im):
        return np.array(im)
    def to_standard(self,im):
        return im.resize(self.base_size)
    def to_standard_f(self,source_path,target_path):        
        im=Image.open(source_path)
        im=self.to_standard(im)
        im.save(target_path)
        

class Tag(object):
    def __init__(self,pdd,tag_path,standard_image=None,base_size=None,cache_name='tag_cache'):
        self.pdd=pdd
        self.tag_path=tag_path
        if not(standard_image) and base_size:
            self.standard_image=StandardImage(base_size)
        else:
            self.standard_image=standard_image
        #self.base_size=base_size
        self.cache_name=cache_name
    def standardise(self,im):
        return im.resize(self.base_size)
    def flow(self):
        id_to_path=pdd.id_to_path
        #base_size=self.base_size
        tag_path=self.tag_path
        
        df=pdd.read()
        
        for iid,record in df.iterrows():
            if record['value']!='!':
                try:
                    if not os.path.exists(tag_path+'/'+record['value']):
                        os.mkdir(tag_path+'/'+record['value'].encode('utf8'))
                    #f=open(id_to_path(str(record['id'])),'rb')
                    #im=Image.open(id_to_path(str(record['id'])))
                    #im=self.standerd_image.to_standard(im)
                    #im.save(os.path.join(tag_path,record['value'],str(record['id'])+'.png'))
                    source_path=id_to_path(str(record['id']))
                    target_path=os.path.join(tag_path,record['value'],str(record['id'])+'.png')
                    self.standerd_image.to_standard_f(source_path,target_path)
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
                #im_l.append(np.array(im))
                im_l.append(self.standerd_image.to_array(im))
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
    def to_categorical(self,y,nb_classes=None):
        y = np.asarray(y, dtype='int32')
        if nb_classes==None:
            nb_classes=max(self.id_to_key.keys())+1
        Y = np.zeros((len(y), nb_classes))
        for i in range(len(y)):
            Y[i, y[i]] = 1.
        return Y

    def select(self,test_percent=0.1,y_mode='Y'):
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
        if y_mode=='y':
            return (X_train,y_train),(X_test,y_test)
        elif y_mode=='Y':
            Y_train,Y_test=map(self.to_categorical,(y_train,y_test))
            return (X_train,Y_train),(X_test,Y_test)

if __name__=='__main__':
    pdd=PD_Model('crop_map.db','crop','.png')
    standard_image=StandardImage((30,49))
    tag=Tag(pdd,'tag',standard_image=standard_image)
    db=Database(tag)