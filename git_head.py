import os
import utils

from git_base import GitBase

class GitHead(GitBase):
    
    def __init__(self, repopath, uselog=False):
        super().__init__(repopath)
        
        self.HeadFilePath = os.path.join(self.gitpath,'HEAD')
        self.HeadBroken = False

        f = open (self.HeadFilePath)
        headtext = f.read()
        f.close()

        # file ref is in the file.
        if headtext.startswith('ref:'):
            refptr = headtext.replace('ref:',"").strip()
            refptr = os.path.join(self.gitpath,refptr)

            if os.path.exists(refptr):
                self.commitptr = utils.readall(refptr).strip()
            else:
                if not uselog:
                    self.commitptr = None
                    self.HeadBroken = True
                    print("main file missing. git repo broken.")
                    print('would suggest running git fsck')
                    print('otherwise set uselog=True')                    
                else:
                    self.commitptr = self.lastLogCommits()['lastcommit']
                    self.HeadBroken = True
        else:
            # in detached head state.
            self.commitptr = headtext.strip()


    def lastLogCommits(self):
        logspath = os.path.join(self.gitpath,"logs","HEAD")
        
        f = open(logspath,'r')
        lines = f.readlines()
        lastline = lines[len(lines)-1]
        f.close()

        startmsg = lastline.index('commit:')

        msg = lastline[startmsg:]

        lastline = lastline[0:startmsg]

        pieces = lastline.split(" ")

        return {
                'previouscommit':pieces[0].strip(),
                'lastcommit':pieces[1].strip(),
                'author':pieces[2].strip(),
                'email':pieces[3].replace('<','').replace(">","").strip(),
                'timestamp':pieces[4].strip(),
                'timezone':pieces[5].strip(),
                'message':msg.replace("commit:","").strip()
                }

if __name__=="__main__":

    RepoPath = "~/Documents/placeflattener_git/"

    g = GitHead(RepoPath)
    
    log = g.lastLogCommits()
    print(log)

    print (g.commitptr)

    print(g.getObjectFileName(g.commitptr))




    


        





