from threading import Thread
import queue 

class DownloadManager():
    """Docstring for DownloadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.task_queue = queue.Queue()
        self.proxyList = self.initProxyList()
        self.__createWorkers(10)

    def initProxyList(self):
        """TODO: Docstring for initProxyList.
        :returns: TODO

        """
        pass

    def scheduleGetMethod(self, url, return_fifo):
        """TODO: Docstring for scheduleGetMethod.

        :arg1: TODO
        :returns: TODO

        """
        task = { "M": 0, "url": url, "return": return_fifo }
        self.task_queue.put(task)
    
    def schedulePostMethod(self, url, params, return_fifo):
        """TODO: Docstring for scheduleGetMethod.

        :arg1: TODO
        :returns: TODO

        """
        task = { "M":1, "url": url, "params": params, "return": return_fifo }
        self.task_queue.put(task)

    def worker(self, i, q):
        print("Created {}".format(i))
        while True:
            q_params = q.get()
            print("Worker: {} Methond {}".format(i, q_param['M']))
            r = q_param['return']
            r.put({"ret": 1})
            q.task_done()


    def __createWorkers(self, num_workers):
        """TODO: Docstring for __createWorkers.

        :num_workers: TODO
        :returns: TODO

        """
        print("Creating {}".format(num_workers))
        for i in range(num_workers):
            w = Thread(target=self.worker, args=(i, self.task_queue, ))
            w.setDaemon(True)
            w.start()

def main():
    """TODO: Docstring for function.

    :arg1: TODO
    :returns: TODO

    """
    mgr = DownloadManager()
    return_q = queue.Queue()
    for i in range(10):
        if i%2==0:
            mgr.schedulePostMethod("post", "params", return_q)
        else:
            mgr.scheduleGetMethod("get", return_q)

    return_q.join()

if __name__ == "__main__":
    main()
