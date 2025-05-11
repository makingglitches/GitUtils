from git_base import GitBase
from git_head import GitHead
from git_commit import GitCommit

import hashlib
import zlib

class GitTree(GitBase):

    class GitTreeEntry:
        def __init__(self,filemode:str,filename:str,sha1sum:str):
            self.sha1sum = sha1sum
            self.filemode = filemode
            self.filename = filename
    
    def __init__(self, repopath,treeid):
        super().__init__(repopath)

        self.TreePtr = treeid
        self.TreeFileLocation = self.getObjectFileName(treeid)

        f = open(self.TreeFileLocation, 'rb')
        content = zlib.decompress( f.read())
        f.close()

        i = content.index(bytes("\x00","utf-8"))

        treeid = content[:i]
        content = content[i+1:]

        res = []

        while len(content) > 0:
            node,content = self.decodenext(content)
            res.append(node)            

        self.TreeItems = res        


    
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
    

