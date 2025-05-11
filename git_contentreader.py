from git_base import GitBase
import zlib

class GitReader(GitBase):
    def __init__(self, repopath):
        super().__init__(repopath)

    def ReadContent(self,objectid:str)->bytes:
        """
        For reading back SMALL entries like trees, or commits, etc
        NOT FOR BLOB FILES, IT LAZILY READS BACK THE WHOLE FILE
        Will pull entry from an idx file as well.

        Args:
            objectid (str): _description_

        Raises:
            FileNotFoundError: _description_

        Returns:
            bytes: _description_
        """

        # This is not for blob files !
        # it reads back the whole object into a byte array !

        type, filename = self.findObject(objectid)

        if type is None:
            raise FileNotFoundError(f"The objectid {objectid} could not be located !")
        
        if type == 'obj':
            f = open(filename,'rb')
            b = f.read()
            f.close()
            return b
        
    
