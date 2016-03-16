# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 08:22:23 2016

@author: yiyuezhuo
"""

from decoder import get_cut
from PIL import Image
import numpy as np

def im_cut(im):
    cll=get_cut(im)
    x_size,y_size=im.size
    cll.sort()
    rl=[]
    for i in range(len(cll)-1):
        rl.append(im.crop((cll[i],0,cll[i+1],y_size-1)))
    return rl
    
class GeneralImage(object):
    def __init__(self,im,standard_image,db):
        self.standard_image=standard_image
        self.db=db
        if type(im)==str:
            self.im=Image.open(im)
        else:
            self.im=im
        self.cut_l=im_cut(self.im)
        self.tag=None
        self.array_l=[self.standard_image.to_array(cut) for cut in self.cut_l]
    def adapt(self,array):
        return np.array([[array]])
    def predict(self,model,mode='prob'):
        pl=[model.predict(self.adapt(array)) for array in self.array_l]
        if mode=='prob':
            return pl
        elif mode=='max':
            return [self.db.id_to_key(p.argmax()) for p in pl]


from tag_model import PD_Model,StandardImage,Tag,Database

pdd=PD_Model('crop_map.db','crop','.png')
standard_image=StandardImage((30,49))
tag=Tag(pdd,'tag',standard_image=standard_image)
db=Database(tag)    

from conv2 import Model

mod=Model(tag.select())
model=mod.model
mod.fit(20)

gi=GeneralImage('0.jpg')
print gi.predict(mod)