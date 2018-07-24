#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 09:32:10 2018

@author: sardor
"""
import sys
import pika
import pymysql
import linecache
import keras
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time
import tensorflow as tf
import requests
from io import BytesIO
from PIL import Image

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
MODEL = "image_ids"
LABEL_ACCURACY = 0.8
#################################################




def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('\n\nEXCEPTION IN ({}, LINE {} "{}"): {}\n'.format(filename, lineno, line.strip(), exc_obj))


### TensorFlow Session
def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)


# whenever message recieved this callback function is called by pika library
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    try:
        sql_select = "SELECT * from " + DB_IMAGE_TABLE + " where id=%d" % (int(body))
#        print(sql_select)
        sql_success = cursor.execute(sql_select)
        if(sql_success==0):
            print('id did not match')
        else:
            record = cursor.fetchone()
#            print(record[1])
            response = requests.get(record[1])
#            print(response)
            if(response.status_code == 200):
                # load image
                image = Image.open(BytesIO(response.content))
                image = np.array(image)
                
                # copy to draw on
#                draw = image.copy()
#                draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)
                
                # preprocess image for network
                image = preprocess_image(image)
                image, scale = resize_image(image)
                
                # process image
                start = time.time()
                boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
                print("processing time: ", time.time() - start)
                
                # correct for image scale
                boxes /= scale
                tags = []
                #"a:2:{i:0;s:5:"HELLO";i:1;s:3:"YES";}"
                # visualize detections
                label_count = 0
                for box, score, label in zip(boxes[0], scores[0], labels[0]):
                    # scores are sorted so we can break
                    if score < LABEL_ACCURACY:
                        break
                        
#                    color = label_color(label)
                    
#                    b = box.astype(int)
#                    draw_box(draw, b, color=color)
                    
                    label_count += 1
                    tags.append(labels_to_names[label])
                    caption = "{} {:.3f}".format(labels_to_names[label], score)
#                    draw_caption(draw, b, caption)
                    print(caption)
                label_in_dc2_format = 'a:'+str(label_count)+':{'
                i = 0
                for tag in tags:
                    label_in_dc2_format += 'i:'+str(i)+';s:'+str(len(tag))+':"'+tag+'";'
                    i += 1
                label_in_dc2_format += '}'
                #show image
#                plt.figure(figsize=(15, 15))
#                plt.axis('off')
#                plt.imshow(draw)
#                plt.show()
                try:
                    sql_update = "UPDATE "+ DB_IMAGE_TABLE + " set tags='%s' where id=%d"\
                                % (label_in_dc2_format, record[0])
                    cursor.execute(sql_update)
                    db.commit()
                    print('Image with id {} labeled and updated in DB'.format(record[0]))
                except:
                    db.rollback()
                    PrintException()
            else:
                print('\n!! Request to {} returned with status code {}\n'.format(record[1],
                                                              response.status_code))
    
    except Exception as err:
        PrintException();
        print ("[Error]: ",repr(err))
    
    
        
        
        
###############################################################################
   ########################MAIN STARTS HERE#################################
    
# use this environment flag to change which GPU to use
#os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# set the modified tf session as backend in keras
keras.backend.tensorflow_backend.set_session(get_session())
# adjust this to point to your downloaded/trained model
# models can be downloaded here: https://github.com/fizyr/keras-retinanet/releases

# load retinanet model
model = models.load_model(MODELPATH, backbone_name='resnet50')

# if the model is not converted to an inference model, use the line below
# see: https://github.com/fizyr/keras-retinanet#converting-a-training-model-to-inference-model
#model = models.load_model(model_path, backbone_name='resnet50', convert=True)

#print(model.summary())

# load label to names mapping for visualization purposes
labels_to_names = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
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





## DB connect
db = pymysql.connect(DBSERVER,DBUSERNAME,DBPASS,DBNAME)
cursor = db.cursor()


#/////////////////////////////////////////////////////////////////////////////
# make connection to RABBITMQ channel
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITSERVER,credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# declare RABBITMQ  queue
channel.queue_declare(queue=RABBITQUEUE, durable=True)

# dont recieve messege while busy
channel.basic_qos(prefetch_count=1)

# tell rabbitmq callback function above should assigned to queue 'hello'
channel.basic_consume(callback, queue=RABBITQUEUE)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()


#sql_select = "SELECT * from otel where ipsrc is NULL \
#                and ipdst=%d and protocol=%d and s_port is NULL and d_port='%d' " \
#                % (ipdst_in_xml,int(ipproto_in_xml),int(d_port_in_xml))
#sql_success = cursor.execute(sql_select)
#
#sql_insert = "INSERT INTO processed_events(cid) VALUES (%d)" % cid
#try: cursor.execute(sql_insert); db.commit();
#except Exception as err: db.rollback();PrintException(); print ("[Error]: unable to write data to blocked_ip table, ",repr(err))

connection.close()
#/////////////////////////////////////////////////////////////////////////////