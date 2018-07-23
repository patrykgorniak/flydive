import queue 
import json
from threading import Thread
from common import HttpManager
from common import LogManager as lm
from common import Constants 
from common.ConfigurationManager import CfgMgr
import random
import time
import sys, os
from time import sleep

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
        file = open("configs/proxy.txt")
        proxyTxt = file.read()
        file.close()
        file = open("configs/https_proxy.txt")
        httpsProxyTxt = file.read()
        file.close()
        # proxyTxt = HttpManager.getMethod("http://multiproxy.org/txt_all/proxy.txt").text
        # return Constants.proxylist
        return self.parseProxyTxt(proxyTxt, httpsProxyTxt)

    def parseProxyTxt(self, proxyListTxt, httpsProxyTxt):

        proxyList = []
        # for http, https in zip(httpsProxyTxt.split("\n"), proxyListTxt.split("\n")):
        for http in proxyListTxt.split("\n"):
            proxyList.append( {"http" : http} )
        return proxyList

    def worker(self, i, q):
        lm.debug("Created {}".format(i))
        limit = 5
        while True:
            counter = 0
            task = q.get()
            method = task['M']
            ret_q = task['return']

            if method is None:
                lm.debug("Method NONE.")
                while not q.empty() and not ret_q.empty():
                    lm.debug("Queue is not empty")
                    sleep(1)
                lm.debug("Queue is empty")
                ret_q.put( {'data':None} )
            else:
                while True:
                    if counter == limit:
                        lm.debug("No response from server.")
                        ret_q.put( {'data':None} )

                    proxy = self.proxyList[random.randrange(0,len(self.proxyList))]
                    lm.debug("Worker: {} Method {} PROXY: {}".format(i, task['M'], proxy))
                    if method == 0:
                        # time.sleep(random.randrange(3, 12))
                        httpContent = HttpManager.getMethod(task['url'], proxy)
                        if httpContent is not None:
                            ret_q.put({'data':json.loads(httpContent.text), 'url': task['url'] } )
                            break
                        else:
                            lm.debug("Request error for: {} {}".format(task['url'], proxy))
                    else:
                        # time.sleep(random.randrange(3, 12))
                        httpContent = HttpManager.postMethod(task['url'], task['params'], proxy)
                        if httpContent is not None:
                            ret_q.put({'data':json.loads(httpContent.text), 'url': task['url'] } )
                            break
                        else:
                            lm.debug("Request error for: {} {}".format(task['url'], proxy))
                    counter = counter + 1
                    sleep(counter * 2)

            q.task_done()

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
        self.q.join();
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
