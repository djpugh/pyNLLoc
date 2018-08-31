#!/usr/bin/python
"""XYZ2Angle
****************************

XYZ2Angle converts input x,  y, z, values in km or latitude longitude depth value to take-off angles and azimuths for the set of recievers.

It is a python wrapper for the C++ executable compiled from getAngles.cpp. This uses some of the functions in the NonLinLoc code (specifically GridLib and it's dependencies)
to convert the a given x,y,z location into take-off angle samples for all stations. 

To compile the executable, it is necesary to compile some other components into object code. For an example, please see the make_angles.sh file, or the README.

This uses Scat2Angle to convert XYZ coordinates into a location file, and then evaluates the take-off angles.

Command line flags
*********************************
To obtain a list of the command line flags use the -h flag::

    $~ XYZ2Angle -h

This will provide a list of the arguments and their usage.


Running from the command line
*********************************
To run from the command line on  linux/*nix  it is necessary to make sure that the XYZ2Angle script installed is on the path,
or to set up a manual alias/script, e.g. for bash::

    python -c "import XYZ2Angle;XYZ2Angle.__run__()" $*


On windows (Requires NLLoc programs to be installed on windows too) using powershell add the following commandlet to your profile (for information on customizing your powershell profile see: http://www.howtogeek.com/50236/customizing-your-powershell-profile/)::

    function XYZ2Angle{
        $script={
            python -c "import XYZ2Angle;XYZ2Angle.__run__()" $args
        }
        Invoke-Command -ScriptBlock $script -ArgumentList $args
    }



Running from within python
*********************************
To run from within python, (assuming the module is on your PYTHONPATH)::

    >>import XYZ2Angle
    >>XYZ2Angle.__run__()

This will run with the default options, although these can be customized - see the XYZ2Angle.__run__ docstrings.
 
"""
try:
    import argparse
    _ARGPARSE=True
except:
    _ARGPARSE=False
try:
    from .Scat2Angle import write_stations, get_stations
    from .Scat2Angle import get_angles as get_scat_angles
except:
    from Scat2Angle import write_stations, get_stations
    from Scat2Angle import get_angles as get_scat_angles

import struct,shutil,os,glob,textwrap
def make_scatter_file(x,y,z,endian='='):
    """Make the scatter file for the x y z coordinates

    Args
        x: float x coordinate
        y: float y coordinate
        z: float z coordinate

    Keyword Args
        endian: endian value for binary numbers

    Returns:
        str: 'xyz.scat' scatter file name

    """
    import struct
    fid=open('xyz.scat','wb')
    fid.write(struct.pack(endian+'I',1))
    #Dummy values
    fid.write(struct.pack(endian+'III',1,1,1))
    #First node
    fid.write(struct.pack(endian+'ffff',x,y,z,1))
    fid.close()
    return 'xyz.scat'
def get_angles(x,y,z,grid_path='./grid/',endian='=',phase='P'):
    """Runs the conversion of x y z to angles

    Args
        x: float x coordinate
        y: float y coordinate
        z: float z coordinate

    Keyword Args
        grid_path: str path to grid files for angle calculation
        endian: endian value
        phase: str phase to calculate angles for
    """
    station_file=write_stations(get_stations(grid_path,phase),grid_path)
    scatter_file=make_scatter_file(x,y,z,endian)
    get_scat_angles(station_file,scatter_file)
    os.remove('xyz.scat')
    shutil.move('xyz.scatangle','xyz.angle')
def latlon_xyz(latitude,longitude,depth,latitude_0,longitude_0,latitude_1,latitude_2):
    """Converts latitude and longitude into x y z

    Uses pyproj abd lambert projection to convert the coordinates using a given origin.

    Args
        latitude: float latitude in degrees
        longitude: float longitude in degrees
        depth: float depth in km
        latitude_0: float latitude of origin in degrees
        longitude_0: float longitude of origin in degrees 
        latitude_1: float latitude of first standard parallel in degrees 
        latitude_2: float latitude of second standard parallel in degrees 

    Returns
        (float,float,float): tuple of x, y, z coordinates in km from latitude_0 and longitude_0 origin
    """
    from pyproj import Proj
    p=Proj('+proj=lcc +lat_0='+str(latitude_0)+' +lon_0='+str(longitude_0)+' +lat_1='+str(latitude_1)+' +lat_2='+str(latitude_2),ellps='WGS84')
    [x_0,y_0]=p(float(longitude_0),float(latitude_0))
    [x,y]=p(longitude,latitude)
    return (x-x_0)/1000.,(y-y_0)/1000.,depth
def __run__():
    """Main function for running XYZ2Angle from command line.

    For command line options, use the '-h' flag.
    """
    options=__parser__()
    if os.path.isdir(options['grid_path']):
        options['grid_path']=options['grid_path'].rstrip(os.path.sep)+os.path.sep
    if not options['xyz']:
        header_file=glob.glob(options['grid_path']+'*.hdr')[0]
        lat0,lon0,lat1,lat2=parse_header_file(header_file)
        [options['X'],options['Y'],options['Z']]=latlon_xyz(options['X'],options['Y'],options['Z'],lat0,lon0,lat1,lat2)
    get_angles(options['X'],options['Y'],options['Z'],options['grid_path'],options['endian'],options['phase'])
    output=open('xyz.angle').readlines()
    print ('Results for Location:\nX:'+str(options['X'])+' km  Y:'+str(options['Y'])+' km  Z:'+str(options['Z'])+' km\n')
    print (''.join(output[1:]))
def time():
    raise NotImplementedError()
    # print ('To use XYZ2Time')
def parse_header_file(filename):
    """Parses hdr file for grid origin and parallels (Lambert transform)

    Args
        filename: str header filename

    Returns
        (float,float,float,float): tuple of floats for latitude and longitude of the origin and
                                     the latitiudes of the first and second standard parallels
    """
    lines=open(filename).readlines()
    latitude_0=lines[2].split()[5]
    longitude_0=lines[2].split()[7]
    latitude_1=lines[2].split()[9]
    latitude_2=lines[2].split()[11]
    return latitude_0,longitude_0,latitude_1,latitude_2
def __parser__(input_args=False):
    """Command line parser for XYZ2Angle

    Keyword Args
        input_args: list of input arguments (defaults to sys.argv)

    Returns
        dict: dictionary of selected command line options.
    """
    description="""XYZ2Angle - Wrapper to convert lat/lon/depth or XYZ coordinates to angles using NLLoc by David Pugh (Bullard Laboratories, Department of Earth Sciences, University of Cambridge) 
    """
    optparsedescription="""Arguments are set as below, syntax is -gTest or --gridpath=Test
    """
    argparsedescription="""Arguments are set as below, syntax is -gTest or -g Test
    """ 
    if _ARGPARSE:
        class IndentedHelpFormatterWithNL(argparse.RawDescriptionHelpFormatter):
            def _format_action(self, action):
                # determine the required width and the entry label
                help_position = min(self._action_max_length + 2,
                                    self._max_help_position)
                help_width = self._width - help_position
                action_width = help_position - self._current_indent - 2
                action_header = self._format_action_invocation(action)

                # ho nelp; start on same line and add a final newline
                if not action.help:
                    tup = self._current_indent, '', action_header
                    action_header = '%*s%s\n' % tup

                # short action name; start on the same line and pad two spaces
                elif len(action_header) <= action_width:
                    tup = self._current_indent, '', action_width, action_header
                    action_header = '%*s%-*s  ' % tup
                    indent_first = 0

                # long action name; start on the next line
                else:
                    tup = self._current_indent, '', action_header
                    action_header = '%*s%s\n' % tup
                    indent_first = help_position

                # collect the pieces of the action help
                parts = [action_header]
                # if there was help for the action, add lines of help text
                if action.help:
                    help_text = self._expand_help(action)
                    help_lines = []
                    for para in help_text.split("\n"):
                        if not len(textwrap.wrap(para, help_width)):
                            help_lines.extend(' ')
                        else:
                            help_lines.extend(textwrap.wrap(para, help_width))

                    help_lines.extend(' ')
                    help_lines.extend(' ')
                    parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
                    for line in help_lines[1:]:
                        parts.append('%*s%s\n' % (help_position, '', line))

                # or add a newline if the description doesn't end with one
                elif not action_header.endswith('\n'):
                    parts.append('\n')

                # if there are any sub-actions, add their help as well
                for subaction in self._iter_indented_subactions(action):
                    parts.append(self._format_action(subaction))

                # return a single string
                return self._join_parts(parts)
        parser=argparse.ArgumentParser(prog='XYZ2Angle',description=description+argparsedescription,formatter_class=IndentedHelpFormatterWithNL)
        parser.add_argument('X',type=float,help="Latitude in degrees/X coordinate in km (-x flag required)")
        parser.add_argument('Y',type=float,help="Longitude in degrees/Y coordinate in km (-x flag required)")
        parser.add_argument('Z',type=float,help="Depth in km/Z coordinate in km (-x flag required)")
        parser.add_argument("-g","--gridpath","--grid_path",help='Grid files path use for the location,defaults to  current directory',dest='grid_path',default='./')
        parser.add_argument("-x","--xyz",help='Using XYZ coordinates in km relative to geographic origin',action='store_true',dest='xyz',default=False)
        parser.add_argument("-e","--endian",help='Endian value to use',choices=['=','<','>','@','!'],dest='endian',default='=')
        parser.add_argument("-p","--phase",help="Set grid phase to use e.g. P or S",dest='phase',default='P')
        if input_args:
            options=parser.parse_args(input_args)
        else:
            options=parser.parse_args()
        options=vars(options)
    else:
        class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):
            def format_description(self, description):
                if not description: return ""
                desc_width = self.width - self.current_indent
                indent = " "*self.current_indent
            # the above is still the same
                bits = description.split('\n')
                formatted_bits = [
                  textwrap.fill(bit,
                    desc_width,
                    initial_indent=indent,
                    subsequent_indent=indent)
                  for bit in bits]
                result = "\n".join(formatted_bits) + "\n"
                return result

            def format_option(self, option):
                # The help for each option consists of two parts:
                #   * the opt strings and metavars
                #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
                #   * the user-supplied help string
                #   eg. ("turn on expert mode", "read data from FILENAME")
                #
                # If possible, we write both of these on the same line:
                #   -x    turn on expert mode
                #
                # But if the opt string list is too long, we put the help
                # string on a second line, indented to the same column it would
                # start in if it fit on the first line.
                #   -fFILENAME, --file=FILENAME
                #       read data from FILENAME
                result = []
                opts = self.option_strings[option]
                opt_width = self.help_position - self.current_indent - 2
                if len(opts) > opt_width:
                  opts = "%*s%s\n" % (self.current_indent, "", opts)
                  indent_first = self.help_position
                else: # start help on same line as opts
                  opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
                  indent_first = 0
                result.append(opts)
                if option.help:
                  help_text = self.expand_default(option)
                # Everything is the same up through here
                  help_lines = []
                  for para in help_text.split("\n"):
                    if not len(textwrap.wrap(para, self.help_width)):
                        help_lines.extend(' ')
                    else:
                        help_lines.extend(textwrap.wrap(para, self.help_width))
                  help_lines.extend(' ')
                  help_lines.extend(' ')
                # Everything is the same after here
                  result.append("%*s%s\n" % (
                    indent_first, "", help_lines[0]))
                  result.extend(["%*s%s\n" % (self.help_position, "", line)
                    for line in help_lines[1:]])
                elif opts[-1] != "\n":
                  result.append("\n")
                return "".join(result)
        parser=optparse.OptionParser(prog='XYZ2Angle',description=description+optparsedescription,formatter_class=IndentedHelpFormatterWithNL)
        parser.add_option('X',type=float,help="Latitude in degrees/X coordinate in km (-x flag required)")
        parser.add_option('Y',type=float,help="Longitude in degrees/Y coordinate in km (-x flag required)")
        parser.add_option('Z',type=float,help="Depth in km/Z coordinate in km (-x flag required)")
        parser.add_option("-g","--gridpath","--grid_path",help='Grid files path use for the location,defaults to  current directory',dest='grid_path',default=False)
        parser.add_option("-x","--xyz",help='Using XYZ coordinates in km relative to geographic origin',action='store_true',dest='XYZ',default=False)
        parser.add_option("-e","--endian",help='Endian value to use',choices=['=','<','>','@','!'],dest='endian',default='=')
        parser.add_option("-p","--phase",help="Set grid  phase to use e.g. P or S",dest='phase',default='P')
        if input_args and len(input_args):
            (options,args)=parser.parse_args(input_args)
        else:
            (options,args)=parser.parse_args()
        options=vars(options)        
    return options        
if __name__=="__main__":
    __run__()

