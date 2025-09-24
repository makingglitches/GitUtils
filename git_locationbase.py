from git_base import GitBase
from git_objectaccess import GitObjectAccess,GitObjectLocation,FindObjectResult
from git_const import correctId,GitObjectType
import _io
import os

class GitLocationBase(GitBase):
    """
    Base class for objects that represent a git object with an objectid and location
    in either a packfile or a loose object.
    """
    def __init__(self,repopath:str, objectId:str | bytes, expectedtype:GitObjectType):

        super().__init__(repopath)

        self.ObjectId = correctId(objectId)
        """
        The SHA1 of the object
        """

        self.gio = GitObjectAccess.FromPath(repopath)
        """
        A pointer to the GIO instance for this repository
        """

        res = self.gio.findObject(objectId)
        
        self.ObjectLocation:GitObjectLocation = res.Location if res.Found else None
        """
        Object location entry for this object
        """

        self.TempFileName:str = None
        """
        Contains the name of the temporary file containing the bytes for this object
        """
        self.Reader:_io.BufferedReader = None
        """
        When temporary object is opened by self.open() contains the byte reader object
        """

        self.ObjectType:GitObjectType = None
        """
        Specfies the object type pulled from the byte stream
        """

        # double checks that type retrieval is working for this objetc.
        if res.Found:
            # Std error code. 
            self.ErrorOnTypeNot(objectId,res.Type, expectedtype )
            
    
    def open(self)->_io.BufferedReader:
        if self.ObjectLocation is not None:
            self.TempFileName = self.gio.GetObjectBytes(self.ObjectId)[1]            
            f = open(self.TempFileName,'rb')
            self.Reader = f
            return f
        
        return None
    
    def close(self,deletetemp=True):
        if self.Reader and not self.Reader.closed:
            self.Reader.close()
        
        if os.path.exists(self.TempFileName) and deletetemp:
            os.remove(self.TempFileName)

    def readall(self)->bytes:
        f = self.open()
        res = f.read()
        self.close()

        return res





        

