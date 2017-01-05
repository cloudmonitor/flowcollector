# _*_ coding:utf-8 _*_


import pika
from multiprocessing import Process, current_process
from settings import *
from mongodbconn import MongoHelper


class FlowStorge(Process):
    """存储流数据到数据库"""
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.180'))
    conn = MongoHelper(FLOWDB_CONN).getconn()

    def __init__(self):
        super(FlowStorge, self).__init__()

    def callback(self, ch, method, properties, body):
        # print " [%s] Received %r" % (current_process().pid, body)
        db = FlowStorge.conn["flowdb"]
        flows = json.loads(body)
        db.flow.insert(flows)
        # print " [%s] Store Done" % (current_process().pid, )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.180'))
        channel = connection.channel()
        channel.queue_declare(queue='flow', durable=True)
        print ' [%s] Waiting for messages. To exit press CTRL+C' % (current_process().pid, )
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue='flow')
        channel.start_consuming()


if __name__ == "__main__":
    pool = []
    for i in range(4):
        p = FlowStorge()
        p.daemon = True
        p.start()
        pool.append(p)
    for pro in pool:
        p.join()









