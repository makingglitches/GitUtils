from git_base import GitBase
import zlib
import git_head

class GitCommit(GitBase):

    class GitContribute:
        def __init__(self, lines:list[str]):
            self.User = lines[0]
            self.Email = lines[1].replace("<","").replace(">","")
            self.TimeStamp = lines[2]
            self.GMTOffset = lines[3]

    def __init__(self, repopath,objectid):
        super().__init__(repopath)

        self.CommitPtr = objectid
        self.commitfilename = self.getObjectFileName(objectid)
        
        f = open(self.commitfilename,'rb')

        contents = zlib.decompress(f.read()).decode()

        i = contents.index("\x00")
        
        self.commitNumber = contents[0:i].replace("commit ","")

        self.contents = contents[i+1:]

        lines = self.contents.splitlines()

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

