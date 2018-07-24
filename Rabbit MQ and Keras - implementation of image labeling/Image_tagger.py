#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 11:05:59 2018

@author: sardor
"""

import sys
import pymysql
import linecache
from keras_retinanet.utils.image import preprocess_image, resize_image
import numpy as np
import time
import requests
from io import BytesIO
from PIL import Image
from Keras_initializer import KERAS_INIT
from RabbitMQ_initializer import RABBITMQ_INIT

#################################################
## DATABASE ##
DBSERVER = "localhost"
DBUSERNAME = "root"
DBPASS = "root"
DBNAME = "otel"
DB_IMAGE_TABLE = "image"
#################################################


#################################################
## RABBITMQ ##
RABBITSERVER = "localhost"
RABBITQUEUE = "image_ids"
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
#################################################


#################################################
## RESNET50 MODEL ##
MODELPATH = "resnet50_coco_best_v2.1.0.h5"
MODEL2PATH = "custom_inferenced_model_v2.h5"
LABEL_ACCURACY = 0.8
LABEL2_ACCURACY = 0.9
#################################################

class Image_Tagger:
    def __init__(self):
        keras_models = KERAS_INIT(MODELPATH,model2=MODEL2PATH)
        self.model = keras_models.get_model()
        self.model2 = keras_models.get_model2()
        self.db = pymysql.connect(DBSERVER,DBUSERNAME,DBPASS,DBNAME)
        self.labels_to_names = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle',4: 'airplane',
                   5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
                   10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
                   14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow',
                   20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack',
                   25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
                   30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite',
                   34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard',
                   37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass',
                   41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl',
                   46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
                   51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
                   56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
                   60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse',
                   65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave',
                   69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book',
                   74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear',
                   78: 'hair drier', 79: 'toothbrush'}
        self.labels_to_names2 = {0: 'bloody', 1: 'gun', 2: 'lingerie', 3: 'plaka', 4: 'symbol'}
        RABBITMQ_INIT(RABBITSERVER, RABBITQUEUE, RABBITMQ_USER, RABBITMQ_PASS, self.callback)
    
    
    ### Exception print
    def PrintException():
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('\n\nEXCEPTION IN ({}, LINE {} "{}"): {}\n'.format(filename, lineno, line.strip(), exc_obj))
    
    
    ## callback function for RABBITMQ
    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        self.predict(img_id=body)
    
    
    
    def predict(self, img_id):
        cursor = self.db.cursor()
        try:
            sql_select = "SELECT * from " + DB_IMAGE_TABLE + " where id=%d" % (int(img_id))
            sql_success = cursor.execute(sql_select)
            if(sql_success==0):
                print('[WARNING] id did not found on table')
            else:
                record = cursor.fetchone()
                response = requests.get(record[1]) # url is on second column
                if(response.status_code == 200):  # if url HTTP response is OK
                    # load image
                    image = Image.open(BytesIO(response.content))
                    image = np.array(image)
                    
                    # preprocess image for network
                    image = preprocess_image(image)
                    image, scale = resize_image(image)
                    
                    
                    tags = []
                    label_count = 0
                    
                    
                    # process image from model1
                    start = time.time()
                    boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(image, axis=0))
                    print("processing time for model1: ", time.time() - start)

                    for score, label in zip(scores[0], labels[0]):
                        # scores are sorted so we can break
                        if score < LABEL_ACCURACY:
                            break
                        
                        label_count += 1
                        tags.append(self.labels_to_names[label])
                        caption = "{} {:.3f}".format(self.labels_to_names[label], score)
                        print('Model1 predictions:',caption)
                    
                    
                    # process image from model2
                    if(self.model2):
                        start = time.time()
                        boxes, scores, labels = self.model2.predict_on_batch(np.expand_dims(image, axis=0))
                        print("processing time for model2: ", time.time() - start)
    
                        for score, label in zip(scores[0], labels[0]):
                            # scores are sorted so we can break
                            if score < LABEL_ACCURACY:
                                break
                            
                            label_count += 1
                            tags.append(self.labels_to_names2[label])
                            caption = "{} {:.3f}".format(self.labels_to_names2[label], score)
                            print('Model2 predictions:',caption)
                        
                    ## start making string in format DC2FORMAT{ARRAY}
                    label_in_dc2_format = 'a:'+str(label_count)+':{'
                    i = 0
                    for tag in tags:
                        label_in_dc2_format += 'i:'+str(i)+';s:'+str(len(tag))+':"'+tag+'";'
                        i +=1
                    label_in_dc2_format += '}'
                    try:
                        sql_update = "UPDATE "+ DB_IMAGE_TABLE + " set tags='%s' where id=%d"\
                                    % (label_in_dc2_format, record[0])
                        cursor.execute(sql_update)
                        self.db.commit()
                        if len(tags)>0:
                            print('Image with id {} labeled and updated in DB'.format(record[0]))
                        else:
                            print('Image with id {} has no labels predicted'.format(record[0]))
                    except:
                        self.db.rollback()
                        self.PrintException()
                else:
                    print('\n!! Request to {} returned with status code {}\n'.format(record[1],
                                                  response.status_code))
        except Exception:
            self.PrintException();
            
            
###############################################################################
   ########################MAIN STARTS HERE#################################
if __name__ == '__main__':
    Image_Tagger()