'''
Created on Apr 28, 2021

@author: Bill Olsen
'''
from geometry_base import Plyline

def singleton_section_line(d_xy, cmds):
    '''
    Return sectionline for the case that there is only one point on the line
    
    Arguments
    ---------
    d_xy : dictionary of coordinate pairs
        -   key : well id 
        -   value : tuple (x,y)
            world coordinates of the well (x,y) : (real, real).
    
    cmds : Namespace as returned by argparse module
        -   user supplied directives.
        
    Returns
    -------        
    orderedkeys : list
        The well ids ordered along section line.
        
    sectionline : Plyline
        A polyline with just one node at xy. length = 0 
        
    projectionlines : None
        A fenceline does not have projectionlines.
        
    Notes:
    -   A singleton is does not neatly fit into the concept of a section line,
        but forcing it into a kind of degenerate section line representation 
        allows it to be drawn using many of the same methods used for regular
        cross sections designed for multiple wells.
    -   The Plyline class must support single point lines.     
    '''
    assert len(d_xy) == 1
    section_line = Plyline(list(d_xy.values()),'singleton')
    return list(d_xy.keys()), section_line, None