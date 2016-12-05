# _*_ coding:utf-8 _*_

import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='192.168.1.180'))
channel = connection.channel()

channel.queue_declare(queue='flow', durable=True)
print ' [*] Waiting for messages. To exit press CTRL+C'


def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    print " [x] Done"
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='flow')

channel.start_consuming()