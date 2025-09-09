from git_base import GitBase
from git_objectaccess import GitObjectAccess,GitObjectLocation,FindObjectResult
from git_const import correctId,GitObjectType
import _io
import os

class GitLocationBase(GitBase):
    def __init__(self,repopath:str, objectId:str | bytes, expectedtype:GitObjectType):

        super().__init__(repopath)

        self.ObjectId = correctId(objectId)

        self.gio = GitObjectAccess.FromPath(repopath)
        res = self.gio.findObject(objectId)
        
        self.ObjectLocation:GitObjectLocation = res.Location if res.Found else None

        self.TempFileName:str = None
        self.Reader:_io.BufferedReader = None
        self.ObjectType:GitObjectType = None

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





        

