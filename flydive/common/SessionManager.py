import os
import sys
import json
from common.DatabaseModel import Connections
from common import LogManager as lm
from datetime import datetime

# TODO: merge this JSON encoder with FLJsonEncoder from tools
class SessionEncoder(json.JSONEncoder):
    def default(self, objs):
        """TODO: Docstring for default.

        :o: TODO
        :returns: TODO

        """
        if isinstance(objs,datetime):
            return objs.timestamp()

        return objs.to_dict()

class SessionDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        t = Connections(id=d['id'], src_iata=d['src_iata'], dst_iata=d['dst_iata'], carrierCode=d['carrierCode'])
        return t


class SessionManager(object):
    """docstring for SessionManager"""
    def __init__(self, session_name):
        super(SessionManager, self).__init__()
        self.session_name = session_name
        self.dir = "status"
        self.session_file = self.session_name + "_session.txt"
        self.full_path = os.path.join(self.dir, self.session_file)
        self.open = False
        self.restore = False

        self.__open()

    def log(self, message):
        lm.debug("SessionManager: {0}".format(message))

    def __open(self):
        """TODO: Docstring for open.
        :returns: TODO

        """
        self.open = True
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        if not os.path.exists(self.full_path):
            self.restore = False
        else:
            self.restore = True

    def isOpen(self):
        """TODO: Docstring for is_open.
        :returns: TODO

        """
        return self.open

    def isSaved(self):
        """TODO: Docstring for isSaved.
        :returns: TODO

        """
        return self.restore

    def save(self, objs):
        """TODO: Docstring for logState.

        :state: TODO
        :returns: TODO

        """
        print(type(objs[0]))
        if type(objs[0]) is not Connections:
            raise TypeError("Object is not type of Connections")
        self.__save(objs)

    def restoreSession(self):
       """TODO: Docstring for restoreSession.
       :returns: TODO

       """
       self.log("Restore session.")
       restoredSession = []
       restoredSession.extend(self.__load())
       return restoredSession

    def __load(self):
        """TODO: Docstring for load.
        :returns: TODO

        """
        if os.path.exists(self.full_path):
            with open(self.full_path, 'r', encoding="utf-8") as f:
                content = f.read()
                f.close()
                array = json.loads(content, cls=SessionDecoder)
                return array

    def __save(self, obj):
        """TODO: Docstring for save.
        :returns: TODO

        """
        encoded = json.dumps(obj, cls=SessionEncoder)
        print(self.full_path)
        with open(self.full_path, 'w', encoding="utf-8") as f:
            f.write(encoded)
            f.close()

    def close(self):
        """TODO: Docstring for close.
        :returns: TODO

        """
        if os.path.exists(self.full_path):
            os.remove(self.full_path)
            self.open = False


def __test_main():
    """TODO: Docstring for __test_main.
    :returns: TODO

    """
    s = SessionManager("test")
    if(s.isSaved()):
        print("Session can be restored")
        con = s.restoreSession()
        for c in con:
            print("{} : {}".format(type(c), c))
        s.close()
    else:
        print("Save session")
        date = datetime.now()
        con = []
        for i in range(5):
            con.append(Connections(id = i, src_iata="WAW_{}".format(i), dst_iata="LTN_{}".format(i), carrierCode = "W6",
                                   updated=str(date)))
            # con.append({"src_iata": "WAW_{}".format(i), "dst_iata": "LTN_{}".format(i), "carrierCode" : "W6",
            #             "updated": str(date)})
        s.save(con)

if __name__=="__main__":
    __test_main()
