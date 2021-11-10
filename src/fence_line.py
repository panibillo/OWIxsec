'''
Created on Apr 27, 2021

@author: Bill
'''
import numpy as np
import unittest
from functools import lru_cache

from geometry_base import Point, Line, Plyline, Rectangle

import logging
logger = logging.getLogger('fence_line')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.WARNING)

@lru_cache(256)
def hypot_p(a,b):
    """ Return hypotenuse between a=(x,y) and b=(x,y) """
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

@lru_cache(256)
def score_swapM(a,b,c,d, d_xy):
    """ 
    Return the reduction in summed lengths due to swapping b and c
    
    Arguments
    ---------
    a,b,c: dictionary keys
        Identifiers of points in dictionary d_xy.    
        
    d_xy : dictionary of points on the line
        values are 2-tuples of (x,y) coordinates
    
    Returns
    -------
    Change_in_length : float
        The change is the new total length minus the original total length. 
        
    swapped_indices : tuple of 2 integers.
    
    Notes
    -----
    -   The swap tried is between points b and c. Points a and d do not move.
    -   The original total length is ab + bc + cd 
    -   The new total length is ac + cb + bd.
    -   But bc=cb, so the net change is just (ac+bd) - (ab + bc). 
    -   A positive number means that swapping b and c results in a greater
        total length
    """
    ab = hypot_p(d_xy[a], d_xy[b])
    cd = hypot_p(d_xy[c], d_xy[d])
    ac = hypot_p(d_xy[a], d_xy[c])
    bd = hypot_p(d_xy[b], d_xy[d])
    return (ab + cd) - (ac + bd), (b,c)

@lru_cache(256)
def score_swapE(b,c,d, d_xy):
    """ 
    Return the reduction in summed lengths due to swapping a and b
    
    Arguments
    ---------
    b,c,d: dictionary keys
        Identifiers of points in dictionary d_xy. a should be an end-point, b  
        should be an end-point.
        
    d_xy : dictionary of points on the line
        values are 2-tuples of (x,y) coordinates
    
    Returns
    -------
    Change_in_length : float
        The change is the new total length minus the original total length. 
        
    swapped_indices : tuple of 2 integers.

    Notes
    -----
    -   Index b should be an end point. The swap tried is between b and c. Point
        d does not move.
    -   The original total length is  bc + cd
    -   The new total length is cb + bd 
    -   But bc=cb, so the change is bd - cd 
    -   A positive number means that swapping b and c results in a greater
        total length
    """
    cd = hypot_p(d_xy[c], d_xy[d])
    bd = hypot_p(d_xy[b], d_xy[d])
    return bd - cd, (b,c)

def fenceline_smooth(d_xy, ordered_wids):
    """
    Alter the ordering of points along a fenceline to minimize total length.
    
    Arguments
    ---------
    d_xy : dictionary of points on the line

    ordered_wids : ordered list of dictionary keys
    
    Returns
    -------
    ordered_wids : ordered list of dictionary keys
    
    Notes
    -----
    o   Assumes that the ordered list provided is an optimal ordering on a 
        projected section-line, or is an approximate ordering along a user 
        supplied line.
    o   The algorithm simply sweeps across the ordered list trying to see if
        swapping an adjacent pair will shorten the overall length.  After each 
        sweep of the entire list only one swap is acted on.  Sweeps continue
        until no length reduction is seen.
    o   Only adjacent pairs are swapped in any single trial.  But points can
        migrate after many swaps.
    o   Possible end-point swaps: 
        -  From  [a b c ...] to [b a c ...].  
        -  The distance [ab] is unchanged. Swap if [ac] < [bc]
    o   Possible middle-point swaps:
        -  From [...a b c d...] to [...a c b d...]
        -  The distance bc] is unchanged. Swap if [ac]+[bd] < [ab]+[cd]
    o   The dictionary d_xy is unpacked to related lists K and P, because
        calls to score_swap require hashable arguments, and dictionaries are not
        hashable.  At the beginning, K is equal to the provided ordered_wids, 
        and P is a list of point tuples (x,y) in order matching to K. K and P
        are kept in matching order throughout.  Only K is returned however.
    o   If the algorithm produces an undesirable result, the user should provide
        either an angle hint or a user line hint.
    """
    N = len(d_xy)
    
    if N < 3: 
        # There is nothing to do
        return ordered_wids
#     l_key = list(d_xy.keys())
#     l_xy = [d_xy[k] for k in l_key]
    K = list(ordered_wids)
    P = [d_xy[k] for k in K]
    Q = tuple(P)
    if N == 3:
        # This case does not work in the general algorithm, and nees only 2 trys
        dL1,swap_pair1 = score_swapE(0,1,2, Q)
        dL2,swap_pair2 = score_swapE(2,1,0, Q)
        if dL1 < 0 and dL1 < dL2:
            K[0],K[1] = K[1],K[0]
        elif dL2 < 0:
            K[1],K[2] = K[2],K[1]
        return K
    
    bestdL = -1
    icount = 0
    while bestdL < 0:
        best_dL = 1
        best_swap = None
        for i in range (0,N-3):
            if i == 0:
                dL, swap_pair = score_swapE(0,1,2, Q)
            elif i == N-4:
                dL, swap_pair = score_swapE(-1,-2,-3, Q)
            else:
                dL, swap_pair = score_swapE(i, i+1, i+2, Q)
            if dL < bestdL:
                bestdL, best_swap = dL, swap_pair
        icount += 1
        logger.debug (f"swapping? {icount}, {bestdL}, {best_swap}")
        if icount> 100: break
        if best_swap is not None:
            a,b = best_swap
            K[a], K[b] = K[b], K[a]
            P[a], P[b] = P[b], P[a]
            T = tuple(P)
        else:
            break
        
    return K

def find_fenceline_with_userline(d_xy, cmds): #oxy, match_all_ordered_points=False):
    '''
    determine ordering of points in d_xy to best match points in oxy
    
    Arguments
    ---------
    d_xy : dictionary of coordinate pairs
        -   key : well id 
        -   value : tuple (x,y)
            world coordinates of the well (x,y) : (real, real).

    cmds : Namespace as returned by argparse module
        The namespace is defined in xsec_cl.py. The following properties affect
        the shape of the fenceline: 
        -   cmds.userline  
        -   cmds.userangle 
        -   cmds.userangle_constraint
        
    Returns
    -------
    ordered_wids : list of key values from d_xy ordered along the fenceline
    
    Algorithm and details
    ---------------------
       Create the line segments between points d_xy.  Match each point in oxy to 
    the nearest line segment, and then compute its position along that segment
    by finding its normal projection onto the line. If it is near a corner, 
    compute its position along both adjacent segments and take the average.   
    Let the coordinates along each line segment be cummulative, so that the 
    computed coordinates are comparable with each other and can be ranked.  
    This provides a solution to the problem of one node being closest to several
    wells, yet may have isues near acute corners.  
    
    d_xy : dict of well location coordinate pairs
        keys : wid
        values : pairs of float (float,float)
    
    userline : list of pairs of float [[float,float],...]
        User defined nodes. Need not correspond exactly with wells in
        number or in location.  Minimum of 2 nodes required.

    Lines : list of Line()
       The individual directed line segments joining the sorted user nodes 
       of userline. Together the line segments form a directed polyline, but a   
       polyline object is never created.  Each segment is given 2 custom 
       attributes s0 & s1 (float), which are the polyline length coordinates
       of the starting and ending points of each line segment.
    -   s0 : float
            coordinate of segment starting point, measured from the polyline
            origin.
    -   s1 : float
            coordinate of segment ending point, measured from the polyline
            origin.

    n : int
        Number of line segments in userline

    d : cumulative length of lines.

    knearest : dict
        Dictionary identifying the user node that is closest to each point in 
        d_xy
        -   key : wid (key from d_xy)
        -   value : int (index of point in oxy)
    
    kposition : dict
        Position of point d_xy along the userline  
        -   key : wid (key from d_xy)
        -   value : cumulative position coordinate on userline
    
    L.s0 : real
        Cumulative length at the start of segment L, measuered along the entire 
        cross section line from the beginning of the first segment.
    
    L.s1 : real
        Cumulative length at the end of segment L, measuered along the entire 
        cross section line from the beginning of the first segment.
        
    rl : boolean
        Describes point location relative to line segment entering node (left).
        True if normal projection of point onto line falls within end points.
        False if normal projection of point falls beyond endpoints. 

    rr : boolean
        Describes point location relative to line segment leaving node (right).
        True if normal projection of point onto line falls within end points.
        False if normal projection of point falls beyond endpoints. 
        
    Xl : float
        x coordinate of normal projection of point onto line along line segment
        entering node (left). The coordinate may be beyond an endpoint.

    Xr : float
        x coordinate of normal projection of point onto line along line segment
        exiting a node (right). The coordinate may be beyond an endpoint.
    -   
    '''
    userline = cmds.userline
 
    Lines = [Line((xy0,xy1)) for xy0,xy1 in zip(userline[:-1], userline[1:])] 
    n = len(Lines)
    d = 0
    for L in Lines:   
        L.s0 = d
        L.s1 = d + L.length
        d += L.length
    
    # find the nearest node on userline to each point on d_xy
    knearesti = dict() 
    knearestp = dict() 
    for k,a in d_xy.items():
        dmin = np.inf
        for i,b in enumerate(userline):
            d = hypot_p(a,b)
            if d < dmin: 
                knearesti[k] = i
                knearestp[k] = a
                dmin = d
    
    # find X,Y for each point in d_xy on the 1 or 2 Lines through the 
    # nearest node on userline
    kposition = dict()
    for k,a in d_xy.items():
        i = knearesti[k]
        # Try to map the point to each adjacent line. 
        # This should only fail when the index i is out of range.
        logger.debug (f"A__: i,k,a= {i}, {k}, {a})")
        try:
            assert (i-1) >= 0
            L = Lines[i-1]
            Xl,_ = L.XY(a)
            Xl = Xl + L.s0
            rl = ((L.s0 <= Xl <= L.s1) 
                  or (i==0 and Xl < L.s1)) 
            logger.debug (f"  B: {rl}, {Xl:4.1f}")
        except Exception as e:
            rl,Xl = None, None
            logger.debug ('  C: None, None')
            
        try:
            L = Lines[i]
            Xr,_ = L.XY(a)
            Xr = Xr + L.s0
            rr = ((L.s0 <= Xr <= L.s1)
                  or (i==n-1 and Xr > L.s0))
            logger.debug (f'  D: {rr}, {Xr:4.1f}')
        except Exception as e:
            rr,Xr = None, None
            logger.debug ('  E: None, None' )

#         if   rl is not None and rr is None: kposition[k] = Xl
#         elif rl is None and rr is not None: kposition[k] = Xr
#         elif Xl is not None and Xr is not None: kposition[k] = (Xl + Xr)/2
#         elif Xl is not None: kposition[k] = Xl
#         elif Xr is not None: kposition[k] = Xr

        # if the point maps exclusively to one line (rl xor rr) then take that X  
        if   rl and not rr: kposition[k] = Xl
        elif not rl and rr: kposition[k] = Xr
        
        # else if the point can map to both lines, take the average X
        elif Xl and Xr    : kposition[k] = (Xl + Xr)/2
       
        # else one of the maps faile, take the X from the map that did not fail
        elif Xl           : kposition[k] = Xl
        elif Xr           : kposition[k] = Xr
        
        else: raise ValueError 
    
    # Ordering of points in d_xy is now defined by their sorted values in
    # kposition[k]  
    rposition = {v:k for k,v in kposition.items()} 
    ordered_wids = [rposition[v] for v in sorted(rposition.keys())]
    return ordered_wids 
        
def fenceline(d_xy, cmds):  
    '''           
    Compute fenceline line as a Plyline with attributes

    Arguments
    ---------
    d_xy : dictionary of coordinate pairs
        -   key : well id 
        -   value : tuple (x,y)
            world coordinates of the well (x,y) : (real, real).

    cmds : Namespace as returned by argparse module
        The namespace is defined in xsec_cl.py. The following properties affect
        the shape of the fenceline: 
        -   cmds.userline  
        -   cmds.userangle 
        -   cmds.userangle_constraint
    
    Returns
    -------        
    orderedkeys : list
        The well ids ordered along section line.
        
    sectionline : Plyline
        Nodes are the fenline world coordinates 
        
    projectionlines : None
        A fenceline does not have projectionlines.
        
    Notes
    -----
    -   First call find_best_sectionline_ordering(d_xy, option='fenceline')
        and use the orderedkeys that it returns.
        
    -   If len(d_xy) < 2, then there is no real chance for a fence line, so
        cmds are ignored and a single well drawing is returned.
    
    -   properties of cmds that are used to determine the ordering of wells 
        along the fenceline are:
        -   cmds.userline : array of (x,y) coordinate pairs, in approximate 
            order along fenceline.
    
        -   If userline and userangle are both None, then use:
                find_best_sectionline_ordering(d_xy, option='fenceline')
    
        -   If len(userline)==2: Then userline defines the orientation, and the  
            wells are ordered along that orientation.
            
        -   ? If len(userline)>2 then len(userline) must equal len(d_xy). 
            The points in 
            xy define the ordering of points and orientation of the section
            line.  But the points in oxy may only be approximate locations;
            they are used to find the nearest wells in d_xy, and then the
            ordering along the section line is determined by the order of
            the nearest matching point in oxy.
            
        -   If userangle is not None, then the best fenceline ordering is found
            as ordered along userangle, plus or minus userangle_constraint if 
            given.  
    ''' 
    logging.debug(f"fenceline d_xy: {d_xy}")
    logging.debug(f"fenceline userline: {cmds.userline}")
    logging.debug(f"fenceline userangle: {cmds.userangle}")
    logging.debug(f"fenceline userangle_constraint: {cmds.userangle_constraint}")
     
    if len(d_xy) == 1:
        from singleton_section_line import singleton_section_line
        return singleton_section_line (d_xy, cmds)
    
    if cmds.userline:
        ordered_wids = find_fenceline_with_userline(d_xy, cmds)
        if len(ordered_wids)>5 and len(ordered_wids)/len(cmds.userline)>2:
            ordered_wids = fenceline_smooth(d_xy, ordered_wids)
    else:
        from projected_line import find_best_projected_ordering 
        ordered_wids, _ = find_best_projected_ordering(d_xy, cmds)
        logger.debug(f"F1-- {ordered_wids}")
        ordered_wids = fenceline_smooth(d_xy, ordered_wids)
        logger.debug(f"F2-- {ordered_wids}")
     
    xy = [d_xy[k] for k in ordered_wids]
    logger.debug (f"xy: {xy}")
    xsecline = Plyline(xy, label='fenceline')
    return ordered_wids, xsecline, None  

def plot_layout(d_xy, polyline, userline, title):
    """This is a debugging routine to visulize the sectionline in map view"""
    from matplotlib import pyplot as plt
    fig, axsL = plt.subplots(1,1)
    
    logger.debug(f"polyline-X= {polyline.xy[:,0]}")
    logger.debug(f"polyline-Y= {polyline.xy[:,1]}")
    axsL.plot(polyline.xy[:,0], polyline.xy[:,1],
                     color=polyline.linecolor)
    
    for xy in d_xy.values():
        axsL.plot(*xy, 'or')
    if userline is not None:
        x = [p[0] for p in userline]        
        y = [p[1] for p in userline]
        axsL.plot(x,y,'g')
        axsL.plot(x,y,'g.')
    axsL.set_aspect('equal')
    plt.title(title)
    plt.show()    
    
class Cmds():
    """This is only a simulation of command line arguments for testing."""
    def __init__(self):
        self.userangle = None
        self.userangle_constraint = None
        self.userline = None
        self.userline = None

class Test(unittest.TestCase):
    def d_xy2(self):
        return {'w1':Coord(0,0),
                'w2':Coord(3,4),
                'w3':Coord(6,0),
                'w4':Coord(7,4),
                'w5':Coord(8,0)}
        
    def test_find_fencline_with_userline(self):
        title = 'find_fencline_with_userline'
        cmds = Cmds()
        d_xy = self.d_xy2()
        cmds.userline = ((0,3),(7,3),(9,0))
        ordered_wids, xsecline, _ = fenceline(d_xy, cmds)
        plot_layout(d_xy, xsecline, cmds.userline, title)

    def test_find_fencline_with_smooth(self):
        title = 'find_fencline_with_smooth'
        cmds = Cmds()
        d_xy = self.d_xy2()
        cmds.userline = None
        ordered_wids, xsecline, _ = fenceline(d_xy, cmds)
        plot_layout(d_xy, xsecline, cmds.userline, title)
if __name__ == "__main__":
    from xsec_data_abc import Coord
    unittest.main() 