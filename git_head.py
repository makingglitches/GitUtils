import os
import utils

from git_base import GitBase

class GitHead(GitBase):    
    """
    This class looks for the head commit.  It first looks in the default path
    parses this file and uses its contents to locate the current head commit.
    Otherwise it searches the logs and parses the most current on looking
    for the last commit that has occurred and tries to discover it there.
    """
        
    def __init__(self, repopath:str):
        """
        Opens the specified repo, and looks for the HEAD commit.
        If the commit is broken anywhere in the successive set of file
        HEADBROKEN is set to True and the last logfile is checked
        if this is broken, commitptr will also be None

        Args:
            repopath (str): toplevel path of repository
        """    
        super().__init__(repopath)
        
        self.HeadFilePath = os.path.join(self.gitpath,'HEAD')
        self.HeadBroken = not os.path.exists(self.HeadFilePath)

        if not self.HeadBroken:
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
                    self.HeadBroken = True                                        
            else:
                # in detached head state.
                self.commitptr = headtext.strip()
        
        # this may seem redundant but prior block can set headbroken.
        # defaulting to logs
        if self.HeadBroken:
            logline = self.lastLogCommits()
            self.commitptr = logline['lastcommit'] if logline else None
            self.HeadBroken = True


    def lastLogCommits(self)->dict[str,str] | None:
        """
        Looks in the HEAD log for the previous commit information and parses it.
        Last line in the file is the current log.

        Returns:
            dict[str,str]: a dictionary of values from the logfile read.\n
            returns <b>None</b> if the log does not exist.
        """        
        logspath = os.path.join(self.gitpath,"logs","HEAD")

        if not os.path.exists(logspath):
            return None
        
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




    


        





