from git_base import GitBase
from git_head import GitHead
from git_commit import GitCommit

class GitTree(GitBase):
    def __init__(self, repopath,treeid):
        super().__init__(repopath)

        self.TreePtr = treeid
        self.TreeFileLocation = self.getObjectFileName(treeid)


if __name__=="__main__":
    
    repopath = "~/Documents/placeflattener_git"

    g = GitHead(repopath)
    gc = GitCommit.FromHead(g)
   
    gt =  GitTree(repopath,gc.commitTree)

    print (gt.TreeFileLocation)
    

