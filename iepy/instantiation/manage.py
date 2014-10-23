#!/usr/bin/env python

import os
import sys

from django.core.management import execute_from_command_line

import iepy


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(here)
    iepy.setup(parent_dir)
    execute_from_command_line(sys.argv)

