from git_const import GitObjectType
import git_head

from git_locationbase import GitLocationBase

from git_objectaccess import GitObjectType

class GitCommit(GitLocationBase):
    """
    Represents a single commit object in the repo tree.
    """
    class GitContribute:
        """
        Represents the user information about who committed or authored this commit
        """
        def __init__(self, lines:list[str]):
            """
            Constructor. accepts lines read from the commit object.

            Args:
                lines (list[str]): from the commit file, provided by GitCommit
            """
            self.User = lines[0]
            """
            Username of the contributor
            """
            self.Email = lines[1].replace("<","").replace(">","")
            """
            Email of the contributor
            """
            self.TimeStamp = lines[2]
            """
            Timestamp of the commit
            """
            self.GMTOffset = lines[3]
            """
            GMT Offset of the time timestamp.
            """

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
    def FromHead(repopath:str )->"GitCommit":
        """
        Parses commit from repo's current HEAD

        Args:
            repopath (str): path to the top level directory of the local repository

        Returns:
            GitCommit: the HEAD commit
        """
        g = git_head.GitHead(repopath)
        return GitCommit(g.RepoPath,g.commitptr)
    

if __name__=="__main__":
    
    repopath = "~/Documents/placeflattener_git"

    g = git_head.GitHead(repopath)

    c = GitCommit(repopath, g.commitptr)

    c1 = GitCommit.FromHead(repopath)

    objid = g.lastLogCommits()['previouscommit']

    c2:GitCommit = GitCommit(repopath,objid)
    
    print(c2.commitNumber)
    print(c2.message)
    print(c2.committer.Email)
    print(c2.author.Email)
    print(c2.commitTree)

    print("Test Passed")

