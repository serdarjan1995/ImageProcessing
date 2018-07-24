#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 11:43:41 2018

@author: sardor
"""
import keras
from keras_retinanet import models
import tensorflow as tf

class KERAS_INIT:
    def __init__(self,MODELPATH, *args, **kwargs):
        self.start_keras()
        # load retinanet model
        self.model = models.load_model(MODELPATH, backbone_name='resnet50')
        if('model2' in kwargs):
            MODEL2PATH = kwargs.get('model2', None)
            self.model2 = models.load_model(MODEL2PATH, backbone_name='resnet50')
        else:
            self.model2 = None
    def start_keras(self):
        # set the modified tf session as backend in keras
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        keras.backend.tensorflow_backend.set_session(tf.Session(config=config))
        
    def get_model(self):
        return self.model
    
    def get_model2(self):
        return self.model2