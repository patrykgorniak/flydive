from threading import Thread
import queue 

class DownloadManager():
    """Docstring for DownloadManager. """

    def __init__(self, num_workers, q):
        """TODO: to be defined1. """
        self.num_workers = num_workers
        self.task_queue = q #queue.Queue()
        self.proxyList = self.initProxyList()
        self.__createWorkers(self.num_workers)

    def initProxyList(self):
        pass

    def scheduleGetMethod(self, url, return_fifo):
        task = { "M": 0, "url": url, "return": return_fifo }
        self.task_queue.put(task)
    
    def schedulePostMethod(self, url, params, return_fifo):
        task = { "M":1, "url": url, "params": params, "return": return_fifo }
        self.task_queue.put(task)

    def worker(self, i, q):
        print("Created {}".format(i))
        while True:
            q_params = q.get()
            print(q_params)
            print("Worker: {} Method {}".format(i, q_params['M']))
            r = q_params['return']
            r.put({"ret": 1})
            q.task_done()


    def __createWorkers(self, num_workers):
        print("Creating {}".format(num_workers))
        for i in range(num_workers):
            w = Thread(target=self.worker, args=(i, self.task_queue, ))
            w.setDaemon(True)
            w.start()

def main():
    q = queue.Queue()
    mgr = DownloadManager(5, q)
    return_q = queue.Queue()
    for i in range(10):
        if i%2==0:
            mgr.schedulePostMethod("post", "params", return_q)
        else:
            mgr.scheduleGetMethod("get", return_q)
    q.join()

if __name__ == "__main__":
    main()
