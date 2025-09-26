import os
import struct
from git_const import getHexId
from git_const import GitObjectType

class _basestruct:
    def __init__(self, repopath:str):        
        self.toplevelpath:str = os.path.expanduser(repopath)
        """
        Top Level path of the git repo eg ~/MyRepo
        """        

        self.gitpath:str = os.path.join(self.toplevelpath,'.git')
        """
        The git subdirectory. eg ~/MyRepo/.git
        """        

        self.objectspath:str = os.path.join(self.gitpath,'objects')
        """
        Location of the loose and pack objects directory
        """        

        self.logpath:str = os.path.join(self.gitpath,'logs')
        """
        Location of commit logs
        """        

        self.packpath:str = os.path.join(self.objectspath,'pack')
        """
          Location of the packfiles.s
        """  

        self.loosetagspath:str = os.path.join(self.gitpath, 'refs','tags')  
        """
        Location where loose tags not consolidated by `git gc` have been stored.
        One commit object id per file
        """

        self.packedtagsfile:str = os.path.join(self.gitpath,'packed-refs')
        """
        Location where tag names referenencing specific commits have been stored.
        """

        self.looseheadspath:str = os.path.join(self.gitpath,'refs','heads')


GITBASE_REGISTRY:dict[str, _basestruct]  = {}

class GitBase:
    """
    Base object for most major git objects in this package, provides convenience methods
    and directory pointers.
    """ 
    
    # place all references to gitbase fields specifically here
    # the idea is to keep the same values from being stored many many times
    RepoPath:str = property( lambda self: self._dictptr.toplevelpath )   
    gitpath:str = property(lambda self: self._dictptr.gitpath)
    objectspath:str = property(lambda self: self._dictptr.objectspath)
    logpath:str = property( lambda self: self._dictptr.logpath)
    packpath:str = property( lambda self: self._dictptr.packpath)
    loosetagspath:str = property( lambda self: self._dictptr.loosetagspath)
    packedtagsfile:str = property( lambda self: self._dictptr.packedtagsfile)
    looseheadspath:str = property( lambda self: self._dictptr.looseheadspath)

    def __init__(self, repopath:str):

        self.dictptr:_basestruct = None

        if repopath in GITBASE_REGISTRY:
            self._dictptr = GITBASE_REGISTRY[repopath]
        else:
            self._dictptr = _basestruct(repopath)
            GITBASE_REGISTRY[repopath] = self._dictptr  
               

    def ErrorOnTypeNot(self,objectid:str|bytes, objtype:GitObjectType, expected:GitObjectType):
        if objtype != expected:
            s = f"ERROR !\n This should never happen !\nExpected {expected}\nFound:{objtype}\nFor Object {getHexId(objectid)}"
            raise ValueError(s)

    def getObjectFileName(self,objectid:str | bytes)->str:
        """
        Returns the likely loose object filename if object id is not in a packfile.

        Returns:
            str: the full possible path to the object if its a loose object.
        """        
        objectid = getHexId(objectid)
        objdir = os.path.join(self.objectspath,objectid[:2],objectid[2:])

        return objdir
    
    @staticmethod
    def getVarInt( b:bytes, initialLeftShift=0)->int:
        """
        Retrieves a variable integer as found in record headers indicating length

        Args:
            b (bytes): the full list of bytes discovered
            initialLeftShift (int, optional): the initial left bitshift. Defaults to 0.

        Returns:
            tuple[int,int]: the retrieved integer value
        """        
        shift = initialLeftShift

        value = 0

        for i in range(0,len(b)):
                # make room for the next 7 bits            
                bits = b[i] & 0b01111111
                value |= (bits << shift)
                shift += 7

        return value

    def chomp(self, buffer:bytes, len:int)->tuple[bytes,bytes]:
        """
        Removes the first len bytes from the buffer and returns the remaining buffer
        and extracted value

        Args:
            buffer (bytes): initial byte string
            len (int): length of bytes to extract

        Returns:
            tuple[bytes,bytes]: tuple containing the extracted value, and then the remaining bytes.
        """        
        piece = buffer[:len]
        buffer = buffer[len:]

        return (piece, buffer)
      
    def findObjectInPath(self,objectid:str | bytes)->str | None:
        """
        Determines if an object exists in the loose objects dirctories of the repo

        Args:
            objectid (str | bytes): the object id in question

        Returns:
            str | None: if object is loose, returns path to the object, otherwise returns None
        """        

        filename = self.getObjectFileName(objectid)

        return filename if os.path.exists(filename) else None
        
       
if __name__ == "__main__":

    testid = '4621aaae578e5dee50584ced72f9591c4f5e4055'

    RepoPath = "~/Documents/placeflattener_git/"
    g = GitBase(RepoPath)

    bstr = b'\x81\xf5\xff\x82}'

    o=     [ g.RepoPath,    
           g.gitpath, \
           g.logpath, \
           g.packpath, \
           g.objectspath, \
           g.getObjectFileName(testid), \
           g.findObjectInPath(testid), \
           g.chomp(bstr, 2),
           g.getVarInt(bstr)]
    
    print(o)

    
        

    