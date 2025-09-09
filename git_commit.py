from git_base import GitBase
from git_const import getHexId, correctId,GitObjectType
import zlib
import git_head

from git_locationbase import GitLocationBase


from git_objectaccess import GitLocationType, \
                             GitObjectLocation, \
                             GitObjectAccess,\
                             GitObjectType

class GitCommit(GitLocationBase):

    class GitContribute:
        def __init__(self, lines:list[str]):
            self.User = lines[0]
            self.Email = lines[1].replace("<","").replace(">","")
            self.TimeStamp = lines[2]
            self.GMTOffset = lines[3]

    def __init__(self, repopath,objectid:str | bytes):
        super().__init__(repopath,objectid,GitObjectType.COMMIT)

        contents = self.readall()

        i = contents.index(b"\x00")
        
        self.commitNumber = contents[0:i].replace(b"commit ",b"").decode()

        self.contents =  contents[i+1:]

        lines = [s.decode() for s in  self.contents.splitlines()]

        self.commitTree = lines[0].replace('tree','').strip()
        self.parentCommitPtr = lines[1].replace('parent','' ).strip()
        self.author  = GitCommit.GitContribute( self.splitcontline(lines[2]))
        self.committer =  GitCommit.GitContribute(self.splitcontline(lines[3]))
        
        # line 5(4) is always blank
        self.message = "\n".join(lines[5:])
        
    

    def splitcontline(self,line:str):
        lines = line.split(" ")

        return lines[1:]


    @staticmethod
    def FromHead(g:git_head.GitHead):
        return GitCommit(g.toplevelpath,g.commitptr)
    
    def FromHeadandPtr(g:git_head.GitHead, objectid:str):
        return GitCommit(g.toplevelpath,objectid)

if __name__=="__main__":
    
    repopath = "~/Documents/placeflattener_git"

    g = git_head.GitHead(repopath)

    c = GitCommit(repopath, g.commitptr)

    c1 = GitCommit.FromHead(g)

    objid = g.lastLogCommits()['previouscommit']

    c2 = GitCommit.FromHeadandPtr(g,objid)

    print("Test Passed")

