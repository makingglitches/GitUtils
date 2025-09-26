import sys
import os

ppath = os.path.dirname(__file__)
ppath = os.path.dirname(ppath)

sys.path.append(ppath)

import git_objectaccess
import git_const

gio = git_objectaccess.GitObjectAccess('random_git_repo')

obs = gio.LooseObjectsByType[git_const.GitObjectType.TAG]


