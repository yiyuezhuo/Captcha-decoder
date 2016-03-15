# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 19:45:30 2016

@author: yiyuezhuo
"""

'''一句话都不说，你们又不高兴'''

from tag_model import Database

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils

batch_size = 32
nb_epoch = 20
data_augmentation = True

img_rows=49
img_cols=30

db=Database()
(X_train, y_train), (X_test, y_test) = db.select()
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

nb_classes = max(max(y_train),max(y_test))+1

Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)



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

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')

model.fit(X_train, Y_train, batch_size=batch_size,
          nb_epoch=nb_epoch, show_accuracy=True,
          validation_data=(X_test, Y_test), shuffle=True)


score = model.evaluate(X_test, Y_test,
                       show_accuracy=True, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])
