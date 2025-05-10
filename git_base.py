import os

class GitBase:

    def __init__(self, repopath):
        self.toplevelpath = os.path.expanduser(repopath)
        self.gitpath = os.path.join(self.toplevelpath,'.git')
        self.objectspath = os.path.join(self.gitpath,'objects')
        self.logpath = os.path.join(self.gitpath,'logs')

    def getObjectFileName(self,objectid:str):
        objdir = os.path.join(self.objectspath,objectid[:2],objectid[2:])
        return objdir