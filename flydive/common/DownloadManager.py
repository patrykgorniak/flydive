import queue 
import json
from threading import Thread
from common import HttpManager
from common import LogManager as lm
from common import Constants 
from common.ConfigurationManager import CfgMgr
import random

class DownloadThread(Thread):
    """Docstring for DownloadManager. """

    def __init__(self, num_workers, q):
        Thread.__init__(self)
        self.num_workers = num_workers
        self.task_queue = q #queue.Queue()
        self.proxyList = self.initProxyList()
        self.__createWorkers(self.num_workers)

    def run(self):
        lm.debug("Waiting for task_queue")
        self.task_queue.join()

    def initProxyList(self):
        return Constants.proxylist


    def worker(self, i, q):
        lm.debug("Created {}".format(i))
        while True:
            task = q.get()
            method = task['M']
            ret_q = task['return']
            q.task_done()

            if method is None:
                lm.debug("Method NONE.")
                while not q.empty():
                    lm.debug("Queue is not empty")
                    sleep(1)
                lm.debug("Queue is empty")
                ret_q.put( {'data':None} )
            else:
                while True:
                    proxy = self.proxyList[random.randrange(0,len(self.proxyList))]
                    lm.debug("Worker: {} Method {} PROXY: {}".format(i, task['M'], proxy))
                    if method == 0:
                        httpContent = HttpManager.getMethod(task['url'], proxy)
                        if httpContent is not None:
                            ret_q.put({'data':json.loads(httpContent.text), 'url': task['url'] } )
                            break
                    else:
                        httpContent = HttpManager.postMethod(task['url'], task['params'], proxy)
                        if httpContent is not None:
                            ret_q.put({'data':json.loads(httpContent.text), 'url': task['url'] } )
                            break

    def __createWorkers(self, num_workers):
        lm.debug("Creating {}".format(num_workers))
        for i in range(num_workers):
            w = Thread(target=self.worker, args=(i, self.task_queue, ))
            w.setDaemon(True)
            w.start()

class AsyncDownloadManager():
    def __init__(self):
        self.q = queue.Queue()
        self.cfg = CfgMgr().getConfig()
        self.workers = int(self.cfg['DOWNLOAD_MANAGER']['workers'])
        self.mgr = DownloadThread(self.workers, self.q).start()

    def scheduleGetMethod(self, url, return_fifo):
        task = { "M": 0, "url": url, "return": return_fifo }
        self.q.put(task)

    def schedulePostMethod(self, url, params, return_fifo):
        task = { "M":1, "url": url, "params": params, "return": return_fifo }
        self.q.put(task)

    def finished(self, return_fifo):
        lm.debug("Send finished")
        task = { "M": None, "return": return_fifo }
        self.q.put(task)

def main():
    mgr = AsyncDownloadManager()
    return_q = queue.Queue()
    for i in range(10):
        if i%2==0:
            mgr.schedulePostMethod("post", "params", return_q)
        else:
            mgr.scheduleGetMethod("get", return_q)

    for i in range(10):
        r = return_q.get()
        print(r)

if __name__ == "__main__":
    main()
