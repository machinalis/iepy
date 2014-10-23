#!/usr/bin/env python

import sys

from django.core.management import execute_from_command_line

import iepy
iepy.setup(__file__)


if __name__ == "__main__":
    execute_from_command_line(sys.argv)
