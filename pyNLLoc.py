#!/usr/bin/env python
"""pyNLLoc
=================================
Python module for running NonLinLoc on a cluster by David J Pugh (Bullard Laboratories, Department of Earth Sciences, University of Cambridge)

This module allows the location program NonLinLoc to be easily run from the command line, including for looping over different velocity models, and running Scat2Angle to convert the scatter file to an angle scatter file.

The code can be called from the command line directly or from within python itself (see below)

File Preparation
*********************************
The required file structure for running pyNLLoc is simple. The target directory must contain the control files (.in) for the run along with the observation file (.out), either in the target directory or ./run and ./obs respectively.
If there are multiple observation files, these are appended together to form a single obs.out file in ./obs

There must be appropriate control file(s), either for each program containing all the control commands:
    nlloc_control_vel2grid.in
    nlloc_control_grid2time_P.in
    nlloc_control_grid2time_S.in
    nlloc_control_nlloc.in
or:
    nlloc_control_vel2grid.in
    nlloc_control_grid2time.in
    nlloc_control_nlloc.in

or a single control file with all the control structure:
    nlloc_control.in

A standard NonLinLoc folder structure will be constructed in that directory e.g.::
    ./run - for control files etc
    ./loc - for location (output) files
    ./time - for station time and angle grid files
    ./model - for the velocity model grid files
    ./obs - for the observation files
And the control files will be moved and written for each program, so if any manual editing is done between multiple runs, these will be the ones used by the program.

This script will edit the control files and tweak any file paths to the full file path. 
If the stations or model are accessed using and INCLUDE command in the appropriate control file, they must also be present in the target directory  or ./run with appropriate formats(.sta and .mod/.vel). If there are multiple files of a given format in the target directory or ./run, problems can occur.
If running over multiple velocity models, the velocity models must not be hard coded into the control file but includes using INCLUDE in the control file, and included in a separate folder to the target directory (e.g. ./models)

An example file structure is:
    ./obs.out
    ./nlloc_control_vel2grid.in
    ./nlloc_control_grid2time_P.in
    ./nlloc_control_grid2time_S.in
    ./nlloc_control_nlloc.in
    ./stations.sta
    ./model.vel

Which will then be changed to 
    ./obs.out

    ./obs
        ./obs/obs.out

    ./run
        ./run/nlloc_control_vel2grid.in
        ./run/nlloc_control_grid2time_P.in
        ./run/nlloc_control_grid2time_S.in
        ./run/nlloc_control_nlloc.in
        ./run/stations.sta
        ./run/model.vel

    ./loc
        -output files

    ./time
        -station grid  files

    ./model
        -model grid files

If a single control file is used the example file structure is: 
    ./obs.out
    ./nlloc_control.in
    ./stations.sta
    ./model.vel

Which will then be changed to:
    ./obs.out

    ./obs
        ./obs/obs.out

    ./run
        ./run/nlloc_control_vel2grid.in
        ./run/nlloc_control_grid2time_P.in
        ./run/nlloc_control_grid2time_S.in
        ./run/nlloc_control_nlloc.in
        ./run/stations.sta
        ./run/model.vel

    ./loc
        -output files

    ./time
        -station grid  files

    ./model
        -model grid files

Note that the single control file is changed to one for each program

Running on a cluster
*********************************

It is also possible to run this code on a cluster using qsub and pyqsub. This can be called from the commandline using a flag:

    * -q, --qsub, --pbs

This runs using a set of default parameters, however it is also possible to adjust these parameters using commandline flags (use -h flag for help and usage)



Command line flags
*********************************
To obtain a list of the command line flags use the -h flag::

    $~ pyNLLoc -h

This will provide a list of the arguments and their usage.


Running from the command line
*********************************
To run from the command line on  linux/*nix  it is necessary to make sure that the pyNLLoc script installed is on the path,
or to set up a manual alias/script, e.g. for bash::

    python -c "import pyNLLoc;pyNLLoc.__run__()" $*


On windows (Requires NLLoc programs to be installed on windows too) using powershell add the following commandlet to your profile (for information on customizing your powershell profile see: http://www.howtogeek.com/50236/customizing-your-powershell-profile/)::

    function pyNLLoc{
        $script={
            python -c "import pyNLLoc;pyNLLoc.__run__()" $args
        }
        Invoke-Command -ScriptBlock $script -ArgumentList $args
    }



Running from within python
*********************************
To run from within python, (assuming the module is on your PYTHONPATH)::

    >>import pyNLLoc
    >>pyNLLoc.__run__()

This will run with the default options, although these can be customized - see the pyNLLoc.__run__ docstrings.
 
"""
try:
    import argparse
    _ARGPARSE=True
except:
    _ARGPARSE=False
import optparse,os,glob,stat,sys,shutil,subprocess,textwrap
import pyqsub#python module for cluster job submission using qsub.
from pyqsub import isPath
def _make_folders(target='.'):
    os.chdir(target)
    try:
        os.mkdir('loc')
    except OSError:
        pass
    try:
        os.mkdir('time')
    except OSError:
        pass
    try:
        os.mkdir('model')
    except OSError:
        pass
    try:
        os.mkdir('run')
    except OSError:
        pass
    try:
        os.mkdir('obs')
    except OSError:
        pass
    #Move files
    Data=[]
    for data_file in glob.glob('*.out'):
        Data.extend(open(data_file).readlines())
        Data.append('\n')
    open('obs'+os.path.sep+'obs.out','w').write(''.join(Data))
    controlFiles=glob.glob('*.in')
    controlFiles.extend(glob.glob('*.vel'))
    controlFiles.extend(glob.glob('*.mod'))
    controlFiles.extend(glob.glob('*.sta'))
    for controlFile in controlFiles:
        shutil.move(controlFile,'run'+os.path.sep+controlFile)
def _check_control_files(CWD,options=False,model_name=False):
    obsFile=glob.glob('obs/*.out')[0].split('/')[1]
    #Vel2Grid    
    if os.path.exists('run/nlloc_control_vel2grid.in'):
        control_file='run/nlloc_control_vel2grid.in'
    elif os.path.exists('run/nlloc_control.in'):
        control_file='run/nlloc_control.in'
    else:
        raise ValueError('Missing Control File - Vel2Grid')
    control=_read_control_file(control_file)
    for i,line in enumerate(control):
        if 'VGOUT' in line:
            control[i]="VGOUT "+CWD+'/model/velocity\n'
        if 'INCLUDE' in line:
            if model_name:
                control[i]='INCLUDE '+model_name+'\n'
            else:
                velmodFiles=[]
                velmodFiles.extend(glob.glob('run'+os.path.sep+'*.vel'))
                velmodFiles.extend(glob.glob('run'+os.path.sep+'*.mod'))
                velmodFiles.extend(glob.glob('run'+os.path.sep+'velmod.txt'))
                velmod=velmodFiles[0]
                control[i]='INCLUDE '+CWD+os.path.sep+velmod+'\n'
    _write_control_file(control,'run/nlloc_control_vel2grid.in')
    #Grid2Time P    
    if os.path.exists('run/nlloc_control_grid2time_P.in'):
        control_file='run/nlloc_control_grid2time_P.in'
    elif os.path.exists('run/nlloc_control_grid2time.in'):
        control_file='run/nlloc_control_grid2time.in'
    elif os.path.exists('run/nlloc_control.in'):
        control_file='run/nlloc_control.in'
    else:
        raise ValueError('Missing Control File - Grid2Time P')
    control=_read_control_file(control_file)
    for i,line in enumerate(control):
        if 'GTFILES' in line:
            control[i]="GTFILES "+CWD+'/model/velocity '+CWD+'/time/grid P 0\n'
        if 'INCLUDE' in line:
            stationsFiles=glob.glob('run'+os.path.sep+'*.sta')
            stationsFiles.extend(glob.glob('run'+os.path.sep+'stations_grid.txt'))
            stations=stationsFiles[0]
            control[i]='INCLUDE '+CWD+os.path.sep+stations+'\n'
    _write_control_file(control,'run/nlloc_control_grid2time_P.in')
    #Grid2Time S
    if os.path.exists('run/nlloc_control_grid2time_S.in'):
        control_file='run/nlloc_control_grid2time_S.in'
    elif os.path.exists('run/nlloc_control_grid2time.in'):
        control_file='run/nlloc_control_grid2time.in'
    elif os.path.exists('run/nlloc_control.in'):
        control_file='run/nlloc_control.in'
    else:
        raise ValueError('Missing control File - Grid2Time S')
    control=_read_control_file(control_file)
    for i,line in enumerate(control):
        if 'GTFILES' in line:
            control[i]="GTFILES "+CWD+'/model/velocity '+CWD+'/time/grid S 0\n'
        if 'INCLUDE' in line:
            stationsFiles=glob.glob('run'+os.path.sep+'*.sta')
            stationsFiles.extend(glob.glob('run'+os.path.sep+'stations_grid.txt'))
            stations=stationsFiles[0]
            control[i]='INCLUDE '+CWD+os.path.sep+stations+'\n'
    _write_control_file(control,'run/nlloc_control_grid2time_S.in')
    #NLLoc
    if os.path.exists('run/nlloc_control_nlloc.in'):
        control_file='run/nlloc_control_nlloc.in'
    elif os.path.exists('run/nlloc_control.in'):
        control_file='run/nlloc_control.in'
    else:
        raise ValueError('Missing control File - NLLoc')
    control=_read_control_file('run/nlloc_control_nlloc.in')
    for i,line in enumerate(control):
        if 'LOCSIG' in line:
            control[i]="LOCSIG "+obsFile.split('.')[0]
        if 'LOCFILES' in line:
            if model_name:
                control[i]='LOCFILES '+CWD+'/obs/'+obsFile+' NLLOC_OBS '+CWD+'/time/grid '+CWD+'/loc/'+obsFile.split('.')[0]+'.'+os.path.splitext(os.path.split(model_name)[1])[0]+' 0\n'
            else:
                control[i]='LOCFILES '+CWD+'/obs/'+obsFile+' NLLOC_OBS '+CWD+'/time/grid '+CWD+'/loc/'+obsFile.split('.')[0]+' 0\n'
    _write_control_file(control,'run/nlloc_control_nlloc.in')
    #Scat2Angle
    if options and not options['NoScatter']:
        if model_name:
                control=[CWD+'/time/grid\n',CWD+'/loc/'+obsFile.split('.')[0]+'.'+os.path.splitext(os.path.split(model_name)[1])[0]+'\n'  ]
        else:
            control=[CWD+'/time/grid\n',CWD+'/loc/'+obsFile.split('.')[0]+'\n']    
        _write_control_file(control,'run/nlloc_control_scat2angle.in')
    try:
        os.remove('run/nlloc_control.in')
    except:
        pass
    try:
        os.remove('run/nlloc_control_grid2time.in')
    except:
        pass
def _write_control_file(control,filename):
        fcontrol=open(filename,'w')
        fcontrol.write(''.join(control))
        fcontrol.close()
        os.chmod(filename, stat.S_IRWXO| stat.S_IRWXG|stat.S_IRWXU)
def _read_control_file(filename):
    fcontrol=open(filename)
    control=fcontrol.readlines()
    fcontrol.close()
    return control

def _run_nlloc(options=False):
    """Runs the NonLinLoc programs in the target directory. Needs to be preceded by a call to _setup.
    """
    if options and options['models']:
        models=glob.glob(os.path.splitext(options['models'])[0]+'*.mod')
        for model in models:
            print 'Runing model: '+model
            _check_control_files('.',options,model_name=model)
            options['models']=False
            _run_nlloc(options)
    else:
        Vel2Grid("run/nlloc_control_vel2grid.in")
        Grid2Time("run/nlloc_control_grid2time_P.in")
        Grid2Time("run/nlloc_control_grid2time_S.in")
        NLLoc("run/nlloc_control_nlloc.in")
        if options and not options['NoScatter']:
            Scat2Angle("run/nlloc_control_scat2angle.in")
def Vel2Grid(control_file="run/nlloc_control_vel2grid.in"):
    process=subprocess.Popen(['Vel2Grid',control_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err=process.communicate()
    print 'Vel2Grid\n\n'+out+str(err)
def Grid2Time(control_file="run/nlloc_control_grid2time.in"):
    process=subprocess.Popen(['Grid2Time',control_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err=process.communicate()
    print 'Grid2Time\n\n'+out+str(err)
def NLLoc(control_file="run/nlloc_control_nlloc.in"):
    process=subprocess.Popen(['NLLoc',control_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err=process.communicate()
    print 'NLLoc\n\n'+out+str(err)
def Scat2Angle(control_file="run/nlloc_control_scat2angle.in"):
    process=subprocess.Popen(['Scat2Angle',control_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err=process.communicate()
    print 'Scat2Angle\n\n'+out+str(err)
    
def _setup(target='.',options=False):   
    """Sets up the NonLinLoc directory structure and control files in the target directory. Needs to be called before _run_nlloc.
    """
    os.chdir(target)
    CWD=os.getcwd()
    _make_folders(target)
    _check_control_files(CWD,options)   
def __run__(target='.',inputArgs=False):
    """Main code for running pyNLLoc

    Args
        target - str target directory [default ='.']
        inputArgs - list of command line flags [default=False] for more information on the command line flags use -h as a flag.
    """
    options,optionsMap=_parser(inputArgs)
    if options['qsub']:
        optionsMap['DataPath']=optionsMap['DATAPATH']
        return pyqsub.submit(options,optionsMap,__name__)
    else:
        for key in options.keys():
            if 'qsub' in key:
                options.pop(key)
        _setup(options['DataPath'],options)
        _run_nlloc(options)


def _parser(inputArgs=False):
    description=__doc__+"\n\nCommand Line Arguments\n*********************************\n"
    optparsedescription="""Arguments are set as below, syntax is -dTest or --datafile=Test
"""
    argparsedescription="""Arguments are set as below, syntax is -dTest or -d Test
"""
    #Set up qsub defaults
    default_nodes=1
    default_ppn=1
    default_pmem=4
    default_walltime="24:00:00"
    default_queue='batch' 
    optionsMap={}   
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
        parser=argparse.ArgumentParser(prog='pyNLLoc',description=description+argparsedescription,formatter_class=IndentedHelpFormatterWithNL)
        parser.add_argument('DataPath',type=isPath,help="Target Path use for the location, optional but must be specified either as a positional argument or as an optional argument (see -d below) If not specified defaults to all current directory",nargs="?")
        parser.add_argument("-d","--datapath","--data_path",help='Target Path use for the location, optional but must be specified either as a positional argument or as an optional argument (see -d below) If not specified defaults to all current directory',type=isPath,dest='DATAPATH',default=False)
        parser.add_argument("-n","--noscatter","--no_scatter",help='Do not run scatter to angles conversion',action='store_true',dest='NoScatter',default=False)
        parser.add_argument("-m","--models_path","--multiple_models_path",help='Run inversion with multiple models. Model file endings are .mod. [default=False]',dest='models',default=False)
        group=parser.add_argument_group('Cluster',description="\nCommands for using pyNLLoc on a cluster environment using qsub/PBS")
        group=pyqsub.parser_group(module_name='pyNLLoc',group=group,default_nodes=default_nodes,default_ppn=default_ppn,default_pmem=default_pmem,default_walltime=default_walltime,default_queue=default_queue) 
        for option in parser._actions:
            if len(option.option_strings):
                i=0
                while i<len(option.option_strings) and '--' not in option.option_strings[i]:
                    i+=1
                optionsMap[option.dest]=option.option_strings[i]
        #For testing
        if inputArgs:
            options=parser.parse_args(inputArgs)
        else:
            options=parser.parse_args()
        options=vars(options)
        if not options['DataPath'] and not options['DATAPATH']:
            print "Data file not provided, using current directory."
            options['DataPath']=os.path.abspath('./')
        elif options['DataPath'] and options['DATAPATH']:
            parser.error("Multiple data files specified.")
        elif options['DATAPATH']:
            options['DataPath']=options['DATAPATH']
        options.pop('DATAPATH')
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
        parser=optparse.OptionParser(prog='pyNLLoc',description=description+argparsedescription,formatter=IndentedHelpFormatterWithNL(),usage="%prog [options]\nUse -h to get more information")
        parser.add_option("-d","--datapath","--data_path",help='Target Path use for the location, optional but must be specified either as a positional argument or as an optional argument (see -d below) If not specified defaults to all current directory',dest='DATAPATH',default=False)
        parser.add_option("-n","--noscatter","--no_scatter",help='Do not run scatter to angles conversion',action='store_true',dest='NoScatter',default=False)
        parser.add_option("-m","--models_path","--multiple_models_path",help='Run inversion with multiple models. Model file endings are .mod. [default=False]',dest='models',default=False)
        group=optparse.OptionGroup(parser,'Cluster',description="\nCommands for using pyNLLoc on a cluster environment using qsub/PBS")
        group=pyqsub.parser_group(module_name='pyNLLoc',group=group,default_nodes=default_nodes,default_ppn=default_ppn,default_pmem=default_pmem,default_walltime=default_walltime,default_queue=default_queue) 
        parser.add_option_group(group)    
        for option in parser.option_list:
            optionsMap[option.dest]=option.get_opt_string()
        if inputArgs and len(inputArgs):
            (options,args)=parser.parse_args(inputArgs)
        else:
            (options,args)=parser.parse_args()
        options=vars(options)
        options['DataPath']=False
        if len(args):
            options['DataPath']=args[0]
        options['DataPath']=False
        if len(args):
            options['DataPath']=args[0]
        if not options['DataPath'] and not options['DATAPATH']:
            print "Data file not provided, using current directory."
            options['DataPath']=os.path.abspath('./')
        elif options['DataPath'] and options['DATAPATH']:
            parser.error("Multiple data files specified.")
        elif options['DATAPATH']:
            options['DataPath']=options['DATAPATH']
        options.pop('DATAPATH')    
        try:
            options['DataPath']=isPath(options['DataPath'])
        except ValueError:
            parser.error("Data file: \""+options['DataPath']+"\" does not exist")
    if options['models']:
        if os.path.isdir(os.path.abspath(os.path.split(options['models'])[0])):
            options['models']=os.path.abspath(os.path.split(options['models'])[0])+os.path.sep+os.path.split(options['models'])[1]
            if os.path.isdir(os.path.split(options['models'])[1]):
                options['models']+=os.path.sep
        else:
            parser.error('models path does not exist')
    if options['qsub']:
        if  len([key for key in os.environ.keys() if 'PBS' in key and key!='PBS_DEFAULT']):
            parser.error('Cannot submit as already on cluster') 
        try:
            ret=subprocess.call(["which","qsub"])
        except:
            ret=1
        if ret:
            parser.error('Could not find qsub - cannot run in cluster mode')        
        if not options['qsub_pmem'] or options['qsub_pmem']<=0:
            options['PMem']=8 # set to use 8GB for sampling...
            options['qsub_pmem']=0
        if options['qsub_walltime']:
            if len(options['qsub_walltime'].split(':'))!=3:
                parser.error('Walltime '+options['qsub_walltime']+' format incorrect, needs to be HH:MM:SS')
            walltime=60.*60.*int(options['qsub_walltime'].split(':')[0])+60.*int(options['qsub_walltime'].split(':')[1])+int(options['qsub_walltime'].split(':')[2])
    return options,optionsMap

if __name__=='__main__':
    __run__()
