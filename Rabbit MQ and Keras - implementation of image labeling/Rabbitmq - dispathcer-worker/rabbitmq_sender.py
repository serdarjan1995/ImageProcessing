#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:59:11 2018

@author: sardor
"""

import pika
import sys


#################################################
## RABBITMQ ##
RABBITSERVER = "localhost"
RABBITQUEUE = "image_ids"
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
#################################################

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS,erase_on_connect=True)
parameters = pika.ConnectionParameters(host=RABBITSERVER,credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='image_ids', durable=True)

message = ' '.join(sys.argv[1:]) or "-1"
channel.basic_publish(exchange='',
                      routing_key='image_ids',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r" % message)
connection.close()