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
    
    def searchidx(self,objectid:str):
        filename= ""

        # goes through the index files in the pack directory
        # loads the initial tables and performs object search.
        for dir in os.walk(self.packpath):

            for file in dir[2]:
                
                if file.endswith('.idx'):
                    filename = os.path.join(dir[0],file)
                    f = open(filename ,"rb")
                    idxcontents = f.read()
                    f.close()

                    idxheader, idxcontents = self.chomp(idxcontents,8)

                    fanouttable = []

                    for i in range(0,256):
                        countbytes,idxcontents = self.chomp(idxcontents,4)
                        countint = struct.unpack(">I",countbytes)[0]
                        fanouttable.append(countint)
                    
                    N = fanouttable[255]
                    
                    rawsha1 = []

                    for i in range(0,N):
                        sha1, idxcontents = self.chomp(idxcontents,20)
                        rawsha1.append(sha1)
                    
                    searchstr = bytes.fromhex(objectid)
                    char1 = searchstr[0]

                    n1 = fanouttable[char1-1] if char1 > 0 else 0
                    n2 = fanouttable[char1]

                    for i in range(n1-1,n2):
                        if rawsha1[i] == searchstr:
                            return filename   
                        
        # searching the tables if nothing found... 
        return None                                     

    
    def findObject(self,objectid:str):
        filename = self.getObjectFileName(objectid)

        if os.path.exists(filename):
            return ('obj',filename)
        
        idx = self.searchidx(objectid)

        if idx is None:
            return (None,None)

        return ('idx',idx)
       
if __name__ == "__main__":

    RepoPath = "~/Documents/placeflattener_git/"
    g = GitBase(RepoPath)

    # for project root readme.md
    i = g.searchidx('454ecfb0052cf47a83473524a70a08644bb552a0')