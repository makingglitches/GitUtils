import zlib

from git_head import GitHead


class GitTyper:

    objecttypes:list[str] = ['blob','tree','commit','tag']

    @staticmethod
    def getType(filename:str):
        z  = zlib.decompressobj()
        res = b""

        f = open(filename,'rb')

        frame = f.read(100)

        while frame:
            res = res +  z.decompress(frame)
            frame = f.read(100)
            datype = None

            for t in GitTyper.objecttypes:
               if t in res:
                   datype = t
                   break
            
            if datype is not None:
               f.close()               
               return datype
           
        f.close()
        return None

if __name__ == "__main__":

    blobuid = "5d49a3487ef956f4ebe2823b0da690d25e931ab7"
    treeuid = "555733f9c6c19427f88dd4863eb9c128ca2f2e20"
    
    repopath = "~/Documents/placeflattener_git"

    g = GitHead(repopath)




