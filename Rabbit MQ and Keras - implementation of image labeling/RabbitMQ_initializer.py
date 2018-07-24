#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:49:21 2018

@author: sardor
"""
import pika

class RABBITMQ_INIT:
    def __init__(self, server, queue, user, password, callback):
        self.server=server
        self.queue=queue
        self.user=user
        self.password=password
        self.callback=callback
        self.connect()
    
    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(host=self.server,credentials=credentials)
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # declare RABBITMQ  queue
        channel.queue_declare(queue=self.queue, durable=True)
        
        # dont recieve message while busy
        channel.basic_qos(prefetch_count=1)
        
        # tell rabbitmq callback function above should assigned to queue 'hello'
        channel.basic_consume(self.callback, queue=self.queue)
        
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
        connection.close()