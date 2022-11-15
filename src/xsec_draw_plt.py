'''
Created on Dec 26, 2020

@author: Bill
'''
import unittest
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
#from matplotlib.widgets import Slider, Button, RadioButtons

import logging 
logger = logging.getLogger('xsec_draw_plt')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.WARNING)


class xsec_draw():
    """
    Implementation of a drawing ouput module for Xsec
    
    Attributes
    ----------
    Ulo,Uhi : float
        min,max x in output window coordinates 
    Vlo,Vhi : float
        min,max y in output window coordinates 

    ulo,uhi : float
        min,max x of cross section, in output window coordinates 
    vlo,vhi : float
        min,max y of cross section, in output window coordinates 

    Methods
    -------
    grid(majorticks, minorticks)
    
    line(geometry_base.PlyLine)
    
    rect(geometry_base.Rect)
    
    point(geometry_base.Point)
    
    publish()
    
    Notes
    -----
    o   The main module orchestrates the entire drawing process.
    o   This module is responsible for
        -   Defining the ouput coordinate system.
        -   Implementing drawing primitives that accept geometry and attributes
            defined in geometry_base.py
        -   Publishing the output. 
    o   This module implements only drawing and labeling primitives.
    
    o   The focus of this implementation is the cross section window.  The Map
        window is rudimentary. It is presumed that a proper map window will be
        implemented separately.
    """
    
    def __init__(self):
        """ 
        Set the output window dimensions, and initialize the plot
        """
        logger.info("xsec_draw.__init__()")
        self.size = (6,8)
        self.fig, axs = plt.subplots(2,1)
        # add a little room above the lower plot for a title
        self.fig.tight_layout(pad=2.5) 
        self.axM = axs[0]  # map plot
        self.axX = axs[1]  # cross section plot
        self.axX.set_axisbelow(True)
        
        # There are different ways to control visibility of the xaxis labels.
        self.axX.get_xaxis().set_visible(False)
#         self.axX.axis('off')
#         self.axX.get_xaxis().set_ticklabels([])
#         self.axX.get_xaxis().set_ticks([])
#         self.axX.get_xaxis().set_visible(False)
#         self.axX.get_yaxis().set_ticklabels([])
#         self.axX.get_yaxis().set_ticks([])
        
        # Margin areas surrounding the cross section
        self.lborder = 100
        self.rborder = 50
        self.tborder = 20
        self.bborder = 20
        
        self.xsec_aspect_ratio = self.size[1]/self.size[0]

    def plot_Map  (self, d_xy, d_label, polyline, normals=None):   
        """ plots a Map layout of the points in d_xy, the polyline, and normals
        """
        axs = self.axM
        axs.plot(polyline.xy[:,0], polyline.xy[:,1],
                     color=polyline.linecolor)
        if normals:
            for n in normals:
                axs.plot(n.xy[:,0], n.xy[:,1], 'b')  
        
        for wid, xy in d_xy.items():      
            axs.plot(xy.x, xy.y, 'or')
            axs.text(xy.x, xy.y, d_label[wid])
        axs.set_aspect('equal')
 
        
    def get_output_win(self, slims, zlims):
        """ Return the horizontal and vertical ranges for the output window
        
            Arguments
            ---------
            slims : (float, float)
                Min and Max s dimensions in world coordinates - measured along 
                the section-line. Might not start at 0.
            zlims : (float, float)
                Min and Max elevations in world coordinates.  Since the grid-
                lines fully contain all of the well components, the zlims are
                the lowest and highest grid-lines.
        
            Returns
            -------
            ulims : (float, float)
                Min and max horizontal coordinates of output window
            vlims : (float, float)
                Min and max vertical coordinates of output window
            
            Notes
            -------
            o   In this module matplotlib is used to draw the output, so the
                output window simply uses world coordinates:
                -   ulims = slims
                -   vlims = zlims
        """
        self.ulo, self.uhi = slims
        self.vlo, self.vhi = zlims
        self.ulims = (self.ulo, self.uhi)
        self.vlims = (self.vlo, self.vhi)
        return self.ulims, self.vlims
    def set_size(self, xlo, xhi, ylo, yhi):
        logger.debug (f"xsec_draw.set_size({xlo}, {xhi}, {ylo}, {yhi})")
        self.xlo, self.xhi = xlo, xhi
        self.ylo, self.yhi = ylo, yhi
        plt.xlim( xlo-self.lborder, xhi+self.rborder)
        plt.ylim( ylo-self.bborder, yhi+self.tborder)
    def set_extent(self, xmin, xmax, zmin, zmax):
        logger.debug (f"xsec_draw.set_extent({xmin}, {xmax}, {zmin}, {zmax})")
        plt.xlim( xmin, xmax)
        plt.ylim( zmin, zmax) #since this is a cross section, z means y
    
    def line(self, l):
        '''
        Draw a line
        '''
        L = Line2D(l.x, l.y, lw=l.linethick, c=l.linecolor, ls=l.linestyle, zorder=l.zorder)
        self.axX.add_line(L)
        
    def rect(self, r): 
        '''
        Draw a rectangle, with border and fill
        '''
        logger.debug(str(r))
        if not r.fillcolor:
            self.axX.add_patch(Polygon(r.boundary, closed=True,
                                       fill = False,
                                       edgecolor=r.linecolor,
                                       linewidth=r.linethick,
                                       linestyle=r.linestyle,
                                       zorder=r.zorder))
            
        p = plt.Rectangle(r.anchor, r.width, r.height, 
                          fill=True, 
                          edgecolor=r.linecolor,
                          linewidth=r.linethick,
                          linestyle=r.linestyle,
                          zorder=r.zorder)
        if r.fillcolor:
            p.set_facecolor(r.fillcolor)
        if r.pattern:
            p.set_hatch(r.pattern)
            p.set_edgecolor(r.patterncolor)
        self.axX.add_patch(p)
    
    def polyline(self, polyline):   
        '''
        Draw a polyline
        '''
        self.axX.plot(polyline.xy[:,0], polyline.xy[:,1],
                     color=polyline.linecolor, 
                     lt=polyline.linethick,
                     jointstyle = 'miter')
    
    def symbol(self, x, y, marker, color):
        '''
        Draw a marker at x,y  
        Some marker suggestions:
            'v'  = Tall triangle pointing down
            'D'  = thick diamond
            'd'  = thin diamond
            10 = CARETUPBASE (short triangle pointing up)
            11 = CARETDOWNBASE  (short triangle pointing down)
        '''
        self.axX.plot(x, y, 
                      marker = marker, 
                      color  = color)
        
    def label(self, x, y, txt, **kwargs):
        ''' 
        Draw text at x,y
        '''
        self.axX.text(x,y, txt, **kwargs)
        
    # def publish(self, title=''): 
    #     '''
    #     This is where the output can be directed to the screen or to a file
    #     '''
    #     if title: self.axX.set_title(title)
    #     self.axX.set_axisbelow(True)
    #     plt.show()  

    def publish(self, title=''): 
        '''
        This is where the output can be directed to the screen or to a file
        '''
        if 0:
            if title: self.axX.set_title(title)
            self.axX.set_axisbelow(True)
            plt.show()  
        else:
            from QTguitest import XsecWindow
            M = XsecWindow(plt=plt)


class Test(unittest.TestCase):
    
    def test_grid(self):
           
        from geometry_base import Point, Line, Plyline, Rectangle, cRectangle 
        
        legend = {}
        legend['QUUU']= {'code': 'QUUU', 'label': 'Unconsolidated', 'fillcolor': '#ed9b37', 'patterncolor': '#000000', 'pattern': None, 'linecolor': '#000000', 'linethick': 1.0, 'linestyle': '-'}
        legend['OPDC']= {'code': 'OPDC', 'label': 'Prairie du Chien', 'fillcolor': '#1365df', 'patterncolor': '#000000', 'pattern': None, 'linecolor': '#000000', 'linethick': 1.0, 'linestyle': '-'}
        legend['CJDN']= {'code': 'CJDN', 'label': 'Jordan', 'fillcolor': '#fff52a', 'patterncolor': '#000000', 'pattern': None, 'linecolor': '#000000', 'linethick': 1.0, 'linestyle': '-'}

        D = xsec_draw() 
#         D.set_size(0,1000,700,900)                 # (x0,x1, y0,y1)
        majorticks = ([700, 800, 900], 2.0, 'k' )
        minorticks = ((720,740,760,780,850), 1.0, 'b')
        D.grid(majorticks, minorticks)
        r = cRectangle((300,40),(720,760),**legend['CJDN'])
        D.rect(r)
        r = cRectangle((300,40),(760,860),**legend['OPDC'])
        D.rect(r)
        D.finish()
         


if __name__ == "__main__":
    unittest.main()