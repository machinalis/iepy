# adjustment of the sys.path for been able to import ORM stuff while defining
# models
from __future__ import absolute_import
import os
import sys
import iepy

ORM_NEEDED_PATH = os.path.join(iepy.__path__[0], 'webui')

if ORM_NEEDED_PATH not in sys.path:
    print 'Adding %s to the python path' % ORM_NEEDED_PATH
    sys.path.append(ORM_NEEDED_PATH)
    iepy.setup()

