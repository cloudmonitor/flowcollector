# _*_ coding:utf-8 _*_

from multiprocessing import Process
import os
import time

# 子进程要执行的代码
def run_proc(name):
    print 'Run child process %s (%s)...' % (name, os.getpid())
    i = 3
    while i != 0:
        i = i-1
        print 111111
        time.sleep(2)

if __name__=='__main__':
    print 'Parent process %s.' % os.getpid()
    p = Process(target=run_proc, args=('test',))
    p1 = Process(target=run_proc, args=('test',))
    print 'Process will start.'
    p.start()
    p1.start()
    p.join()
    print "dfsdfsd"
    p1.join()
    p.join()
    print 'Process end.'

