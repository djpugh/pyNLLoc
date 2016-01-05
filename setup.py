#!/usr/bin/env python
"""Setup script for pyNLLo scripts
*************************************
Call from command line as: sudo python setup.py install if on unix
or python setup.py install


"""
from __future__ import print_function
from distutils.core import setup
try:
  from setuptools import setup
  _SETUPTOOLS=True
except:
  try:
    from ez_setup import setuptools
    _SETUPTOOLS=True
  except:
    _SETUPTOOLS=False
    from distutils.core import setup as setup
import sys,shutil,os,datetime,subprocess,glob

def setup_package(install=False,build=False,clean=False):
    """setup_package()

    Function to call distutils setup to install the package to the default location for third party modules.

    Checks to see if required modules are installed and if not tries to install them (apart from Basemap)
    """ 
    try:
        from .__init__ import __author__,__version__,__email__,__doc__,__looseversion__,__build__
    except:
        from __init__ import __author__,__version__,__email__,__doc__,__looseversion__,__build__
    kwargs=dict(name='pyNLLoc',version=str(__version__)+'b'+str(__build__),author=__author__,author_email=__email__,
                packages=['pyNLLoc'],
                package_dir={'pyNLLoc':'.'},
                requires=[],
                install_requires=[],
                provides=['pyNLLoc','Scat2Angle','XYZ2Angle'],
                url='https://github.com/djpugh/pyNLLoc',
                download_url='https://github.com/djpugh/pyNLLoc/tarball/v'+__version__,
                bugtrack_url='https://github.com/djpugh/pyNLLoc/issues',
                scripts=['pyNLLoc.py','Scat2Angle.py','XYZ2Angle.py'],
                description='pyNLLoc: Python functions for NonLinLoc and Scat2Angle',
                long_description=__doc__+'\n\n'+open('README.md').read()+'\n',
                package_data={'pyNLLoc':['README','make_angles.sh','GridLib.c','GetAngles.cpp','NLLoc_code/*/*','NLLoc_code/*.*']},
                classifiers=["Development Status :: 5 - Production/Stable",
                             "Intended Audience :: Science/Research",
                             "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                             "Natural Language :: English",
                             "Programming Language :: Python",
                             "Programming Language :: C++",
                             "Topic :: Scientific/Engineering"
                            ])
    if _SETUPTOOLS:
        kwargs['extras_require']={'Cluster':['pyqsub>=1.0.0']}
        kwargs['install_requires'].append('pyqsub>=1.0.0')
        kwargs.pop('scripts')
        kwargs['version']=__looseversion__
        kwargs['entry_points']={'console_scripts': ['pyNLLoc = pyNLLoc:pyNLLoc_run','Scat2Angle = pyNLLoc:Scat2Angle_run','XYZ2Angle = pyNLLoc:XYZ2Angle_run']#,'XYZ2Time = pyNLLoc:XYZ2Time_run']
                                }
    if build or 'build_all' in sys.argv or 'build-all' in sys.argv:
        #clean dist dir
        try:
            for fname in glob.glob('dist/*'):
                try:
                    os.remove(fname)
                except:
                    pass
        except:
            pass
        print ('------\nBUILDING DISTRIBUTIONS\n-----\n')
        clean_package()
        argv=[sys.executable,"setup.py","sdist"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","sdist","--format=gztar"]
        subprocess.call(argv)
        if _SETUPTOOLS:
            clean_package()
            argv=[sys.executable,"setup.py","bdist_egg"]
            subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wheel"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_msi"]
        subprocess.call(argv)
        clean_package()
        print ('\n------\nBUILD COMPLETE\n------\n')
        
    elif 'pypi_upload' in sys.argv:
        argv=[sys.executable,"setup.py","sdist","upload", "-r", "pypi"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","sdist","--format=gztar","upload", "-r", "pypi"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wininst","upload", "-r", "pypi"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wheel","upload", "-r", "pypi"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_msi","upload", "-r", "pypi"]
        subprocess.call(argv)
    elif 'clean_all' in sys.argv or clean or 'clean-all' in sys.argv:
        argv=[sys.executable,"setup.py","clean","--all"]
        subprocess.call(argv)
        try:
            shutil.rmtree('build/')
        except:
            pass
        try:
            shutil.rmtree('pyNLLoc-'+__looseversion__+'/')
            shutil.mkdir('pyNLLoc-'+__looseversion__+'/')
        except:
            try:
                shutil.rmtree('pyNLLoc-'+__version__+'/')
                shutil.mkdir('pyNLLoc-'+__version__+'/')
            except:
                pass
        if _SETUPTOOLS:
            try:
                shutil.rmtree('pyNLLoc.egg-info/')
                shutil.mkdir('pyNLLoc.egg-info/')
            except:
                pass
    else:
        if 'install' in sys.argv:
            #Try to build GetNLLOCScatterAngles and add to scripts
            ret=os.system('make all')
            if ret!=0:
                ret=os.system('./make_angles.sh')
            if ret!=0:
                print ('\n\n*******************************\n\nC++ module not automatically compiled.\nPlease build manually.\n\n*******************************\n\n')

        try:
            setup(**kwargs)
        except ValueError:
            kwargs['version']=__version__
            setup(**kwargs) 
def setup_help():
    #Run setup with cmd args (DEFAULT)
    if '--help' in sys.argv or '-h' in sys.argv:
        print ("""setup.py script for pyNLLoc
          
pyNLLoc can be installed from the source by calling:

    $ python setup.py install

To install it as a non root user (or without using sudo):

    $ python setup.py install --user

This will install the module to the user site-packages directory. Alternatively, to install the module to a specific location use:

     $ python setup.py install --prefix=/path/to/top_level_directory

""")
        
    if '--help' in sys.argv or '-h' in sys.argv or '--help-commands' in sys.argv:
        print ("pyNLLoc has several additional commands in addition to the standard commands",end='')
        if not '--help-commands' in sys.argv:
            print ("(see --help-commands)",end='')
            print ("\b. These include:")
            print ("")
        print ("""  build_all         build all distributions
  clean_all         clean all cython and build related files
    """)
def clean_package():
  old_argv=sys.argv
  sys.argv=['clean_all']
  setup_package(clean=True)
  sys.argv=old_argv


if __name__=="__main__":
  setup_package()
