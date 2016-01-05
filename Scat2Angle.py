#!/usr/bin/python
"""Scat2Angle
***********************

Scat2Angle is a python wrapper for the C++ executable compiled from getAngles.cpp. 
This uses some of the functions in the NonLinLoc code (specifically GridLib and it's dependencies)
to convert the location PDF scatter samples into take-off angle samples for all stations. 

To compile the executable, it is necesary to compile some other components into object code. For an example, please see the make_angles.sh file, or the README

The input control file is very simple - A two line file::
    
    path/to/nonlinloc/time/gridfiles
    path/to/nonlinloc/loc/scatfiles

The paths can have the beginning of the file name as well
e.g. ~/mynlloc/time/grid

where the grid files are in ~/mynlloc/time and begin with e.g. grid.***** for the P phases. The same applies for the location .scat files.

There is an optional third line which sets the phase to use (i.e. P or S), where the default is P.



Command line flags
*********************************
To obtain a list of the command line flags use the -h flag::

    $~ Scat2Angle -h

This will provide a list of the arguments and their usage.


Running from the command line
*********************************
To run from the command line on  linux/*nix  it is necessary to make sure that the Scat2Angle script installed is on the path,
or to set up a manual alias/script, e.g. for bash::

    python -c "import Scat2Angle;Scat2Angle.__run__()" $*


On windows (Requires NLLoc programs to be installed on windows too) using powershell add the following commandlet to your profile (for information on customizing your powershell profile see: http://www.howtogeek.com/50236/customizing-your-powershell-profile/)::

    function Scat2Angle{
        $script={
            python -c "import Scat2Angle;Scat2Angle.__run__()" $args
        }
        Invoke-Command -ScriptBlock $script -ArgumentList $args
    }



Running from within python
*********************************
To run from within python, (assuming the module is on your PYTHONPATH)::

    >>import Scat2Angle
    >>Scat2Angle.__run__()

This will run with the default options, although these can be customized - see the Scat2Angle.__run__ docstrings.
 
Output file
*********************************

The output format for the scatangle file is:

            Probability
            StationName Azimuth TakeOffAngle
            StationName Azimuth TakeOffAngle

            Probability
            .
            .
            .

e.g.::

            504.7
            S0271   231.1   154.7
            S0649   42.9    109.7
            S0484   21.2    145.4
            S0263   256.4   122.7
            S0142   197.4   137.6
            S0244   229.7   148.1
            S0415   75.6    122.8
            S0065   187.5   126.1
            S0362   85.3    128.2
            S0450   307.5   137.7
            S0534   355.8   138.2
            S0641   14.7    120.2
            S0155   123.5   117
            S0162   231.8   127.5
            S0650   45.9    108.2
            S0195   193.8   147.3
            S0517   53.7    124.2
            S0004   218.4   109.8
            S0588   12.9    128.6
            S0377   325.5   165.3
            S0618   29.4    120.5
            S0347   278.9   149.5
            S0529   326.1   131.7
            S0083   223.7   118.2
            S0595   42.6    117.8
            S0236   253.6   118.6

            502.7
            S0271   233.1   152.7
            S0649   45.9    101.7
            S0484   25.2    141.4
            S0263   258.4   120.7
            .
            .
            .
"""
EXECUTABLE="GetNLLOCScatterAngles"#Default name for C++ executable compiled using make_angles.sh
import glob,sys,os
def read_control():
    """Read control file from command line arguments.

    If --grid or -g is set as a command line argument, the sample probability values are kept, otherwise they are set to 1 (for Markov chain type sampling).

    Returns

        (str,str,str,bool): tuple of strings and bool for the grid file path, scatter file path, phase and the grid_sampling flag.
    """
    control=open(sys.argv[1],'r').readlines()
    grid_root=control[0].rstrip()
    scatter_root=control[1].rstrip()
    try:
        phase=control[2].rstrip()
    except:
        phase='P'
    try:
        grid_sampling=not control[3].rstrip().lower()=='false'
    except:
        grid_sampling=False
        if len(sys.argv)>2 and ('--grid' in sys.argv or '-g' in sys.argv):
            grid_sampling=True
    return grid_root,scatter_root,phase,grid_sampling    
def get_stations(grid_root,phase='P'):
    """Gets input stations from angle header files 

    Reads the list of angle header files at::

        grid*.phase.*.angle.hdr

    and parses the station names, linking them to the angle files.

    Returns
        list: list of stations and angle file pairs, separated by a ":" and ended by a ";".
    """
    angles=glob.glob(grid_root+'*.'+phase+'.*.angle.hdr')
    stations=[]
    for file in angles:
        sta=file.split('.angle.hdr')[0].split('.')[-1]
        stations.append(sta+':'+file.split('.hdr')[0]+';\n')
    return stations    
def get_scatter(scatter_root):
    """Gets input scatter files in the scatter file path

    Only returns those files which do not have a scatangle file.

    Returns
        list: list of scatter files without a scatangle equivalent.
    """
    return [u for u in glob.glob(scatter_root+'*.scat') if u+'angle' not in glob.glob(scatter_root+'*.scatangle')]    
def write_stations(stations,grid_root):
    """Writes station gile into grid file path as stations.txt file.

    Returns
        str: station file path
    """
    open(os.path.split(grid_root)[0]+'/stations.txt','w').write(''.join(stations))
    return os.path.split(grid_root)[0]+'/stations.txt'    
def get_angles(station_file,scatter_file,grid_sampling):
    """Runs the C++ executable using an os.system call for the input station_file, scatter_file and grid_sampling values

    Returns
        int: output of the os.system call
    """
    return os.system(EXECUTABLE+scatter_file+' '+station_file+' '+str(int(grid_sampling)))
def print_help():
    """Prints command line help message.
    """
    print (__doc__)
def __run__():
    """Main function, called as script

    Uses command line arguments to obtain files and runs the C++ executable for each scatter file.
    For a list of the command line options, use the '-h' flag.
    """
    if len(sys.argv)!=2:
        print ('Requires a control file.')
        print ('For help use -h flag.')
        return
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        return
    else:
        grid_root,scatter_root,phase,grid_sampling=read_control()
        stations=get_stations(grid_root,phase)
        station_file=write_stations(stations,grid_root)
        scatter_files=get_scatter(scatter_root)
        for scatter_file in scatter_files:
            get_angles(station_file,scatter_file,grid_sampling)        
if __name__=="__main__":
    __run__()