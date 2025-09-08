from git_base import GitBase
from git_head import GitHead
from git_commit import GitCommit
from git_objectaccess import GitObjectAccess
from git_objectaccess import GitObjectLocation
from git_const import GitObjectType
from git_const import correctId

import hashlib
import zlib

class GitTree(GitBase):

    class GitTreeEntry:
        def __init__(self,filemode:str,filename:str,objectid:str | bytes, type:GitObjectType ):
            self.sha1sum:bytes = correctId( objectid)
            self.filemode:str = filemode
            self.filename:str = filename
            self.type:GitObjectType = type
    
    def __init__(self, repopath,treeid:str | bytes):
        super().__init__(repopath)

            
        self.TreePtr:bytes = correctId (treeid)

        """
        Contains the object Id of the tree.
        """   

        gio = GitObjectAccess.FromPath(repopath)

        res = gio.findObject(treeid)

        
        self.TreeFileLocation:GitObjectLocation = None if not res.Found else res.Location

        # if this happens something is very very wrong.
        if res.Type != GitObjectType.TREE:
            emsg = f"Object {self.TreePtr.hex()} if not of the correct type\nFindObject returned {res.Type} "
            raise TypeError(emsg)

        # retrieve tree bytes.
        bfilename:str = gio.GetObjectBytes(self.TreePtr)[1]

        f = open(bfilename, 'rb')
        content = f.read()
        f.close()

        # decode tree object.
        i = content.index(bytes("\x00","utf-8"))

        treenumber = content[:i]

        # header contains 'tree {treenumber}'
        self.TreeNumber:int = int(treenumber.replace(b'tree ', b'').decode())

        content = content[i+1:]

        treeitems = []

        while len(content) > 0:
            node,content = self.decodenext(content)
            treeitems.append(node)            

        self.TreeItems:list[GitTree.GitTreeEntry] = treeitems      


    def decodenext(self,buffer:bytes):
        
        i= buffer.index(" ".encode())

        mode,buffer = self.chomp(buffer,i+1)
        mode = mode.decode().strip()
        
        i = buffer.index(b"\x00")
        filename,buffer = self.chomp(buffer,i+1)
        filename = filename.decode().strip()[:len(filename)-1]

        shabuff,buffer = self.chomp(buffer, 20)

        return (GitTree.GitTreeEntry(mode,filename,shabuff.hex()),buffer)

if __name__=="__main__":
    
    repopath = "~/Documents/placeflattener_git"

    g = GitHead(repopath)
    gc = GitCommit.FromHead(g)
   
    gt =  GitTree(repopath,gc.commitTree)

    print (gt.TreeFileLocation)
    

