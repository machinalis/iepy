# -*- coding: utf-8 -*-

import os

HERE = os.path.abspath(os.path.dirname(__file__))

__version__ = None

with open(os.path.join(HERE, 'version.txt'), encoding='utf-8') as filehandler:
    __version__ = filehandler.read().strip().replace("\n", "")
