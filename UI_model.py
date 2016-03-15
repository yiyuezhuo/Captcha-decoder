# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 22:58:58 2016

@author: yiyuezhuo
"""

import pandas as pd
import sqlite3
import os    


class PD_Model(object):
    def __init__(self,db_path,bind_path,bind_suffix):
        self.db_path=db_path
        self.bind_path=bind_path
        self.bind_suffix=bind_suffix
    def init(self):
        df=pd.DataFrame({'id':[1,2],'value':['!','f']})
        con=sqlite3.connect(self.db_path)
        df.to_sql('map',con)
        con.close()
    def read(self):
        con=sqlite3.connect(self.db_path)
        records=list(con.execute('select id,value from map'))
        ids,values=zip(*records)
        df=pd.DataFrame({'id':ids,'value':values})
        con.close()
        return df
    def append(self,df):
        con=sqlite3.connect(self.db_path)
        df.to_sql('map',con,if_exists='append')
        con.close()
    def id_to_path(self,id):
        return self.bind_path+'/'+str(id)+self.bind_suffix

def App(pdd,PAGE_ITEMS=20):
    from flask import Flask,render_template,request,redirect
    
    CUR_DIR=os.path.realpath(os.path.dirname(__file__))
    
    app = Flask(
        __name__,
        static_folder=os.path.join(CUR_DIR, 'static'),
        template_folder=os.path.join(CUR_DIR, 'templates'))
        
    @app.route('/')
    def index():
        return 'Welcome use flask again'
    
    @app.route('/image')
    def image():
        params=request.args
        #f=open('data/'+params['id']+'.jpg','rb')
        f=open(pdd.id_to_path(params['id']),'rb')
        content=f.read()
        f.close()
        return content
        
    @app.route('/table')
    def table():
        df=pdd.read()
        start=df['id'].max()+1
        return render_template('table.html',ids=range(start,start+PAGE_ITEMS))
        
    @app.route('/rev',methods =['GET','POST'])
    def rev():
        print 'enter rev'
        form=dict(request.form)
        print form
        valid=[{'id':key,'value':value[0]} for key,value in form.items() if len(value[0])!=0]
        
        df=pd.DataFrame(valid)
        print df
        pdd.append(df)
        return redirect('/table')
    
    return app
    #app.run(debug=True)
    
def start_hand_put():
    pdd=PD_Model('map.db','data','.jpg')
    app=App(pdd)
    app.run(debug=True)

def start_crop_put():
    pdd=PD_Model('crop_map.db','crop','.png')
    app=App(pdd)
    app.run(debug=True)

import sys
'''
db_path='crop_map.db'
bind_path='crop'
bind_suffix='.png'
PAGE_ITEMS=20
'''


if __name__=='__main__' and len(sys.argv)>=2:
    if sys.argv[1]=='hand':
        start_hand_put()
    elif sys.argv[1]=='crop':
        start_crop_put()