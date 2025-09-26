import os

def readall(filename:str)->str:
    f = open(filename,'r')
    s = f.read()
    f.close()
    return s

def getallfilenames(searchpath:str)->list[str]:
    res = []

    for path,dirnames,filenames in os.walk(searchpath):
        dirnames[:] = []

        for f in filenames:
            res.append(os.path.join(path, f ))

    return res
