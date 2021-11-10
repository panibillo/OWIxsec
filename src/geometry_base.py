'''
Define basic shapes used by section_line module

Classes
-------
Point()
Plyline()
Line(Plyline)
Plygon()
Rectangle(Plygon)
cRectangle(Rectangle)

Methods
-------
pairRectangles()

Notes
-----
o   These are very simple classes. They have the needed coordinate information,
    plus minimal attributes required by the cross section tool, plus basic
    methods required by the cross section tool, plus basic attributes required
    by matplotlib for drawing.

o   Typlical properties 
    +   x, y
    +   ((x,y), (x,y), ...)
    +   angle         measured counterclockwize from East in radians.
    +   length
    +   label
    +   pointcolor
    +   pointsize
    +   linecolor
    +   linethick
    +   linestyle

Author
------
Bill Olsen

Version
-------    
0.1  2020-11-29


'''

import numpy as np
import unittest
import logging
logger = logging.getLogger('geometry_base')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.WARNING)

def principle_rad_angle(r):
    """ 
    Shift angle r(in radians) to range (-pi:+pi]
    """
    while r < -np.pi:
        r += 2*np.pi
    while r > np.pi:
        r -= 2*np.pi
    return r
    
class Point:
    """
    A 2-dimensional point

    Attributes
    ----------
    x  : float 
        x coordinates of the point.

    y  : float 
        y coordinates of the point.
    
    label : string
        describes the line
        
    pointcolor : ?
        a color descriptor
        
    pointsize : ?
        diameter(?) of the point in drawing units.
    """ 
     
    def __init__(self, x, y, label='', pointcolor='k', pointsize=1.0):
        self._x = x
        self._y = y
        self.p = np.array((x,y))
 
        self.label = label
        self.pointcolor = pointcolor
        self.pointsize = pointsize
    
    def __str__(self):
        return f'({self._x:5.2f}, {self._y:5.2f})'
    
    def __repr__(self):
        return (f"Point({self._x}, {self._y}), \n",
                f"    label='{self.label}', pointcolor='{self.pointcolor}',",
                f" pointsize={self.pointsize})")
     
    def x(self):
        return self._x

    def y(self):
        return self._y
    
    def distance (self, other):
        return np.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)

class Plyline():
    """
    A list of connected straight line segment.

    Attributes
    ----------
    xy : numpy array, dtype=float, shape (n,2), n>=2
        array of ordered x,y points along the line 
    
    label : string
        describes the line
        
    linecolor : ?
        a color descriptor
        
    linethickness : ?
        line thickness in drawing units.
        
    segmentlength : np array(float)
        lengths of @ segment. The number of segments = number of nodes - 1.
    
    length : float
        cumulative length of the entire polyline.
        
    snodes : np array (float)
        Cumulative distance along the polyline measured at each node.  
        snode[0] = 0, snode[-1] = length
    
    centroid : np array ((1,2), float)
        (x,y) coordinates of centroid of nodes. (mean of x_i, mean of y_i)
        
    Methods
    -------
    length : float
    
    
    """
    def __init__(self, xy, label='', 
                 linecolor='k', linethick=1.0, linestyle='-', zorder=1):
        self.xy = p = np.array(xy, dtype = float)  
        self.x = p[:,0]
        self.y = p[:,1]
        self.label = label
        self.linecolor = linecolor
        self.linethick = linethick
        self.linestyle = linestyle
        self.zorder = zorder
        #self.length = np.sum([Line(x1,y1,x2,y2).length for (x1,y1),(x2,y2) in zip ])
        diffs = self.xy[1:,:] - self.xy[:-1,:]
        self.segmentlength = np.sqrt(np.sum(diffs**2, 1))
        self.snodes = np.hstack(([0], np.cumsum(self.segmentlength)))
        self.length = np.sum(self.segmentlength)
        self.centroid = np.mean(self.xy,0)

    def repr_properties(self):
        return '\n    '.join(( 
            f"    label='{self.label}',",
            f"linecolor='{self.linecolor}',",
            f"linethick='{self.linethick}',",
            f"linestyle='{self.linestyle}')")) 
         
    def str_properties(self):
        return ', '.join((
            f"    label='{self.label}'", 
            f"linecolor='{self.linecolor}'", 
            f"linethick='{self.linethick}'", 
            f"linestyle='{self.linestyle}')" ))
                      
    
    def __repr__(self):  
        return '\n'.join((
            "Plyline (np.array(",
            "    "+"\n    ".join((f"[{p[0]}, {p[1]}]," for p in list(self.xy))),
            f"    ),",
            self.str_properties()
        ))

    def __str__(self):
        return '\n'.join((
            "Plyline (np.array(",
            "    "+"\n    ".join((f"[{np.round(p[0],0)}, {np.round(p[1],0)}]," for p in list(self.xy))),
            f"    ),",
            self.str_properties()
        ))

class Line(Plyline):
    """
    A directed straight line segment.

    Arguments
    ---------
    xy : Pair of coordinate pairs, float: tuple, list, or np.array
        E.g. ((x0,y0), (x1,y1))
        The x and y coordinates of starting and ending points. 

    kwargs : see Plyline


    Attributes
    ----------
    _xy0 : pair of float: tuple, list, or np.array
        x and y coordinates of starting point.

    _xy1 : pair of float: tuple, list, or np.array 
        x and y coordinates of ending point.
    
    angle : float [radians]
        angle of directed line [_xy0,_xy1].  The angle is measured in radians
        from the positive horizontal axis.
        
    length : float
        distance from _xy0 to _xy1.
    
    Other attributes inherited from Plyline
    
    
    Methods
    -------
    angledeg : float, rounded [degrees]
        Return the angle of the line directed from xy0 to xy1, in degrees
        measured counterclockwise from East
        
    anglerad : float, radians
        Return the angle of the line directed from xy0 to xy1, in radians
        measured counterclockwise from East
        
    length : float
        Return the length of the line
    """
    
    def __init__(self, xy, **kwargs):
         
        self._xy0 = np.array(xy[0])
        self._xy1 = np.array(xy[1])
        assert np.shape(self._xy0) == (2,), f"self._xy0 {type(self._xy0)}, {self._xy0}"
        assert np.shape(self._xy1) == (2,)
            
        xy = np.vstack((self._xy0, self._xy1))
        super().__init__(xy, **kwargs)
        d = self._xy1 - self._xy0
        self.angle = np.arctan2(d[1], d[0])
    
    def __str__(self):
        x0,y0 = self.xy0()
        x1,y1 = self.xy1()
        return "\n".join((
            f"Line(({x0:5.2f}, {y0:5.2f}), ({x1:5.2f}, {y1:5.2f})"  
            f" # length={np.round(self.length,0)}, angle={self.angledeg()}",
            super().str_properties() ))
    
    def __repr__(self):
        x0,y0 = self.xy0()
        x1,y1 = self.xy1()
        return "\n".join((
            f"Line(({x0}, {y0}), ({x1}, {y1})",
            super().repr_properties() ))
     
    def p0(self):
        return self._xy0
    def p1(self):           
        return self._xy1
    
    def xy0(self):  
        return self._xy0[0], self._xy0[1]
    def xy1(self):  
        return self._xy1[0], self._xy1[1]
    
    def anglerad(self):
        return self.angle + 0 
    def angledeg(self):
        return np.round(self.angle * 180/np.pi, 0)
    def center(self):
        return (self._xy0 + self._xy1)/2      
    
    def XY(self, xy):
        '''
        Return the coordinate of the point in a rotated coordinate system
          
        Notes
        -----
        o   The local coordinate system is rotated, about the starting 
            point of the line. It is not scaled.
        
        o   The mapping is  
            (z-z0)*(cos(a) - i sin(a))
            = (u + iv)(c - is)
            = uc + vs + i(vc -us)
        '''
        u,v = xy[0] - self._xy0[0], xy[1] - self._xy0[1]
        c,s = np.cos(self.angle), np.sin(self.angle)
        X,Y = u*c + v*s, v*c - u*s
        return X,Y
        
from numbers import Number

class Plygon():
    def __init__(self, boundary, **kwargs):
        """ Initialize a polygon object with boundar and other properties.
        
            keyword arguments:
            -   self.boundary  = boundary
            -   self.label     = label
            -   self.linecolor = linecolor
            -   self.linethick = linethick
            -   self.linestyle = linestyle
            -   self.filled    = filled
            -   self.fillcolor = fillcolor
            -   self.pattern   = pattern
        """
        self.__dict__.update(kwargs)
        self.userattributes = dict(kwargs)  # only for information.
 
    def repr_properties(self):
        rv = []
        for k,v in self.userattributes.items():
            if isinstance(v, Number):
                rv.append(f"{k}={v}")
            else:
                rv.append(f"{k}='{v}'")
        return '\n    '.join(rv)
        
    def str_properties(self):
        rv =     [f"label='{self.label}'"]
        rv.append(f"linecolor='{self.linecolor}', linethick='{self.linethick}',linestyle='{self.linestyle}'," )
        rv.append(f"filled   ='{self.fillcolor is not None}', fillcolor='{self.fillcolor}',pattern='{self.pattern}',patterncolor='{self.patterncolor}')" )
        return '\n           '.join(rv)              

    def __repr__(self):  
        return "\n".join(("Plygon("+ "    "+str(self.boundary), self.repr_properties()))
    def __str__(self):
        return "\n".join(("Plygon("+ "    "+str(self.boundary), self.str_properties()))

    def set_boundary(self, boundary):
        logger.debug (f"Plygon.set_boundary({boundary})")
        self.boundary = boundary

class Rectangle(Plygon):
    """
    A rectangle with border and fill.

    Attributes
    ----------
    x : iterable of 2 float values.
            array of ordered xlo < xhi
    
    y : iterable of 2 float values.
            array of ordered ylo < yhi
        
    width : float
        width = x1 - x0
        
    height : float
        height = y1 - y0
    
    label : string
        describes the line
        
    linecolor : ?
        a color descriptor
        
    linethick : ?
        line linethick in points.
        
    facecolor : ?
        a color descriptor
        
    zorder : int
        0,1,2 : draw behind, default, draw in front
        
    Methods
    -------
    length : float
    
    Notes
    -----
    o   Properties are modeled on a matplotlib.patches.rectangle 
    
    o   Degenerate shapes are allowed: having 0 height or 0 width
    """
    
    def __init__(self, x, y, **kwargs):
        """ 
        Define a rectangle, with attributes
        
        Arguments 
        ---------
        x : iterable of 2 float values.
                (xleft, xright)
        
        y : iterable of 2 float values.
                (ybottom, ytop)
        
        keyword arguments are passed to Plygon, and may include
        -    label  
        -    linecolor  
        -    linethick 
        -    linestyle 
        -    filled  
        -    fillcolor 
        -    pattern  
        """
        x0,x1 = self.x = x
        y0,y1 = self.y = y
        boundary = [[x0, y0], [x1,y0], [x1,y1], [x0,y1]]
        self.anchor = (x0,y0)
        self.width = x1 - x0
        self.height = y1 - y0
        self.xcenter = (x0 + x1)/2
        assert (self.width >= 0) and (self.height >= 0)
        super().__init__(boundary, **kwargs) 
     
    def __repr__(self):  
        rv = '\n    '.join(('Rectangle(',
                             f"x=({self.x[0]}, {self.x[1]}),",
                             f"y=({self.y[0]}, {self.y[1]}),",
                             f"width={self.width},",
                             f"height={self.height},"))
        return '\n'.join((rv, super().repr_properties()) )

    def __str__(self):
        rv =     (f"Rectangle (({self.x[0]}, {self.x[1]}), ({self.y[0]}, {self.y[1]})," 
                  f" # width = {self.width}, height = {self.height}")
        return '\n'.join((rv, super().str_properties()))

class cRectangle(Rectangle): 
    """
    A rectangle defined by xcenter, width, ybottom, ytop. Inherits from Rectangle

    Attributes
    ----------
    xcenter : float
        x coordinate from which to measure offset 
    """    
    def __init__(self, x, y, **kwargs):
        """
        Define a rectangle by (x_center, width), (bottom, top), and attributes
        x : iterable of 2 float values.
            (x-center, half width)
    
        y : iterable of 2 float values.
            (ybottom, ytop)

        keyword arguments are passed to Plygon, and may include
        -    label  
        -    linecolor  
        -    linethick 
        -    linestyle 
        -    filled  
        -    fillcolor 
        -    pattern  
        """
        self.xcenter, radius = x
        x0 = self.xcenter - radius 
        x1 = self.xcenter + radius 
        super().__init__((x0,x1), y, **kwargs)

    def __repr__(self):  
        rv = '\n    '.join(('cRectangle(',
                             f"x=({self.xcenter}, {self.width/2}),",
                             f"y=({self.y[0]}, {self.y[1]}),",
                             f"width={self.width},",
                             f"height={self.height},"))
        return '\n'.join((rv, super().repr_properties()))

    def __str__(self):
        rv =     (f"cRectangle (({self.xcenter}, {self.width/2}), ({self.y[0]}, {self.y[1]})," 
                  f" # width = {self.width}, height = {self.height}")
        return '\n'.join((rv, super().str_properties()))

def pairRectangles(xc, ri, ro, y, **kwargs):    
    """ 
    Returns two Rectangles, offset left and right from a common X-centerline. 
    
    Arguments
    ---------
    xc : real
        X-centerline from which to measure offsets to left and right
    ri : real
        inner radius
    ro : real
        outer radius
    y : tuple of (real, real) 
        (ybottom, ytop)
    
    kwargs : keyword arguments as for a Plygon
    """
    rectLeft  = Rectangle((xc-ro, xc-ri), y, **kwargs)
    rectRight = Rectangle((xc+ri, xc+ro), y, **kwargs)
    return rectLeft, rectRight

class Test(unittest.TestCase):   
    def kwargs(self):
        return {'label':'a_label',
                'linecolor':'r',
                'linethick':1,
                'linestyle':'-',
                'fillcolor':'g',
                'pattern':'//',
                'patterncolor':'r'}
        
    def test_principle_rad_angle(self):
        a = 0.45
        C = 2*np.pi
        for m in 1,2,3:
            r = m*C+a
            self.assertAlmostEqual( a, principle_rad_angle(m*C+a), 5)
            self.assertAlmostEqual(-a, principle_rad_angle(m*C-a), 5)
        print ('principle_rad_angle is OK')
    def test_Line(self):
        for ab, c,d,e,f in (( ((0.0, 0.0), (3.0, 4.0)), 'linelabel1', 'k', 2.5, '-'),
                          ( np.array(((0,0),(3,4))), 'nparraydefinedline', None, None, None),
                          ( ((0.0, 0.0), (-5.0, 0.0)), 'linelabel3',None, None, None )
                         ):
            print ('test_Line\n',ab,c,d,e)
            L = Line( ab, label=c, linecolor=d, linethick=e)
            print ('Line:\n  ',L)
            print ('   line angle, length, center:',L.angle, L.length, L.center())
    
    def test_Polyline(self):
        print ('test_Polyline')
        xy = np.array(np.arange(12).reshape(6,2))
        P = Plyline(xy)
        print ('\nstr(P):\n',P)
        print ('\nrepr(P):\n',repr(P))
        print ('centroid',P.centroid)
    
    def test_Rectangle(self):
        print ('test_Rectangle')
        R = Rectangle( (20, 40), (700,800), **self.kwargs()) 
        print ('\nstr(Rectangle)=\n',R)
        
    def test_cRectangle(self):
        print ('pairRectangles(xc, ri, ro, y)')
        xc, ri, ro, y = 100, 20, 30, (700,800)
        print ('pairRectangles(', xc, ri, ro, y, ')')
        R = pairRectangles(xc, ri, ro, y, **self.kwargs()) 
        print (R[0])
        print (R[1])
        

if __name__=='__main__':
    unittest.main()    