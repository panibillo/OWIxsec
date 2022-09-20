'''
Command line interface to cross section module

 
Author
------
Bill Olsen

Version
-------    
0.2  2020-12-05

Notes
-----
o   Command line arguments are defined in xsec_parse_args() using the 
    .add_argument method of the argparse.ArgumentParser.
    
TODO:
    component  A:aquifer (default: include, not-required)
                    draw_openhole: Color outside of the open hole with the aquifer.
                     
'''

import argparse
import numpy as np
from geometry_base import principle_rad_angle

from version import __version__ as XSEC_VERSION

components = """U:labels 
                B:bdrk_depth 
                C:casings  
                F:hydrofrac 
                G:grout 
                H:hole 
                M:pump
                P:perforations 
                S:screen 
                T:stratigraphy
                W:static_water_level)""".split()
#                 L:lithology 
components_dict = {c[0] : c[2:] for c in components}
components_choices = sorted(list(components_dict.keys()))
components_metavar = ' '.join(components_choices)
components_text = 'Components include: ' + \
                  ', '.join((f'{k}({v})' for k,v in components_dict.items()))

components2 = list(components) + ['E:elevation']
components2_dict = {c[0] : c[2:] for c in components2}
components2_choices = sorted(list(components2_dict.keys()))
components2_metavar = ' '.join(components2_choices)
components2_text = 'Components include: ' + \
                  ', '.join((f'{k}({v})' for k,v in components2_dict.items()))

def xsec_parser():
    """
    Command line interface for cross section. 
    
    Returns
    ------- 
    A Namespace with directives for drawing a cross section
    
    Notes
    -------
    o   Utilizes the argparse module to define and document the directives.
    o   For interactive help call with argument ``-h``
    o   Enter list arguments as space separated values. Examples:
        -   A list of three well identifiers would be entered as:
            ``-i 504123 602345 801456``
    """
    parser = argparse.ArgumentParser(description='Generate a well cross section')
    
    parser.add_argument('-V','--version', action='version',
                        version = f"Well Cross-section. Version {XSEC_VERSION}")
    
    # The only required argument is a list of unique well identifiers
    parser.add_argument('-i','--identifiers', 
                        dest='identifiers', 
                        nargs='+', 
                        #type=ascii, 
                        required = True,
                        #metavar='unique_no unique_no ...',  
                        action='store',  
                        help=('Enter the list of Unique Well numbers identifying'  
                              ' which wells to include in the cross section')
                        )
    # The type of section line can be specified as -f or -p.  -f is the default.                     
    parser.add_argument('-f','--fenceline', 
                        dest='isfenceline', 
                        action='store_true',
                        help=('Default. Chooses a fenceline cross-section.'  
                              ' The alternative is --projected.'
                              ' Defaults to --singleton if only one well is drawn')
                        )
    parser.add_argument('-p','--projected', 
                        dest='isprojected', 
                        action='store_true',
                        help=('Optional. Chooses a projected cross-section.'  
                              ' Default is --fenceline.'
                              ' Defaults to --singleton if only one well is drawn')
                        )
    parser.add_argument('-s','--singleton', 
                        dest='issingleton', 
                        action='store_true',
                        help=('Optional. Chooses a singleton cross-section.' 
                              ' Ignored if more than one well identifier is' 
                              ' supplied.'
                              ' Selected automatically if only one well is drawn')
                        )
    # The '--singleton' option is provided for completeness, but really has
    # no effect because it is entirely determined by how many wells from the 
    # list of identifiers is ultimately drawable. It is first set in 
    # xsec_cl.process_cmds, and possibly updated in Xsec_main's __init__ method.
    
    # The user can influence the location and orientation of the section line
    # with varying degrees of control using one or more of the following                    
    parser.add_argument('-l','--linehint', 
                        dest='userline', 
                        nargs='+',  type=float, 
                        #metavar='x1 y1 x2 y2 ...', 
                        action='store', default=None, required = False, 
                        help=('Optional, enter desired sectionline node ' 
                              ' coordinates as a list of x y pairs,'
                              ' e.g. x1 y1 x2 y2 ... .' 
                              ' These are taken as only approximate if a' 
                              ' fenceline is requested, '
                              ' and should describe only a single line segment'  
                              ' if a projected line is requested.')
                        )
    parser.add_argument('-a','--anglehint', 
                        dest='userangledegrees', 
                        type=float, 
                        metavar='degrees',
                        default=None, 
                        required = False,
                        action='store', 
                        help=('Optional, choose directed angle of sectionline'  
                              ' in degrees counterclockwise from East.  The'  
                              ' program will seek a more optimal angle if '  \
                              ' --angle_constraint is set larger than 0.')
                        )
    parser.add_argument('-A','--angle_constraint', 
                        dest='userangle_constraintdegrees', 
                        type=float, 
                        metavar='maxdegrees',
                        default=0, 
                        required = False,
                        action='store', 
                        help=('Optional, constrain sectionline angle to equal' 
                              ' --angle +/- constraint degrees. The default is' 
                              ' 0 degrees.')
                        )
    
    parser.add_argument('-X','--exclude', 
                        dest="exclude",
                        nargs='+',
                        choices=components_choices,
                        #metavar=components_metavar,
                        default=[], 
                        required=False,
                        action='store', 
                        help=('Optional space-separated list of well components'  
                              ' to exclude from the cross section. '  
                              + components_text )
                        )
    parser.add_argument('-I','--includeonly', 
                        dest="includeonly",
                        nargs='+',
                        choices=components_choices,
                        #metavar=components_metavar,
                        default=components_choices,
                        required=False,
                        action='store', 
                        help=('Optional list of well components to include in' 
                              ' the cross section.  If this option is used, then'  
                              ' unlisted components are excluded.'
                              ' Include any components listed as Required.  ' 
                              + components_text )
                        )

    # Required and Not-required options include Elevation along with the  well 
    # components in the Include/Exclude lists
    parser.add_argument('-R','--required', 
                        dest="required",
                        nargs='+',
                        choices=components2_choices,
                        #metavar=components_metavar,
                        default=[],
                        required=False,
                        action='store', 
                        help=('Optional list of well information that must be'  
                              ' present in order for the well to be incluced'  
                              ' in the cross section. Required and Included'  
                              ' options are not interdependent. Default is to'  
                              ' require no components;'  
                              ' Except: Default is to require Elevation unless'
                              ' the drawing is a singleton.  '
                              + components2_text )
                        )

    parser.add_argument('-r','--not_required', 
                        dest="not_required",
                        nargs='+',
                        choices=components2_choices,
                        #metavar=components_metavar,
                        default=[],
                        required=False,
                        action='store', 
                        help=('Optional list of well information that can be'  
                              ' missing without excluding the well from the'  
                              ' cross section. Not-Required and Required'  
                              ' options should be mutually exclusive. In case'
                              ' of conflict, then Not-Required is selected.'
                              '  Default behavior is to not require any'
                              ' components if drawing is a singleton; and to'
                              ' require only Elevation if not a singleton.  '  
                              + components2_text )
                        )
    return parser

def process_cmds(cmds):  
    # After parsing, the type of section line needs to be resolve, in case 
    # the directives are conflicting.
    if len(cmds.identifiers) == 1:
        cmds.isprojected = False 
        cmds.isfenceline = False
        cmds.issingleton = True
        cmds.sectionlinetype = 'singleton'
    elif cmds.isprojected: 
        cmds.isfenceline = False
        cmds.issingleton = False
        cmds.sectionlinetype = 'projected'
    elif cmds.isfenceline: 
        cmds.sectionlinetype = 'fenceline'
        cmds.issingleton = False
    
    # restructure userline into a list of coordinate pairs [(x,y),(x,y), ...]
    if cmds.userline is not None:
        u = cmds.userline
        U = []
        for i in range(0,len(u),2):
            U.append((u[i], u[i+1]))
        cmds.userline = U
    
    # The two options: exclude and includeonly are complementary in concept,
    # so only one is required by the program.  
    # Anticipating that the normal use case will include more and exclude less, 
    # the default includeonly list includes everthing and the default exclude  
    # list is empty. The exclude options are used to update cmds.includeonly;
    # while cmds.exclude is not updated to complement the includeonly options.
    # Therefore, The program should utilize only cmds.includeonly, and should 
    # not reference cmds.exclude; and is enforced by setting the latter to None. 
    if cmds.exclude:
        #exclude = ''.join(cmds.exclude)  # incase they are entered with spaces.
        for a in cmds.exclude:
            if a in cmds.includeonly:
                cmds.includeonly.remove(a)
    cmds.exclude = None
    
    # If an element is both required and not_required, resolve the conflict by
    # making it not_required.
    for a in cmds.not_required:
        if a in cmds.required:
            cmds.required.remove(a)
    
    # User angle hints are given in units of degrees east from north, and have 
    # to be copied to new variables in units of radians counterclockwise from 
    # east.
    cmds.userangle = cmds.userangledegrees
    if cmds.userangle is not None:
        cmds.userangle = principle_rad_angle(np.radians(90-cmds.userangle))

    cmds.userangle_constraint = cmds.userangle_constraintdegrees
    if cmds.userangle_constraintdegrees is not None:
        d = min(np.abs(cmds.userangle_constraintdegrees), 90)
        cmds.userangle_constraint = np.radians(d) 
        
    return cmds

def xsec_parse_args(args=None):
    """
    Process the command line. Entered from the command line or from a script.

    Returns
    -------
    cmds: a dictionary of xsec directives  
    
    Arguments
    ---------
    args : None, str, or list
        - None:   When calling from the command line, the arguments will be 
                  retrieved from the system by the parser.
        - str :   Command line string (when called from another script)
        - list:   Command line string converted to list of string values.
    
    Examples
    --------
    -   Run from the command line:
        > python <your_path>xsec_main.py -i 469382 -R T
    
    -   Run from another script or from the Python prompt:
            from xsec_main import Xsec_main
            from xsec_cl import xsec_parse_args
            command_line_args = "-i 469382 -R T"
    
        +   # Pass command_line_args as a string
            cmds = xsec_parse_args(command_line_args)
            xsec = Xsec_main(cmds)
    
        +   # Pass command_line_args as a list
            cmds = xsec_parse_args(command_line_args.split())
            xsec = Xsec_main(cmds)
    """
    
    parser = xsec_parser()
    if args is None:
        # Handle a call from the command line
        cmds = parser.parse_args()
    elif isinstance(args, str):
        # Handle a call from another module with args = command line string.
        cmds = parser.parse_args(args.split())
    else:
        # Handle a call from another module with args = list of command line args.
        cmds = parser.parse_args(args)
    cmds = process_cmds(cmds)
    return cmds



if __name__ == '__main__':
    """ 
    Demonstrate parsing args as list or as a string
    
    Only one test can be run at a time, for some reason.
    """
    # Pick a test from the list (H, A-E):
    test = 'G'
    
    if test == 'A':
        args = '-i 123456 -X B'
        
    elif test == 'B':
        args = '-f -i 123456 223456 -X C -R E'
        
    elif test == 'C':
        args = '-p -i 123456 223456 -I F -r E'
        
    elif test == 'D':
        args = '-i 123456 223456 -a 36 A 10'
        
    elif test == 'E':
        args = '-i 123456 223456 -l 0 0 100 0'.split()
    
    elif test == 'F':
        args = '-i 123456 -a 120'

    elif test == 'G':
        args = '-i 123456 -a 120 -A 20'

    elif test == 'H':
        xsec_parse_args('-h')

    cmds = xsec_parse_args(args)
    print (f"Test {test}, args=", args)
    for c in cmds._get_kwargs():
        print (c)
        
    print ('///////////////// That concludes xsec_cl script ///////////////////')    