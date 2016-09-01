import configparser
import os

class CfgMgr:

    def __init__(self):
        self.cfg = self.Config()
        self.__instance = self.cfg.getConfig()

    def getConfig(self):
        return self.__instance

    class Config:

        def __init__(self, dirname='configs',filename='FlyDive.cfg'):
            self.__instance = None
            self.dirname = dirname
            self.filename = filename
            self.path = os.path.join('.', self.dirname, self.filename)
            if not os.path.exists(self.path):
                self.__instance = self.__init()
            else:
                config = configparser.ConfigParser()
                config.read(self.path)
                self.__instance = config



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

            config['DATABASE'] = {
                'name': 'flydive',
                'type': 'sqlite'
            }

            with open(self.path,'w') as configfile:
                config.write(configfile)

        def getConfig(self):
            """TODO: Docstring for getConfig.
            :returns: TODO

            """
            return self.__instance

def main():
    mgr = CfgMgr().getConfig();
    print(mgr.sections())

if __name__ == "__main__":
    main()
