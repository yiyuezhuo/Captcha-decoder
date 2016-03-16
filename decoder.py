# -*- coding: utf-8 -*-
"""
Created on Thu Mar 03 22:12:23 2016

@author: yiyuezhuo
"""
from PIL import Image
import IPython.display
#from IPython.display import Image 
# This let IPthon can display Image object inline
import requests
import os
import matplotlib.pyplot as plt
import collections
import pytesseract


url='http://202.115.193.41:8080/kaptcha/goldlib'

def data_get(limit=10000,root='data'):
    if not(os.path.isdir(root)):
        os.mkdir(root)
    eid=[int(name[:-4]) for name in os.listdir(root)]
    if len(eid)==0:
        start=0
    else:
        start=max(eid)
    for i in range(start,start+limit):
        res=requests.get(url)
        name=str(i)+'.jpg'
        f=open(root+'/'+name,'wb')
        f.write(res.content)
        f.close()
        print 'download',name
def hist(im,count=None,return_xl=False):
    if count==None:
        count=sum
    x_size,y_size=im.size
    xl=[]
    for x in range(x_size):
        s=0.0
        for y in range(y_size):
            s+=count(im.getpixel((x,y)))
        xl.append(s)
    if not(return_xl):
        plt.plot(xl)
        plt.show()
    else:
        return xl
def hist_T(im,count=None,return_xl=False):
    x_size,y_size=im.size
    yd={y:0 for y in range(y_size)}
    for x,y,pixel in im_iter_xy(im):
        yd[y]+=count(pixel)
    yl=[yd[i] for i in range(y_size)]
    if not(return_xl):
        plt.plot(yl)
        plt.show()
    else:
        return yl
        
    
def file_iter(root='data',itermax=None):
    i=0
    for name in os.listdir(root):
        path=root+'/'+name
        im=Image.open(path).copy()
        yield im
        i+=1
        if i>itermax:
            raise StopIteration
        
        
def im_iter(im):
    x_size,y_size=im.size
    for x in range(x_size):
        for y in range(y_size):
            yield im.getpixel((x,y))
def im_iter_xy(im):
    x_size,y_size=im.size
    for x in range(x_size):
        for y in range(y_size):
            yield x,y,im.getpixel((x,y))

def spectral(im,most_common=None):
    counter=collections.Counter(im_iter(im))
    if most_common==None:
        return counter
    else:
        return counter.most_common(most_common)
        
def grid_nei(x,y,x_size,y_size,mode='four'):
    if mode=='four':
        rl=[]
        if x>0:
            rl.append((x-1,y))
        if x<x_size-1:
            rl.append((x+1,y))
        if y>0:
            rl.append((x,y-1))
        if y<y_size-1:
            rl.append((x,y+1))
        return rl
    
def clean(im,border=255):
    im=im.convert('1')
    rim=im.copy()
    x_size,y_size=im.size
    for x in range(0,x_size):
        for y in range(0,y_size):
            p=sum([im.getpixel((ix,iy)) for ix,iy in grid_nei(x,y,x_size,y_size)])
            if p<=1:
                rim.putpixel((x,y),0)
            else:
                rim.putpixel((x,y),255)
    return rim
    
def get_white_block(im,white_value=255):
    xl=hist(im,count=lambda x:x,return_xl=True)
    x_size,y_size=im.size
    block_l=[]
    in_block=False
    left=0
    block_label=white_value*y_size
    for x in range(len(xl)):
        if in_block:
            if xl[x]!=block_label:
                block_l.append((left,x))
                in_block=False
        else:
            if xl[x]==block_label:
                in_block=True
                left=x
    return block_l
    
def convert(im,cut=150,top=255,low=0):
    im1=im.convert('1')
    x_size,y_size=im.size
    for x,y,pixel in im_iter_xy(im):
        mean=sum(pixel)/len(pixel)
        if mean>150:
            im1.putpixel((x,y),top)
        else:
            im1.putpixel((x,y),low)
    return im1
def get_critic(im):
    xl=hist(im,count=lambda x:x,return_xl=True)
    cl=[]
    vl=[]
    for i in range(2,len(xl)-2):
        #if xl[i-2]<xl[i] and xl[i-1]<xl[i] and xl[i+1]>xl[i] and xl[i+2]>xl[i]:
        if xl[i-1]<=xl[i] and xl[i+1]>=xl[i]:
            cl.append(i)
            vl.append(xl[i])
    return zip(cl,vl)
def get_cut(im,protect=15,point=8):
    cll=get_critic(im)
    cll.sort(key=lambda x:x[1],reverse=True)
    wl=[]
    for index,value in cll:
        if len(wl)==point:
            return wl
        if len(wl)==0:
            wl.append(index)
        elif min(map(lambda loc:abs(index-loc),wl))>protect:
            wl.append(index)
    raise Exception('cl exshaust')
def show_cut(im,cll):
    x_size,y_size=im.size
    cll.sort()
    for i in range(len(cll)-1):
        plt.imshow(im.crop((cll[i],0,cll[i+1],y_size-1)))
        plt.show()
def save_cut(im,protect=15,point=8):
    im=convert(im)
    cll=get_cut(im,protect=protect,point=point)
    x_size,y_size=im.size
    cll.sort()
    for i in range(len(cll)-1):
        sim=im.crop((cll[i],0,cll[i+1],y_size-1))
        if len(os.listdir('crop'))!=0:
            wid=max([int(name.split('.')[0]) for name in os.listdir('crop')])
        else:
            wid=0
        sim.save('crop/'+str(wid+1)+'.png')
def save_cut_all(bind_path='crop/'):
    for im in file_iter(itermax=1000):
        save_cut(im)

def decode_cut(im,cll):
    x_size,y_size=im.size
    cll.sort()
    for i in range(len(cll)-1):
        #plt.imshow(im.crop((cll[i],0,cll[i+1],y_size-1)))
        #plt.show()
        r=pytesseract.image_to_string(im.crop((cll[i],0,cll[i+1],y_size-1)),'eng')
        print r
def test(itermax,f=None):
    miss=0
    if f==None:
        f=decode_cut
    for im in file_iter(itermax=itermax):
        try:
            im1=convert(im)
            f(im1,get_cut(im1))
        except Exception:
            miss+=1
            print 'miss'
    print 'miss',miss
    
def section_likehood(im1,left1,right1,im2,left2,right2,method='diff'):
    im1s=hist(im1,count=lambda x:x,return_xl=True)
    im2s=hist(im2,count=lambda x:x,return_xl=True)
    sec1=im1s[left1:right1]
    sec2=im2s[left2:right2]
    if method=='diff':
        sec1=[sec1[i+1]-sec1[i] for i in range(len(sec1)-1)]
        sec2=[sec2[i+1]-sec2[i] for i in range(len(sec2)-1)]
    r=sum([abs(sec1[i]-sec2[i]) for i in range(len(sec1))])
    return r

def section_likehood_image(im1,left1,right1,im2):
    x_size,y_size=im2.size
    rl=[]
    for x in range(x_size-(right1-left1)):
        left2=x
        right2=x+right1-left1
        r=section_likehood(im1,left1,right1,im2,left2,right2)
        rl.append(r)
    return rl
        
'''
sweet=Image.open('141.png')
im=Image.open('0.jpg')
im0=im
im1=Image.open('data/1.jpg')
im2=Image.open('data/2.jpg')
im3=Image.open('data/3.jpg')

im=im.convert('1')
'''