from git_head import GitHead
from git_commit import GitCommit
from git_const import GitObjectType
from git_const import correctId
from git_locationbase import GitLocationBase


class GitTree(GitLocationBase):

    class GitTreeEntry:
        def __init__(self,filemode:str,filename:str,objectid:str | bytes, type:GitObjectType ):
            self.sha1sum:bytes = correctId( objectid)
            self.filemode:str = filemode
            self.filename:str = filename
            self.type:GitObjectType = type
    
    def __init__(self, repopath,objectid:str | bytes):
        super().__init__(repopath,objectid,GitObjectType.TREE)

        if not self.ObjectLocation:
            # continue with no other 
            return
        
        content = self.readall()
        
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


    def decodenext(self,buffer:bytes)->tuple[GitTreeEntry,bytes]:
        
        i= buffer.index(" ".encode())

        mode,buffer = self.chomp(buffer,i+1)
        mode = mode.decode().strip()
        
        i = buffer.index(b"\x00")
        filename,buffer = self.chomp(buffer,i+1)
        filename = filename.decode().strip()[:len(filename)-1]

        shabuff,buffer = self.chomp(buffer, 20)

        fres = self.gio.findObject(shabuff)        

        return (GitTree.GitTreeEntry(mode,
                                     filename,
                                     shabuff.hex(), 
                                     fres.Type),
                buffer)

if __name__=="__main__":
    
    repopath = "~/Documents/placeflattener_git"

    g = GitHead(repopath)
    gc = GitCommit.FromHeadObject(g)
   
    gt =  GitTree(repopath,gc.commitTree)

    print (gt.ObjectLocation)
    

