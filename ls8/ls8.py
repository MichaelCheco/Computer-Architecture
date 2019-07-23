#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *
args = sys.argv
program = args[1]

cpu = CPU()

cpu.load(program)
cpu.run()
