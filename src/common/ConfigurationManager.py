import configparser
import os

class CfgMgr:
    # __instance = None

    # def __new__(cls):
    #     if CfgMgr.__instance is None:
    #         CfgMgr.__instance = object.__new__(cls)
    #     return CfgMgr.__instance

    # """Docstring for CfgMgr. """

    def __init__(self, dirname='configs',filename='FlyDive.cfg'):
        self.dirname = dirname
        self.filename = filename
        self.path = os.path.join('.', self.dirname, self.filename)
        if not os.path.exists(self.path):
            self.__init()
        
    def __init(self):
        """TODO: Docstring for restoredefault.
        """
        config = configparser.ConfigParser(allow_no_value=True)

        config['GENERAL'] = {
            'author_name': 'Patryk Górniak',
            'author_mail': 'patryk.lukasz.gorniak@gmail.com',
            'app_name': 'FlyDive',
            'version': 0.1,
        }
        config['PLUGINS'] = {
            'wizzair': 'on',
            'ryanair': 'off'
        }

        with open(self.path,'w') as configfile:
            config.write(configfile)


