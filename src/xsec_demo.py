#!/bin/env python3
'''
Created on May 24, 2021

Test runs for xsec

These tests do 3 things:
    Compose a set of command line argurments.
    Call xsec_parse_args(argurments) to obtain a cmds object.
    Call xsec_main(cmds) to generate a cross section.
    
Remember that arguments must coincide with the xsec_data_<source> in use.

@author: Bill
'''
import os

from xsec_cl import xsec_parse_args
from xsec_main import Xsec_main

welldata_db = os.path.abspath("../demo_data/OWI_demo.sqlite")
assert os.path.exists(welldata_db), f"{welldata_db} missing, it is not under version control"

legend_db = os.path.abspath("../demo_data/xsec_legend.sqlite")
assert os.path.exists(legend_db), os.path.abspath(legend_db)


def run_test(commandline, msg = '', verbose=False):
    print ('Running Test:', msg)
    print ('commandline args > xsec_main ',commandline )
    
    # When calling the command line parser from a script, you must send the 
    # commands in the form of a list.  So split the command line string on 
    # the space character using ".split()"
    # cmds = xsec_parse_args(commandline.split())
    cmds = xsec_parse_args(commandline)
    if verbose:
        for c in cmds._get_kwargs():
            print (c)
        
    # To call Xsec_main from another python script, requires cmds as argument.
    # db_name and legend_db are optional. If db_name is provided, it is passed 
    # through to xsec_data.read_database. If db_name is not provided here, then  
    # the read_database() method should define it, or should import a database 
    # module that does, e.g. class c4db in cwi_db.py.
    # If legend_db is provided, it is passed through to xsec_legend.  If not
    # provided, then LEGEND_DB declared at the top of xsec_legend.py is used.
    xsec =  Xsec_main(cmds, db_name=welldata_db, legend_db=legend_db, msg=msg)
    
    if verbose: 
        print (f"Identifiers Used: {list(xsec.data.d_label.values())}")
        print (f"  Type={type(list(xsec.data.d_label.values())[0])}")
        print (f"xsec.sectionline.xy: {xsec.sectionline.xy}, Type = {type(xsec.sectionline.xy)}")
        print (f"xsec.sectionline.xy[0]: {xsec.sectionline.xy[0]}, Type = {type(xsec.sectionline.xy[0])}")
        print (f"xsec.sectionline.xy[0][0]: {xsec.sectionline.xy[0][0]}, Type = {type(xsec.sectionline.xy[0][0])}")
    #     print (f"  Type(xy)= {type(xsec.sectionline.xy)}")
    #     print (f"  Type(xy[0])= {type(xsec.sectionline.xy[0])}")
    #     print (f"  Type(xy[0][0])= {type(xsec.sectionline.xy[0][0])}")
        print (f"Type(xsec.normals)")
        if (xsec.normals):
            for n in xsec.normals:
                print ('Normals: ', n.xy)
        print (30*'*', ' END TEST: ', msg, 30*'*')
    return xsec


############################################################################### 
###############            Tests using CWI data                 ############### 
############################################################################### 

def test_commandline_help():
    txt = xsec_parse_args(['-h'])
    
def testfenceline1():
    msg = 'fenceline with anglehint, requires, exclude'
    linetype = '-f'
    ids = '-i 195748 200828 200830 509077'  
    requires = '-R M'
    anglehint = '-a 45'
    exclude = '-X U W'
    exclude = ' '
    commandline = (f"{linetype} {ids} {anglehint} {requires} {exclude}")  
    run_test(commandline, msg )  

def testprojected1():
    msg = 'projected section line'
    # ids = '195748 200828 200830 509077'  
    ids = '195748 200828 200830' 
    commandline = (f'-p -i {ids} -a 120 -A 30') 
    run_test(commandline, msg ) 

def testhydrofrac1():
    msg = 'drawing hydrofrac interval'
    ids = '625657 681508 13406'  # two of these have hydrofrac intervals
    commandline = (f'-p -i {ids} -R F')  # Requires hydrofrac, the third well is omitted.
    run_test(commandline, msg ) 
    
def testscreen():
    msg = 'singleton section 1'
    commandline = '-s -i 461415' # screened, singleton explicitly selected
    # commandline = '-i 461415'  # screened, singleton is selected automatically
    run_test(commandline, msg )       
    
def testsingleton(wellid='411888'):
    msg = 'singleton section 2'
    commandline = f'-i {wellid}'   # singleton is selected automatically
    commandline = f'-i {wellid}'
    run_test(commandline, msg )   

def test_noelevation1():
    msg = 'singleton - missing elevation data'
    commandline = '-i 469382'  # missing elevation, default singleton behavior
    run_test(commandline, msg ) 
    
def test_noelevation2():
    msg = 'Group, Elevation required, wells missing elevation omitted'
    commandline = '-p -i 195748 200828 469382 -R E'  # omit 469382
    run_test(commandline, msg ) 

def test_noelevation3():
    msg = 'Group, Elevation not required, draws all with no elevation'
    commandline = '-p -i 195748 200828 469382 -r E'  # draw all without elevation
    run_test(commandline, msg ) 

def test_wells_located_on_vertical():
    msg = 'Geometry error possible when fitting points on a vertical line'
    ids = '105290 126305'
    commandline = f"-p -i {ids}"
    run_test(commandline, msg ) 

def test_compare_possible_duplicates():    
    msg = 'Use the cross section to compare possibly redundant records'
    ids = '14082 14084'
    # ids = '105290 126305'
    # ids = '329310 329324'
    commandline = f"-p -i {ids}"
    run_test(commandline, msg ) 
    
def test_others():
    msg = 'Other examples. Print the xsec object when done'
    ids = '625657 681508'
    ids = '625657 681508 13406 461415 469382'
    ids = '195748 200828 200830'
    #commandline = f"-p -i {ids} -R E"
    commandline = f"-p -i {ids}"
    x = run_test(commandline, msg ) 
    print (x.data)

def run_demo():
    
    testfenceline1()
    testprojected1()
    testhydrofrac1()
    testscreen()
    # testsingleton(411888)
    testsingleton(509077)
    test_noelevation1()  
    test_noelevation2()  
    test_noelevation3()  
    test_wells_located_on_vertical()
    test_compare_possible_duplicates()
    test_others()
    #
    # test_commandline_help()  # Execution terminates when help is called.
 
    return 0  
    
if __name__=='__main__':
    import xsec_legend
    print (xsec_legend.check_legend_path())
    run_demo()
    
    print ('///////////////// That concludes xsec_demo script ///////////////////')    