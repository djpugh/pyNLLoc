#!/usr/bin/python
"""Python module for running NonLinLoc, including on a cluster, as well as providing utilities for converting location scatter files into angle distributions.

Code by David J Pugh
"""

__author__='David J Pugh'
__version__='1.0.0'
__email__='david.j.pugh@cantab.net'
__looseversion__=__version__
__build__=1

from pyNLLoc import __run__ as pyNLLoc_run
from Scat2Angle import __run__ as Scat2Angle_run
from XYZ2Angle import __run__ as XYZ2Angle_run
from XYZ2Angle import time as XYZ2Time_run