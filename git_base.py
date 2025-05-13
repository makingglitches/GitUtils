import os
import struct

class GitBase:

    def __init__(self, repopath):
        self.toplevelpath = os.path.expanduser(repopath)
        self.gitpath = os.path.join(self.toplevelpath,'.git')
        self.objectspath = os.path.join(self.gitpath,'objects')
        self.logpath = os.path.join(self.gitpath,'logs')
        self.packpath = os.path.join(self.objectspath,'pack')

    def getObjectFileName(self,objectid:str):
        objdir = os.path.join(self.objectspath,objectid[:2],objectid[2:])
        return objdir
    
    def chomp(self, buffer:bytes, len:int)->tuple[bytes,bytes]:
        piece = buffer[:len]
        buffer = buffer[len:]

        return (piece, buffer)
      
    def findObjectInPath(self,objectid:str):
        filename = self.getObjectFileName(objectid)

        if os.path.exists(filename):
            return filename

        return None
        

       
if __name__ == "__main__":

    RepoPath = "~/Documents/placeflattener_git/"
    g = GitBase(RepoPath)

    # for project root readme.md
    i = g.searchidx('454ecfb0052cf47a83473524a70a08644bb552a0')