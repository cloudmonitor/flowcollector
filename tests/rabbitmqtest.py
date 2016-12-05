# _*_ coding:utf-8 _*_

import pika
import sys
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.180'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
for i in range(1000):
    message = ' '.join(sys.argv[1:]) or "Hello World!" + str(i)
    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    print " [x] Sent %r" % (message,)
    time.sleep(1)
connection.close()
