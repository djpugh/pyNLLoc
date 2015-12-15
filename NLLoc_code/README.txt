======================================================
Complete NonLinLoc distribution software package
======================================================
Unpack source files: unpack: NLL[VER]_src.tgz
To build:
Solaris:
	make all
Linux:
	make -R all
See http://alomax.net/nlloc and http://alomax.net/nlloc -> tutorials for further information
======================================================


===========================================================================
NLLoc_func_test program demonstrating running NLLoc through a function call
===========================================================================
Unpack source files: unpack: NLL[VER]_src.tgz
To build:
Solaris (not tested):
	make NLLoc_func_test
Linux:
	make -R NLLoc_func_test
Unpack demo files: unpack: NLL[VER]_func.tgz
To run:
	cd nll_func
	./run_func.sh
# clean
	rm -rf out/*
	cd ..
See nll_func/run_func.sh for more detail.
===========================================================================


===========================================================================
ttime_func_test program demonstrating reading values from 2D or 3D grid file through a function call
===========================================================================
Unpack source files: unpack: NLL[VER]_src.tgz
To build:
Solaris (not tested):
	make ttime_func_test
Linux:
	make -R ttime_func_test
Unpack demo files: unpack: NLL[VER]_func.tgz
To run:
	cd ttime_func
	./run_func.sh
	cd ..
See ttime_func/run_func.sh for more detail.
===========================================================================
