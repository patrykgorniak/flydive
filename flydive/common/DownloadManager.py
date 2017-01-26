from threading import Thread
from Queue import Queue


class DownloadManager():
    """Docstring for DownloadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.task_queue = Queue()
        self.proxyList = self.initProxyList()

    def scheduleGetMethod(self, url, return_fifo):
        """TODO: Docstring for scheduleGetMethod.

        :arg1: TODO
        :returns: TODO

        """
        pass
    
    def schedulePostMethod(self, url, params, return_fifo):
        """TODO: Docstring for scheduleGetMethod.

        :arg1: TODO
        :returns: TODO

        """
        pass

    def worker(self, i, q):
        while True:
            q_params = q.get()


    def __createWorkers(self, num_workers):
        """TODO: Docstring for __createWorkers.

        :num_workers: TODO
        :returns: TODO

        """
        for i in range(num_workers):
            worker = Thread(targer=self.worker, args=(i, self.task_queue, ))
            worker.setDaemon(True)
            worker.start()



