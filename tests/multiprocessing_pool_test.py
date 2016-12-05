# _*_ coding:utf-8 _*_

from multiprocessing import Pool
import os
import time


def long_time_task(name):
    print 'Run task %s (%s)...' % (name, os.getpid())
    start = time.time()
    time.sleep(3)
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name, (end - start))

if __name__=='__main__':
    print 'Parent process %s.' % os.getpid()
    p = Pool(5)
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'

"""代码中的p.close()是关掉进程池子，是不再向里面添加进程了，对 Pool 对象调用join() 方法会等待所有子进程执行完毕，
调用 join() 之前必须先调用 close()，调用 close() 之后就不能继续添加新的 Process 了。"""



