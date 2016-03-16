# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 22:19:08 2016

@author: yiyuezhuo
"""
#from tag_model import Database

from keras.models import Sequential,model_from_json  
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils


class Model(object):
    def __init__(self,data):
        self.setup_data(data)
        self.model=self.setup_model()
    def setup_data(self,data,y_mode='Y'):
        if y_mode=='y':
            (X_train, y_train), (X_test, y_test) = data
            nb_classes = max(max(y_train),max(y_test))+1
            print('nb_classes',nb_classes)
            
            Y_train = np_utils.to_categorical(y_train, nb_classes)
            Y_test = np_utils.to_categorical(y_test, nb_classes)
        elif y_mode=='Y':
            (X_train, Y_train), (X_test, Y_test) = data

        print('X_train shape:', X_train.shape)
        print(X_train.shape[0], 'train samples')
        print(X_test.shape[0], 'test samples')
        
        X_train = X_train.astype('float32')
        X_test = X_test.astype('float32')
        
        img_rows,img_cols=X_train[0][0].shape

        self.X_train=X_train
        self.X_test=X_test
        self.Y_train=Y_train
        self.Y_test=Y_test
        self.img_rows=img_rows
        self.img_cols=img_cols
        self.nb_classes=nb_classes
    def setup_model(self):
        self.batch_size = 32
        #data_augmentation = True
        
        img_rows=self.img_rows
        img_cols=self.img_cols
        nb_classes=self.nb_classes
        
        
        model = Sequential()
        
        model.add(Convolution2D(32, 3, 3, border_mode='same',
                                input_shape=(1,img_rows,img_cols)))
        model.add(Activation('relu'))
        model.add(Convolution2D(32, 3, 3))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        model.add(Convolution2D(64, 3, 3, border_mode='same'))
        model.add(Activation('relu'))
        model.add(Convolution2D(64, 3, 3))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        model.add(Dense(nb_classes))
        model.add(Activation('softmax'))
        
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd)
        
        return model
    def evaluate(self):
        model=self.model
        X_test,Y_test=self.X_test,self.Y_test
        score = model.evaluate(X_test, Y_test,show_accuracy=True, verbose=0)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])
    def fit(self,nb_epoch,**kwargs):
        model=self.model
        X_train,Y_train=self.X_train,self.Y_train
        X_test,Y_test=self.X_test,self.Y_test
        batch_size=self.batch_size
        model.fit(X_train, Y_train, batch_size=batch_size,
          nb_epoch=nb_epoch, show_accuracy=True,
          validation_data=(X_test, Y_test), shuffle=True,**kwargs)
    def predict(self,x):
        # suck interface
        return self.model.predict(x)
    def save(self,fname=None):
        fname=fname if fname else 'mymodel'
        model=self.model
        json_string = model.to_json()
        open(fname+'.json', 'w').write(json_string)
        model.save_weights(fname+'.h5')
    def load(self,fname=None):
        fname=fname if fname else 'mymodel'
        
        model = model_from_json(open(fname+'.json').read())
        model.load_weights(fname+'.h5')
        self.model=model


if __name__=='__main__':
    from tag_model import PD_Model,StandardImage,Tag,Database
    
    pdd=PD_Model('crop_map.db','crop','.png')
    standard_image=StandardImage((30,49))
    tag=Tag(pdd,'tag',standard_image=standard_image)
    db=Database(tag)    
    
    mod=Model(tag.select())
    model=mod.model
    mod.fit(20)
