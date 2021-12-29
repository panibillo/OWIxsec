'''
Created on Apr 27, 2021

@author: Bill Olsen
'''
import numpy as np

from geometry_base import  Line, Plyline

import logging
logger = logging.getLogger('projected_line')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.DEBUG)

def rotate(x, y, angle):
    """ 
    Rotate (x,y) points counter-clockwise about the origin by angle 
    
    Arguments
    ---------
    x,y : scalar numbers or numpy vectors
    angle : scalar number (radians)
    
    Returns
    -------
    X,Y : same type and shape as x,y
        Points (x,y) are rotated by angle about the point (x,y)=(0,0).
        A positive angle causes counter-clockwise rotation.
    """
    c,s = np.cos(angle), np.sin(angle)
    X = x*c - y*s
    Y = y*c + x*s
    return X, Y

def translate(x, y, dx, dy):
    """ 
    Translate (x,y) by distance (dx, dy)
    
    Arguments
    ---------
    x,y : scalar numbers or numpy vectors
    dx, dy : scalar numbers
    
    Returns
    -------
    X,Y : same type and shape as x,y
        Points (x,y) are translated to points (X,Y).
    """
    return x + dx, y + dy


def projected_section_line(d_xy, cmds): #orderedkeys=None, theta=None, max_del_theta=60, userline=None): 
    '''           
    Compute section line and projection lines

    Arguments
    ---------
    d_xy : dictionary of coordinate pairs
       -   key : well id 
       -   value : tuple (x,y)
           world coordinates of the well (x,y) : (real, real).

    cmds : Namespace as returned by argparse module
        The namespace is defined in xsec_cl.py
        
    cmds.userline : ((real,real), (real,real))  (optional)
        The userline defines the angle and location of the projected section-
        line.  The endpoints will be adjusted to correspond to the first and  
        last points projected from wells onto the section-line.

    cmds.userangle : real [radians] [-pi/2:pi/2] (optional) 
        Approximate angle of line along which ordering is based.  If a userline
        is also provided, then theta is ignored. If there is no userline then
        the projection line will be oriented along theta, and pass through the
        centroid of the well locations.
        
    cmds.userangle_constraint : real [radians] [0:pi/2]  (optional, default=0)
        Maximum angle that the projection line can differ from given theta.
        If userangle_constraint < 90 then the best fit section line will be determined
        subject to the constraint
            angle = userangle +/- userangle_constraint. 
            
            
    Returns
    -------
    ordered_keys: list
        The well ids correctly ordered along section line.  This is a different 
        object from the orderedkeys that may be provided as an argument, and the 
        ordering will be corrected if it was provided incorrectly.
        
    sectionline : Plyline
        Nodes are the world coordinates of the points along the straight line  
        that the wells project onto.   

    projectionlines : list (line) 
        List of straight line segments normal to the section line
        and leading to each well in the list.
        
    Notes
    -----
    o   This function delegates to either projected_section_line_given()
        or projected_section_line_auto().  Users should call this function, 
        and the arguments provided determine to whom is delegated.
        
    o   The user has several options for controling the location and orientation
        of the projection-line.  
        
        -   If userline is given, it determines the location and orientation of 
            the projection line. Other options are ignored.
            
        -   If theta is given, then it determines the approximate orientation
            of the projection line, subject to the optional contraint of 
            max_del_theta.
    
    -   If theta is given, it is assumed to be approximate.
    '''            
    if len(d_xy) == 1:
        from singleton_section_line import singleton_section_line
        return singleton_section_line (d_xy, cmds)

    if  (cmds.userline is None) :
        _, userangle = find_best_projected_ordering(d_xy, cmds)
        cmds.userangle = userangle

    return projected_section_line_given(d_xy, cmds)

def find_best_projected_ordering(d_xy, cmds): #option='fenceline'):
    '''
    Determine best ordering of points and orientation of section line
 
    Arguments
    ---------
    d_xy : dictionary of coordinate pairs
    -   key : well id 
    -   value : tuple (x,y) : (real, real)
        world coordinates of the well.
 
    cmds : Namespace as returned by argparse module
        The namespace is defined in xsec_cl.py. The following properties affect
        the ordering: 
        -   cmds.userangle (radians)
        -   cmds.userangle_constraint (radians)
         
    Returns
    -------
    ordered_wid : list
        list of well ids in xsecline order.
        The ordering is suitable for either fenceline or projected line.
        Order will be along a line within 90 degrees of the direction specified
        by cmds.userangle.  If cmds.userangle is not specified, it will be 
        from left to right along the best fit line.
         
    angle : real
        Rotation angle of the best fit line (approximate to within tol)
        
    Notes
    -----    
    The best fit line minimizes the sum of squared errors measured normal
    to the best fit line. This requires an iterative solution. Recall that in
    linear least squares, the best fit line always passes through the centroid 
    of the points.
    -   Initialze by translating all points so their centroid maps to the origin
        rotate them by minus the userangle. This maps the line through their 
        centroid and at the userangle onto the X-axis.
    -   Begin loop:
        -   Find the best fit line using standard least-squares
        -   Rotate the points so the best fit line rotates to the X-axis
        -   Repeat until a userangle_constraint is reached, or the change in  
            rotation is less than tol.
    -   Return the final angle used, equals the userangle plus the cumulative 
        loop rotations.
    -   Return the list of wids in the order of their X-coordinates in their 
        final completely rotated state. 
    '''
    # angle tolerance is 1 degree
    tol = np.pi/180
    
    if cmds.userangle is None:
        angle0 = 0
        angle_constraint = 0.99 * np.pi/2
    else:
        angle0 = cmds.userangle
        if cmds.userangle_constraint is None:
            angle_constraint = np.pi/2
        else:
            angle_constraint = cmds.userangle_constraint

    # Extract keys and x,y points from d_xy into ordered lists.
    # The order doesn't matter, except it must remain the same in all 3 lists. 
    x,y,wid = [],[],[]
    logger.debug(f"Entering: pointcount={len(d_xy)}, cmds={cmds}")
    for key,coord in d_xy.items():
        if len(d_xy) < 4: 
            logger.debug (f"starting: {key} {coord}")
        x.append(coord.x)
        y.append(coord.y)
        wid.append(key)
    x = np.array(x)
    y = np.array(y)

    # Center both x and y arrays on their centroids.  This has the effect of 
    # translating the x,y points so that their centroid is at (0,0) in the local
    # X,Y coordinate system.
    xc, yc = np.mean(x), np.mean(y)
    X, Y = translate(x, y, -xc, -yc)

    # Rotate the x,y points about the origin by -angle0. A line at userangle
    # through the centroid in world coordinates, now lies on the X-axis in the 
    # local XY coordinate system. Rotations in the iterative steps are all made
    # relative to these initial rotated positions, denoted X0,Y0   
    X0,Y0 = rotate(X,Y,-angle0)
    theta = 0
    logger.debug(f"    step {0}, dtheta={0:8.4f},  A={np.degrees(theta+angle0):8.4f},     C={np.degrees(angle_constraint):5.4f}")
    
    istep=1  
    errcount, nudge = 0, 0.01  
    while istep < 20: # Let's not loop forever if there is a bug.
        X,Y = rotate(X0,Y0, -theta)
        # logger.debug(f"    step {istep}    X = {X},  Y = {Y}, theta={np.degrees(theta)}, A={np.degrees(theta+angle0)}")
        try:
            p = np.polyfit(X, Y, 1)
        except:
            # We suppose that numpy has thrown np.linalg.LinAlgError because 
            # we have tried to fit a vertical line. But we cannot always catch
            # that error by name. Under Python3.8, numpy 1.21.4, this produces
            # a ValueError that is not reported using the normal error reporting
            # mechanism, so we cannot catch it explicitly.
            if errcount >4:
                break
            theta += nudge
            nudge = -nudge
            errcount += 1
            continue           
            
        f = np.poly1d(p)            # f is a linear polynomial
        theta1 = np.arctan2(f(1),1) # theta1 is slope of the line in rad from +x
        theta += theta1
        logger.debug(f"    step {istep}, dtheta={np.degrees(theta1):8.4f},  A={np.degrees(theta+angle0):8.4f}, theta={np.degrees(theta):5.4f}")
        if theta <= -angle_constraint:
            theta = -angle_constraint
            break
        elif theta >= angle_constraint:
            theta = angle_constraint
            break
        elif np.abs(theta1) < tol:
            break
        istep += 1    

    # Recompute the node ordering using the final angle theta
    X,Y = rotate(X0,Y0, -theta)
    ordered_wid = [wid[i] for i in np.argsort(X)]
    finaltheta = theta + angle0
  
    return ordered_wid, finaltheta  

def projected_section_line_given(d_xy, cmds):
    '''           
    Compute section line and projection lines

    Arguments
    ---------
    d_xy : unordered dict of coordinate pairs
        
        -   wid: (x,y) : (real, real)
            world coordinates of the well.
                    
    cmds.userline :  
        nx2 array of (x,y) coordinate pairs, in world coordinates.
        The two points define a line segment that defines the location and 
        angle of the xsec-line.  The endpoints of the xsec-line will be 
        adjusted.
    
    cmds.userangle : float (radians)
        The userangle is ignored if the userline is given. 

    Returns
    -------
    xsline : line ((x0,y0), (x1,y1))
        Defines a straight section line in world coordinates.
        The end-points are the right-angle projections of the first and last 
        points of the ordered point list.
    
    projectionlines : list (line) 
        List of straight line segments normal to the section line and leading
        to each well in the list.
    
    spacing : numpy vector array
        Individual distances between points along the section line.
        
    Notes
    -----
    -   Either cmds.userline or cmds.userangle needs to be specified.  If the 
        user has not supplied either, then cmds.userangle is determined by a
        call to find_best_projected_ordering() 
        
    -   The spacings may be adjusted in the vertical cross section for clarity,
        but provision is not made here for adjusting the projection lines to
        correspond to such adjusment.
    '''            
    x,y,wid = [],[],[]
    for key,coord in d_xy.items():
        if len(d_xy) < 4:
            logger.debug (f"projected_section_line_given: {key}, {coord}")
        x.append(coord.x)
        y.append(coord.y)
        wid.append(key)

    xy = np.array(list([v.x, v.y] for v in d_xy.values()))
    
    if cmds.userline:
        userLine = Line(cmds.userline)
        alpha = userLine.anglerad() 
        xyc = userLine.center()
    elif cmds.userangle is not None:
        alpha = cmds.userangle
        xyc = np.mean(xy,0) 
    else:
        raise AttributeError('userline or userangle is required in cmds')
    
    # Translate the line center to the origin (0,0) in the X,Y plane. 
    xc, yc = xyc[0], xyc[1]
    X, Y = translate(x, y, -xc, -yc)
    
    # Rotate the X,Y points about the origin by angle -alpha into the U,V plane. 
    # This rotates the section line onto the horizontal (U) axis.
    U, V = rotate(X, Y, -alpha)

    # Project points U,V onto points Up,Vp that lie on the U-axis. This is easy
    # because Up stays equal to U, and Vp is just set to 0     
    Up, Vp = U, V*0  

    # Unrotate points Up,Vp back to the XY plane
    Xp, Yp = rotate(Up, Vp, alpha) 

    # Un-translate points Xp,Yp back to the xy plane
    xp, yp = translate(Xp, Yp, xc, yc)
    xyp = np.array([xp,yp]).T
    
    # Determine the order of identifiers along the projected section line.
    # And identify the indices of the endpoints.
    psort = np.argsort(Up)
    ordered_wids = [wid[i] for i in psort]
    
    # The projection line is defined by the points xyp on it, which have to be
    # reordered in order psort.
    xyp = xyp[psort,:]
    projectionline = Plyline( xyp, label = 'sectionline')
    
    # Define the leader lines from the wells onto the section line
    # Note that xsec_main will ultimately adjust the node spacings on the section
    # line for readability, and have to define pseudo-normals.  These normals
    # are for debugging, so we can visualize whether the projection algorithm is 
    # working correctly.
    normals = []
    for i, wid in enumerate(ordered_wids):
        p0, p1 = d_xy[wid], xyp[i,:] 
        normals.append( Line((p0,p1), label='normal') )

    return ordered_wids, projectionline, normals  

def update_projection_line_nodes(pline, Xnodes): 
    """
    Update node locations on a straight line to match spacing of Xnodes.
    
    Arguments
    ---------
    pline : Plyline.
        This should be the existing projected-section-line.  It will have node
        locations spaced along it corresponding to each well (including the end
        points. 
    
    Xnodes : numpy vector array
        Node coordinates on cross section line in X-dimensions.
    
    Modifies
    -------
    pline : Plyline
        Node spacing along xypline is proportional to spacing in Xnodes.
    """
    x0, x1 = pline.x[0], pline.x[-1]
    y0, y1 = pline.y[0], pline.y[-1]
    dX = np.ptp(Xnodes)
    s = (Xnodes-Xnodes[0])/dX
    pline.xy[:,0] = x0 + s*(x1-x0)
    pline.xy[:,1] = y0 + s*(y1-y0)
    
################################################################################
############################       TESTING      ################################

        
if __name__ == '__main__':
    from dataclasses import dataclass    
    from xsec_data_abc import Coord

    def plot_layout(d_xy, xsecline, theta, normals, title):
        """This is a debugging routine to visulize the sectionline in map view"""
        from matplotlib import pyplot as plt
        fig, axsL = plt.subplots(1,1)  
        
        if len(d_xy) < 5:  
            print('X=', xsecline.xy[:,0])
            print('Y=', xsecline.xy[:,1])
        axsL.plot(xsecline.xy[:,0], xsecline.xy[:,1], color=xsecline.linecolor)
        
        if normals:
            for n in normals:
                axsL.plot(n.xy[:,0], n.xy[:,1], 'b')
        
        for xy in d_xy.values():
            axsL.plot(*xy, 'or')
        axsL.set_aspect('equal')
        plt.title(title)
        plt.show()    

    @dataclass    
    class Cmds:
        """This is only a simulation of command line arguments for testing."""
        userangle : float  
        userangle_constraint : float  
        userline : tuple      

    cmds = Cmds(None,None,None)
    d_xy = {   
        101: Coord(500100, 500200),
        202: Coord(500700, 500400),
        303: Coord(500500, 500500)}
    userangle = np.radians(-30)
    userangle_constraint = np.radians(10)
    userline = ((500000,500250),(500750,500450))     
    
    if 0:
        b_xy = {  
            101: Coord( 100,  100),
            202: Coord(-100, -100)}
        cmds = Cmds(np.radians(45), None, None) 
        ordered_wid, theta = find_best_projected_ordering(b_xy, cmds)
        print ('A(45)', ordered_wid, np.degrees(theta))

        cmds = Cmds(np.radians(40), None, None) 
        ordered_wid, theta = find_best_projected_ordering(b_xy, cmds)
        print ('B(45)', ordered_wid, np.degrees(theta))
        
        cmds = Cmds(np.radians(30), np.radians(4), None) 
        ordered_wid, theta = find_best_projected_ordering(b_xy, cmds)
        print ('C(34)', ordered_wid, np.degrees(theta))

        cmds = Cmds(np.radians(-120), np.radians(4), None) 
        ordered_wid, theta = find_best_projected_ordering(b_xy, cmds)
        print ('D(-124)', ordered_wid, np.degrees(theta))
        
    if 1:
        title ='A'
        cmds.userangle            = None
        cmds.userangle_constraint = None
        cmds.userline             = None
        ordered_wids, theta = find_best_projected_ordering(d_xy, cmds)
        print (ordered_wids, np.degrees(theta))
        oline = Plyline([d_xy[key] for key in ordered_wids])
        ordered_wids, xsecline, normals = projected_section_line(d_xy, cmds)
        print (ordered_wids)
        plot_layout(d_xy, xsecline, theta, normals, title)
    if 1: 
        title ='B'
        cmds.userangle            = np.radians(-30)
        cmds.userangle_constraint = np.radians(10)
        cmds.userline             = None
        ordered_wids, xsecline, normals = projected_section_line(d_xy, cmds)
        plot_layout(d_xy, xsecline, None, normals, title)
    if 1: 
        title ='B0'
        cmds.userangle            = np.radians(-30)
        cmds.userangle_constraint = np.radians(30)
        cmds.userline             = None
        ordered_wids, xsecline, normals = projected_section_line(d_xy, cmds)
        plot_layout(d_xy, xsecline, None, normals, title)
    if 1: 
        title ='C'
        cmds.userangle            = None
        cmds.userangle_constraint = None
        cmds.userline             = userline
        ordered_wids, xsecline, normals = projected_section_line(d_xy, cmds)
        plot_layout(d_xy, xsecline, None, normals, title)
    if 1: 
        title ='D'
        cmds.userangle            = userangle
        cmds.userangle_constraint = userangle_constraint
        cmds.userline             = userline         
        ordered_wids, xsecline, normals = projected_section_line(d_xy, cmds)
        plot_layout(d_xy, xsecline, None, normals, title)
        
    if 1: 
        np.random.seed(0)  
        n=60
        X = np.random.rand(n)*500000
        Y = np.random.rand(n)*400000
        X,Y = rotate(X,Y, np.radians(-30))
        b_xy = {i:Coord(x,y) for i,(x,y) in enumerate(zip(X,Y))}  
        for d,c in ((None , None),
                    (30,None),
                    (30,10),
                    (-100,0),
                    (80,0),
                    (70,10)):
            title =f"E ({d},{c})"
            if d: d=np.radians(d)
            if c: c=np.radians(c)
            cmds = Cmds(d,c, None)
            
        
            ordered_wids, xsecline, normals = projected_section_line(b_xy, cmds)
            plot_layout(b_xy, xsecline, None, normals, title)