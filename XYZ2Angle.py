#!/usr/bin/python
"""XYZ2Angle
======================

XYZ2Angle is a python wrapper for the C++ executable compiled from getAngles.cpp. 
This uses some of the functions in the NonLinLoc code (specifically GridLib and it's dependencies)
to convert the a given x,y,z location into take-off angle samples for all stations. 

To compile the executable, it is necesary to compile some other components into object code. For an example, please see the make_angles.sh file, or the README.

This uses Scat2Angle to convert XYZ coordinates into a location file, and then evaluates the take-off angles.


"""
try:
    import argparse
    _ARGPARSE=True
except:
    _ARGPARSE=False
import Scat2Angle,struct,shutil,os,glob,textwrap
def makeScatter(x,y,z,endian='='):
    import struct
    fid=open('xyz.scat','wb')
    fid.write(struct.pack(endian+'I',1))
    #Dummy values
    fid.write(struct.pack(endian+'III',1,1,1))
    #First node
    fid.write(struct.pack(endian+'ffff',x,y,z,1))
    fid.close()
    return 'xyz.scat'
def run(x,y,z,gridPath='./time/',endian='=',mode='P'):
    stationFile=Scat2Angle.writeStations(Scat2Angle.getStations(gridPath,mode),gridPath)
    scatterFile=makeScatter(x,y,z,endian)
    Scat2Angle.run(stationFile,scatterFile)
    os.remove('xyz.scat')
    shutil.move('xyz.scatangle','xyz.angle')
def latlon2xyz(lat,lon,depth,lat0,lon0,lat1,lat2):
    from pyproj import Proj
    p=Proj('+proj=lcc +lat_0='+lat0+' +lon_0='+lon0+' +lat_1='+lat1+' +lat_2='+lat2,ellps='WGS84')
    [x0,y0]=p(float(lon0),float(lat0))
    [x,y]=p(lon,lat)
    return (x-x0)/1000,(y-y0)/1000,depth
def __main__():
    options=__parser__()
    if os.path.isdir(options['gridpath']):
        options['gridpath']=options['gridpath'].rstrip(os.path.sep)+os.path.sep
    if not options['xyz']:
        headerFile=glob.glob(options['gridpath']+'*.hdr')[0]
        lat0,lon0,lat1,lat2=__headerparser__(headerFile)
        [options['X'],options['Y'],options['Z']]=latlon2xyz(options['X'],options['Y'],options['Z'],lat0,lon0,lat1,lat2)
    run(options['X'],options['Y'],options['Z'],options['gridpath'],options['endian'],options['mode'])
    output=open('xyz.angle').readlines()
    print 'Results for Location:\nX:'+str(options['X'])+' km  Y:'+str(options['Y'])+' km  Z:'+str(options['Z'])+' km\n'
    print ''.join(output[1:])
def __headerparser__(fileName):
    lines=open(fileName).readlines()
    lat0=lines[2].split()[5]
    lon0=lines[2].split()[7]
    lat1=lines[2].split()[9]
    lat2=lines[2].split()[11]
    return lat0,lon0,lat1,lat2
def isPath(string):
    if not string:
        return string        
    elif ',' in string:
        #list
        files=string.lstrip('[').rstrip(']').split(',')
        for i,f in enumerate(files):
            files[i]=isPath(f)
        return files
    elif string and '*' in string and os.path.exists(os.path.abspath(os.path.split(string)[0])):
        return glob.glob(os.path.abspath(os.path.split(string)[0])+os.path.sep+os.path.split(string)[1])
    elif string and '*' not in string and os.path.exists(os.path.abspath(string)):
        return os.path.abspath(string)
    if _ARGPARSE:
        raise argparse.ArgumentTypeError('Path: "'+string+'" does not exist')
    else:
        raise ValueError('Path: "'+string+'" does not exist')
def __parser__(inputArgs=False):
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
        parser.add_argument("-g","--gridpath","--grid_path",help='Grid files path use for the location,defaults to  current directory',dest='gridpath',default='./')
        parser.add_argument("-x","--xyz",help='Using XYZ coordinates in km relative to geographic origin',action='store_true',dest='xyz',default=False)
        parser.add_argument("-e","--endian",help='Endian value to use',choices=['=','<','>','@','!'],dest='endian',default='=')
        parser.add_argument("-m","--mode",help="Set grid phase mode to use e.g. P or S",dest='mode',default='P')
        if inputArgs:
            options=parser.parse_args(inputArgs)
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
        parser.add_option("-g","--gridpath","--grid_path",help='Grid files path use for the location,defaults to  current directory',dest='gridpath',default=False)
        parser.add_option("-x","--xyz",help='Using XYZ coordinates in km relative to geographic origin',action='store_true',dest='XYZ',default=False)
        parser.add_option("-e","--endian",help='Endian value to use',choices=['=','<','>','@','!'],dest='endian',default='=')
        parser.add_option("-m","--mode",help="Set grid phase mode to use e.g. P or S",dest='mode',default='P')
        if inputArgs and len(inputArgs):
            (options,args)=parser.parse_args(inputArgs)
        else:
            (options,args)=parser.parse_args()
        options=vars(options)        
    return options  

