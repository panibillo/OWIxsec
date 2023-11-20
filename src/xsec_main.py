'''
Implements a well cross section drawing tool for well construction 
and geologic layers

  MIT License
  
  Copyright (c) 2021 William C. Olsen
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  
  The above copyright notice and this permission notice shall be included in 
  all copies or substantial portions of the Software.
  
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.


TODO:
    Simplify xsec line defs.
        Too many back and forths, it's confusing.
    Do not compute projection lines until after wells are re-spaced for visual
    

classes
-------
xsec_main  
 
Exceptions
----------
None defined yet

Notes
-----
o   The cross section tool is organized into independent modules.  

    +   xsec_cl             Command line interface.
    +   xsec_main.py        Director.
    +   geometry_base       basic shape objects
    +   xsec_legend         legend information
    +   xsec_data_abc       Parent class for data sources.
    +   xsec_data_<source>  reads well information from a particular source 
    +   fence_line          create a fence-line section-line
    +   projected_line      create a straight section-line with wells projected 
                            onto it.
    +   singleton_section_line    A pseudo-section-line showing only one well.
    +   xsec_draw_plt            provides xsec_draw()


o   Overview of the Main module, which is the director, and the responsibilities 
    of each independent modules.  The Main module:
        
    +   Accepts the user input, consisting of:
        -   A list of well ids (required, not empty)
        -   Line or polyline hints (optional)
        -   Drawing option choices
    
    +   Passes the list of well ids to the Data module, which returns the
        xsec_data object. General properties of the xsec_data object include:
        -   The xsec_data object obtains the well xsec_data needed for drawing.
        -   All information about how to obtain the xsec_data is in the xsec_data module.
        -   The xsec_data module is responsible to put the xsec_data into the form
            expected by the main module.
        -   The xsec_data is organized into the drawing element categories
        -   The xsec_data is stored in standardized 'well component' dictionaries.
        -   Elevations are computed if the xsec_data is stored as depths.
    
    +   Requests the output drawing aspect ratio from the output drawing module. 
        -   The aspect ratio determines the relative magnitudes of the 
            horizontal (U) and vertical (Z) dimensions of a local coordinate
            system used to draw the cross section elements.  Using a local 
            coordinate system allows to draw elements whose shapes are 
            independent of the true dimensions. E.g. drawing a "V" to indicate
            the static water level.

    +   Obtains the section line geometry from the Section_Line module.
        An overview of the Section_Line module:
        -   Drawing Options specify Fence line or Projected line.
        -   Passed the xsec_data object (with well coordinates and diameters), 
            the polyline hint (if given), and drawing options.
        -   Returns a polyline being the section line in world coordinates,
            whether a Fence-line or a Projected-line.
        -   If a Projected-Line, returns a list of the line segments that   
            connect each well to the Projection-line.
        -   Returns the unitless U coordinate of each well in the cross-
            section view.  Normalized coordinates range from 0 to 1. 
        -   Adjusts well spacings along the cross section so that all wells
            can be drawn clearly.
        -   Returns a mapping function from world xy coordinates to U values in 
            the cross section view.  In the case of a projected line.  This 
            function accounts for adjusted well spacings and projection.
        -   Returns a scaling function from U values to world distances
        -   Returns a scaling function to scale well diameter dimensions to
            the unitless U-axis for drawing.
    
    +   Obtains the elevation grid lines and vertical scaling information
        from the Vertical_Scaling module.  An overview of the Vertical_Scaling
        module:
        -   Passed the xsec_data object (including well part top and bottom 
            elevations) and drawing options.
        -   The normalized Z coordinate varies from 0 at the bottom to 1 at
            the top.
        -   Returns mapping functions 
            -   from world elevation to Z
            -   from Z to world elevation
    
    +   Obtains scaling information & functions from the output drawing module. 
        -   Defines functions that map the unitless U,V coordinates to the  
            output drawing coordinates.
        -   If matplotlib is used, then the output coordinates will be world 
            coordinates, because matplotlib will rescale to drawing window 
            coordinates on its own.
             
    +   Draw each well in the cross section view.
        -   The main module loops through each well id in the xsec_data object.
        -   For each well id, the main module loops through each well component
            that it is aware of (e.g. casing, litho layer, water level, etc.).
        -   For each well component, the main module defines a procedure that 
            knows how to draw that element in the cross section view.  These 
            procedures:
            -   Know how to extract the appropriate attributes from the xsec_data 
                object. E.g. top elevation, bottom  elevation, width, labeling 
                attributes, etc.
            -   Map the elevation and diameter attributes to the U,V coordinate 
                system.
            -   Create a geometry_base object for the component, passing the U,V 
                values, output scaling functions, and other possible attributes. 
            -   As each geometry_base oject is created, it is passed to the 
                drawing module for output.


    +   geometry_base objects are defined in the normalized U,V coordinate
        system of the cross section view; They are responsible only for creating
        the geometric shapes, and storing passed attributes (e.g labels). 
        -   The main module defines a distinct procedure for each well component 
            to be drawn (e.g. casing, litho layer, water level, etc.), and knows
            how to extract the top elevation, bottom elevation, width, and any
            other required attributes for the particular component from the xsec_data 
            object.
        -   Each distinct procedure in the main module is responsible for 
            mapping the world values extracted from the xsec_data object to the U,V 
            coordinate system of the cross section view, and passing those 
            values to the correct geometry_base object.
        -   The completed geometry_base objects are passed to the Drawing 
            module as they are created.
            
    +   The drawing module stored and for storing that object in the 
            list of output drawing components.
        
    
            to be drawn.  The procedure knows how to extract the needed xsec_data 
            from the xsec_data object, and it knows which geometry_base object to
            use for that component. E.g. Casing, Lithology layer, Water level.
            knows 
        -   The geometry_base oject is passed the component 
    The 
        geometry_base ojects are defined in normalized U,V coordinates of the 
        cross-section view. 
        -   Creates the drawing components as geometry_base types.
        -   Utilizes the well part dicationaries
        -   Creates a geometry_base object for each drawing element.
    
    +   Instantiate a map object?
        -   Draw and label a companion 'map'    

    +   Instantiate a drawing module
        -   The drawing module must implement methods to draw each of the
            geometry_basethe objects
        -   Draw and label the grid
        -   Draw and label each well component in the cross section.
        -   Draw and label the companion map.
        -   Export the drawing to a file format expected by the caller.
        
    +   Returns control to the user 

    
    -   Unknown who is responsible for drawing coloring choices.

o   Requirements
    
    -   numpy
    -   MatPlotLib
    -   pyodbc
    
o   Design goals implemented

    * Draw 1 well vs. many wells
    
    * Option to draw a Fence line vs Projection line
        
    * Show elevation tics
        
o   Design goals not yet implemented

    - Option to emphasize geology vs well construction
        
    - Option to automatically remove less useful records, vs show all wells
        
    - A method for the user to interactivly adjust drawing scaling factors
        
    - Ability to show geologic layer model
        
    - Option to show water chemistry somehow 
    
o   Coordinate systems and variable naming

    - x,y,z :  world coordinates in world units
        + x : easting, e.g. UTM or County Coords
        + y : northing, e.g. UTM or County Coords
        + z : elevation (positive upward), e.g. Mean Sea level.
        +   units of x and y should be the same, but units of z can be different.
    
    - s : distance measured along the section line, beginning at 0 on the left.  
        +   Same scale and units as x and y (world units)
        +   Measured along the fence line (straight segments between sequential 
            points) or measured along one straight line onto which all of the
            well points are projected.  The cummulative length of all segments 
            is the length of the cross section.
    
    - U : Dimensionless horizontal distance along the section line.
        +   U corresponds directly to s, rather than x or y.
        +   U = s/L, where s is defined above, and L is the range of s.
        
    - V : Dimensionless vertical distance.  
        +   V is scaled to U so that U:V matches the aspect ratio of the cross 
            section in the output window.
    
    - u,v : window coordinates defined by an output drawing class.
        +   The origin, and orientation of u and v are determined by the 
            output drawing class.
        +   (s,z) => (U,V) => (u,v) : world coords => unitless coords => screen 
            coords

    - d : diameter of well components in world units.
        +   The diameter units do not have to match x, y, z, or s units.
        +   In Minnesota County Well Index, the size of well components is 
            described by giving the diameter in inches.
            
    - R : Dimensionless well component radius. 
        +   R has the same dimensionless units as U
        +   The scaling ratio from world diameter d to to dimensionless radius R
            is selected so that the well components can be drawn most legibly.
        +   The relationship between R and U is not very meaningful. R can be 
            rescaled independently to improve well component visibility.
        +   Well components are drawn with widths R proportional to the actual 
            component diameters d.
            
    - r : Well component radius in screen coordinates.
        +   Ratio R:r = U:u 

Authors
-------
William Olsen
Dakota County Environmental Resources Department.

Version
-------
0.1  20201201
'''

import numpy as np
import os

from version import __version__ as XSEC_VERSION

from xsec_legend import xsec_legends, map_legends

from singleton_section_line import singleton_section_line 
from fence_line import fenceline 
from projected_line import projected_section_line, update_projection_line_nodes
import geometry_base  

# Select the data source module and import it as xsec_data.
from xsec_data_OWI3 import xsec_data_OWI3 as xsec_data

# import an ouput drawing and publishing module as xsec_draw
from xsec_draw_plt import xsec_draw

import logging
logger = logging.getLogger('xsec_main')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.INFO)

class Xsec_main():
    """
    Direct the data aquisition, analysis, and drawing of the cross section.
     
    Notes
    -----
    o   The main module orchestrates the entire drawing process.  
    
        +   It delegates knowledge of the xsec_data_OWI source to the Data class.  
        
        +   It delegates building the drawing section_line to the section_line 
            module.
        
        +   It delgates converting section_line to output to the Draw class.
        
    o   The module has 4 user methods:
    
        +   __init__() receives the parameter list describing the list of 
            wells and all of the drawing choices.
            
        +   query() uses the Data class to fill internal xsec_data_OWI dictionaries.
        
        +   layout() determines the overall drawing dimensions, sectionline
            section_line, well spacings along the section line, and finally the
            drawing elements themselves.
            
        +   draw() gives the drawing elements to the Draw class, and directs
            it to send the drawing to output.  In the simplest case, the Draw 
            class can open a matplotlib window and wait for that to close. In 
            other cases the draw class may write an image file or files and 
            return the path(s) to those files; or it may put the shapes and 
            attributes into a GIS file for display there.
        
    """
    def __init__(self, cmds, db_name=None, legend_db=None, msg=''):
        ''' 
        Initialize the xsection wells and drawing choices. 
        
        Arguments
        ---------
        cmds : Namespace as returned by argparse module
            The namespace is defined in xsec_cl.py
        
        Notes
        -----    
        o   All arguments are provided by user (e.g. GIS) prior to calling
            database for additional information.  All that is known of the
            wells is their identifiers. All that is known of the section
            line is either nothing, or an approximate section_line.
            
        o   If the well count > 1, and the sectionline is None, then the 
            program will pick the best section line. 
        
        o   If the outwin is not given, the program uses a hard-coded 
            default size associated with the output file type.
            
        o   If the output file extension is not recognized, it is set to a
            hard-coded default type - initially 'png'.
        '''
        self.__version__ = XSEC_VERSION
        self.cmds = cmds   

        # initialize output module
        self.D = xsec_draw()

        # read the legends file
        self.dlegend = xsec_legends(legend_db=legend_db)

        # query for well xsec_data_OWI
        self.data = xsec_data()      
        ok = self.data.read_database(cmds.identifiers, db_name=db_name)   
        if not ok:
            logger.error(f'Error reading {self.data.datasource}')
            return 

        self.data.remove_wid_if_missing_required_components(cmds.required)
        if len(self.data.wids)==1:
            cmds.sectionlinetype = 'singleton'
            cmds.issingleton = True

        self.data.update_diameters()
        self.data.update_zelevations('E' in cmds.required)
        self.data.update_grout_diameters('G' in cmds.includeonly)
#         self.data.find_zlims()
        self.data.ensure_points_have_spread()

        if logger.level == logging.DEBUG:
            print('Debugging xsec_main.__init__() self.data=\n',self.data)
            
        
        # create the section line in world coordinates
        # self.xsec_data_OWI.d_xy is a dict of xy coordinates by wid
        # cmds.userline is an ordered list of (x,y) tuples provided by the user
        if (cmds.sectionlinetype == 'singleton' or 
            len(self.data.wids) == 1 or
            len(cmds.identifiers) == 0):
            sl = singleton_section_line(self.data.d_xy, cmds)
            
        elif cmds.sectionlinetype == 'fenceline': 
            sl = fenceline(self.data.d_xy, cmds) 

        elif cmds.sectionlinetype == 'projected': 
            sl = projected_section_line(self.data.d_xy, cmds) 
        
        self.ordered_wids, self.sectionline, self.normals = sl
        self.snodes = self.sectionline.snodes
        if len(self.data.d_xy) <= 1:
            self.slims = None
        else:
            self.slims = (min(self.snodes), max(self.snodes))
        
                

        # create_gridlines (in world coordinates) 
        # Note that zlims returned are the limits of the gridlines, while
        # xsec_data_OWI.zlims are the limits of the well components..
        self.zlims = self.determine_gridline_elevations()
                
        # Now the basic xsec_data_OWI preparation is completed and the cross section line
        # layout is known.  The legibility of the well drawings in cross section 
        # now depends on scaling factors a, b, and h that control how wide 
        # individual wells are to be drawn, and how close to each other they may
        # be drawn (in the cross section).  The remainder of the code can be 
        # written to allow the user to interactively play with the scaling 
        # factors, for example by building sliders into the interface. The entry
        # point to the code for changing the scaling is at the xsec_draw() method. 
        print ('call draw')
        self.xsec_draw(a=3.0, b=4.0, h=3.5, msg=msg)
        if logging.root.level == logging.DEBUG:
            print (30*"=" + "  END of xsec_main   " + 30*"=")
    
    def determine_gridline_elevations(self,):                 
        ''' Calculate the gridline elevations 
        
        Modifies
        --------
        self.zlims 
            Modified to span from min gridline to max gridline
            
        Notes
        -----
        o   The possible grid spacings are defined in hard coded defaults. The 
            defaults must be defined so that the major spacings are evenly 
            divisible by the minor spacings.
            -   defaults : (max range, minor spacing, major spacing)
        o   The min and max grid elevations contain the min and max elevations
            of all well drawing components.
        '''
         
        zmin, zmax = self.data.zlims 
        zrange = zmax-zmin
        defaults = ((  10, 0.5,   1),
                    (  20, 0.5,   2),
                    (  50,   1,   5),
                    ( 100,   2,  10),
                    ( 200,   5,  20),
                    ( 400,  10,  50),
                    (9999,  20, 100))
        for range, minor, major in defaults:
            if range > zrange:
                # break as soon as range > zrange. This sets minor & major.
                break
        # Determine the min and max grid line elevations.  Reset self.zlims
        gridbase = np.floor(zmin/major)*major  
        gridtop = np.ceil(zmax/major)*major
        
        # Generate the gridlines.
        tol = minor/5
        z = gridbase
        self.major_gridz = []
        self.minor_gridz = []
        while z < gridtop + tol:
            if np.abs(z%major) < tol:
                self.major_gridz.append(z)
            else:
                self.minor_gridz.append(z)
            z += minor
        
        return (gridbase, gridtop)  # zlims belonging to self.
                    
    def xsec_draw(self, a=2.0, b=3.0, h=2.5, msg=''):
        ''' 
        Adjust the xsec scaling factors, and draw the well elements. 
        
        Arguments
        ---------
        a, b, h : float
            Factors affecting width and spacing of wells as drawn in the cross-
            section.   They are defined where implemented.
            
        Notes
        -----    
        o   This function is the entry point for adjusting the visibility 
            factors a, b, and h, in an interface where the user can interactive-
            ly adjust those factors.
        
        o   Recapitulation of dimension systems:
            -   World coordinates:  
                +   x,y : world map coordinates (e.g. feet or meters)
                +   z : world elevations from MSL (mean sea level) 
                        (from land surface if surface elevation is not known)
                +   d : world well diameter dimensions (e.g. inches) 
            -   Vertical cross section view coordinates
                -   s : world distance along the xsec line (d is scaled to x,y)
                -   z : world elevations from MSL (or from land surface) 
                -   U,V : unitless drawing window coordinates (V/U is the aspect ratio)
                -   u,v : drawing program output coordinates. (e.g. pixels.  In the 
                        case of matplotlib, the output coordinates have the same units as
                        units as world coordinates: u=s, v=z)
                    
        o   Mappings from s to U are completed, and not altered. The U mapping 
            is in Unodes.  But the wells may be spaced too close together in 
            Unodes.  The spacing is modified in unodes.  
            
        o   In the case of a projected section line, the points that the wells
            project to on the section line correspond to the unodes, so the 
            layout view should be updated whenever unodes are modified.
             
        o   The vertical dimensions are not altered here.    
        '''
        # Make handy local reference to some self objects: 
        D = self.D
        data = self.data
        
        # get xsec local (U,V) coordinate system bounds 
        U1, Z1 = 1.0, self.D.xsec_aspect_ratio
        self.Ulims = (0, U1)
        self.Vlims = (0, Z1)

        if self.cmds.sectionlinetype == 'singleton':
            # scale slims so that slims/zlims = aspect ratio, and then center.
            self.slims = np.array(self.zlims) * U1/Z1
            self.slims -= np.mean(self.slims)
         
        # Adjust spacing and size of wells for visibility
        self.adjust_Uscaling(a=a, b=b, h=h)
        
        # Because the spacing is adjusted, must also recompute projection lines
        if self.cmds.sectionlinetype == 'projected':
            self.update_normals()
        
        # get the ouput window drawing coordinate limits (u,v)-plane
        ulims, vlims = D.get_output_win(self.slims, self.zlims)
        self.create_scaling_factors(ulims, vlims)
        
        # create well component width dictionaries
        self.calculate_drawing_part_widths()
        
        # draw the grid lines first, so they are in the background.
        self.draw_gridlines(D)
        
        include = self.cmds.includeonly
        
        # draw the geologic layers
        if 'T' in include: self.draw_strat(D)
        
        # draw the well components
        if 'H' in include: self.draw_openhole(D)
        if 'S' in include: self.draw_screen(D)
        if 'G' in include: self.draw_wellgrout(D)
        if 'C' in include: self.draw_wellcasing2(D)
        if 'F' in include: self.draw_hydrofrac(D)
        if 'P' in include: self.draw_perfs(D)
        if 'M' in include: self.draw_pump(D)
        
        # draw the interpreted level markers
        if 'W' in include: self.draw_swl(D)
        if 'B' in include: self.draw_bdrk(D)
        
        # draw labels
        if 'U' in include: self.label_wells(D)
        
        # set the drawing extents  
        D.set_extent(self.ulims[0], self.ulims[1], self.vlims[0], self.vlims[1])

        # draw a map view of the section line, and label the wells.
        D.plot_Map  (self.data.d_xy, self.data.d_label,
                     self.sectionline, self.normals)
        
        D.publish(title=msg)
                
    def calculate_drawing_part_widths(self):
        ''' 
        Calculate widths for drawing components that do not have diameters.
       
        Attributes modified
        -------------------
        dw_strat : float
            Width of litho rectangles. 
            Matches inner casing diameter
             
        dw_aquifer : float 
            Width of aquifer rectangle. Wider than the well, and drawn behind
            other elements, it generally looks like a pair of rectangles with 
            one on either side of the open hole section. It could also be drawn 
            as a pair of rectangles using geometry_base.pairRectangles.
         
        dw_swl : float
            Width of largest diameter + 4"
        
        dw_bdrk : float
            Width of largest diameter + 4"
             
        Returns
        -------
        maxdia : float
            The maximum diameter among all casings in all wells
         
        Notes
        -----
        o   These widths could be computed locally in the method where they are
            used, but by computing them here as a group one can easily see how
            they relate to each other.
        o   The widths are functions of individual well diameters, so are stored
            in dictionaries indexed by wid, and the units of width are the same
            as the diameters.
        o   The width dictionaries are named with prefix "dw_", and use the wid
            as the key.
        o   Present implementation uses scaling factors proportional to the 
            inner well diameter (self.data.d_diameter) or the maximum well
            componenent diameter (self.data.d_maxdia)
        o   For better legibility it may be usefull to use variable scaling  
            factors that scale smaller wells somewhat larger, and larger wells
            somewhat smaller.    
        '''
        self.dw_strat = {}
        self.dw_aquifer = {}
        self.dw_swl = {}
        self.dw_bdrk = {}
        self.dw_pump = {}
        self.dw_perf = {}
        self.dw_hydrofrac = {}
        
        for wid in self.data.wids:
            d0 = self.data.d_diameter.get(wid, self.data.min_display_diameter)
            d1 = self.data.d_maxdia.get(wid, self.data.default_display_diameter)
            self.dw_strat[wid]     = d0
            self.dw_aquifer[wid]   = d1 * 1.3  
            self.dw_swl[wid]       = d1 * 1.2
            self.dw_bdrk[wid]      = d1 * 1.2
            self.dw_pump[wid]      = d1 * 1.15
            self.dw_perf[wid]      = (d0, d1 * 1.2)
            self.dw_hydrofrac[wid] = (d1*1.2, d1 * 1.5)
        return 

    def adjust_Uscaling(self, a=2.0, b=3.0, h=3.5):
        """ 
        Compute scaling factor w2U for well diameter d
        
        Arguments
        ---------
        a, b : float
            Scaling parameters: max diameter is scaled to 1/(a+bN) where N is 
            the number of wells. N is obtained from self.xsec_data_OWI.  
            -   1/(a+b): maximum factor for scaling when N = 1
            -   1/(bN) : minimum factor when N >> 1
                
        h : float
            Scaling factor for drawing clarity: wells cannot be spaced closer
            to each other than h*R, in the xsec view.
            
        Modifies
        --------
        self.Unodelims : (float, float)
            U coordinates of center-lines of the first and last wells in the 
            xsec drawing. These are inset from the Ulims, so that the full
             widths of the first and last wells can be drawn inside of Ulims.

        self.w2U : float
            Scaling factor from well diameter units to well radius in 
            normalized xsec drawing window units.  
        
        Notes
        -----
        maxR : float
            Max diameter in units of U, among all components of all wells.
            A component with diameter d will be drawn with width:
                       width = (d/D)*U/(a+b*N) 
            where U is the total width of the cross-section, D is the maximum
            diameter among all drawing components, and N is the number of wells.
            For a particular drawing component with diameter d: 
                d*w2U  is the radius of the element in units of U. 
                d*rofd  is the radius of the element in units of u. 

        """

        # compute margin widths and scaling of diameters to U.  These are 
        # interdependent because the margin is set equal to the maximum well
        # component diameter as drawn in the U dimensions.  
        # The scaling factor r_Rofd is derived as rho(d->R) in xsec_calc.pdf. 
        # Umlims are the left an right inner margins in U.
        N = len(self.data.wids) #len(self.xsec_data_OWI.d_xy) 
        (U0, U1) = self.Ulims 
        LU = U1-U0  
        dmax = self.data.dmax 
        self.r_Rofd = LU/( (a + b*N + 2)*2*dmax )  # see xsec_calc.pdf
        maxR = 2 * self.r_Rofd * dmax 
        self.Umargin = maxR 
        U0m, U1m = U0 + self.Umargin, U1 - self.Umargin
        self.Umlims = (U0m, U1m)
 
        # Singletons are handled distinctly:
        if len(self.data.wids) == 1:
            # handle case of singleton well
            self.Unodes = np.array([0.0]) 
            self.d_Unodes = { self.data.wids[0]: 0.0 }        
            return
        
        
        # self.sectionline.snodes are cumulative linear coords of wells along a
        # fence-line or a projection-line.
        # self.Unodes are mapping of snodes onto unitless U coordinates,
        # allowing for left and right margins.
        s = self.sectionline.snodes
        s0, s1 = min(s), max(s)
        s2U = (U1m - U0m)/(s1-s0)
        Unodes = U0m + (s-s0) * s2U 

        # Adjust Unodes so that no two nodes are closer than h*r_Rofd times the 
        # average max_diameter of the wells at either end of the segment.    
        # The max diameters are given per node by xsec_data_OWI.d_maxdia[wid].
        # This is a non-trivial problem without a single best answer. We find a
        # simplified approximate solution, by first increasing each segment 
        # length to a fixed minimum length, which increases the overall length, 
        # and then compressing everything back to the correct overall length. 
        Usegments = np.diff(Unodes)  
        dnodes = np.array([self.data.d_maxdia[wid] for wid in self.ordered_wids])
        dsegments = ((dnodes[1:] + dnodes[:-1]) / 2)
        Hsegments = h * self.r_Rofd * dsegments
        adjusted_Usegments = np.max(np.vstack( (Usegments, Hsegments)),0)
        U0nodes = np.hstack(([0], np.cumsum(adjusted_Usegments)))
        
        # The max Unode may now be over the right margin, so the Unodes have to
        # be compressed back to the original spread. The compression brings the 
        # nodes closer together than the criterion, but that will be allowed.
        self.Unodes = U1m + U0nodes * ((U1m - U0m) / np.ptp(U0nodes))
        
        # Create a dictionary of the Unodes by wid. 
        # Use that Unodes are ordered the same as ordered_wids
        self.d_Unodes = {k:v for k,v in zip(self.ordered_wids, self.Unodes)}


    def update_normals(self):
        """ 
        Recompute normals from well points to the line of projection
        """
        # First need to adjust the projection point locations on the projected
        # section line for visibility, this is the polyline in u,v-coorindates.
        update_projection_line_nodes(self.sectionline, self.Unodes)
        
        # The normals for points that are adjusted will be not be exactly normal.
        legend = map_legends()['normals']
        self.normals = []
        for i, wid in enumerate(self.ordered_wids):
            p0, p1 = self.data.d_xy[wid], self.sectionline.xy[i,:] 
            self.normals.append( geometry_base.Line((p0,p1), **legend) )

        
    ################# Scaling for drawing: factors and functions ###############
    def create_scaling_factors(self, ulims, vlims): #snodes, Unodes, maxdia, maxR, zlims):
        """ 
        Finish the factors for coordinate conversions to drawing window
        
        Arguments
        ---------
        ulims, vlims : (float, float), (float, float)
            horizontal and vertical limits of the output window
        
        Modifies
        --------
        self.d_unodes    dict of nodes in u.
        self.unodes      np array used for linear mapping.
        self.u0          mapping offset 
        self.r_uofU      scaling factor
        self.r_rofR      scaling factor
        
        self.v0          mapping offset 
        self.r_vofZ      scaling factor
            
        Notes
        -----
        o   Assumes existence of snodes, Unodes, maxdia, maxR, zlims
        o   ulims include the margin areas, so the scaling factor from U to u
            uses Ulims rather than Umlims.
        o   TODO: Repair inconsistent notation W->R, and w->d    
        o   TODO: Repair inconsistent naming of conversion funcs eg: vofz -> vofz
        """
        # unodes are equal to Unodes shifted to the range of ulims
        self.ulims = ulims
        self.vlims = vlims
        LU = self.Ulims[1] - self.Ulims[0]  
        Lu = ulims[1]-ulims[0]
        self.u0 = ulims[0]
        self.r_uofU = Lu/LU
        
        umargin = self.Umargin * Lu/LU
        if self.cmds.issingleton:
            self.unodes = np.array([np.mean(ulims)])
        else:
            self.unodes =  ulims[0] + umargin + (self.Unodes - self.Unodes[0])*Lu/LU 
        logger.debug(f"unodes: {', '.join(('%d'%u for u in self.unodes))}")

        self.d_unodes = {i:v for i,v in zip(self.ordered_wids, self.unodes)}
        
        # save scaling factors from well diameter (d) in world coordinates to
        # radius (R or r) in xsec coordinates (U or u, respectively).
        # scaling from R to r is the same as from U to u
        self.r_rofR = self.r_uofU 
        self.r_rofd = self.r_rofR * self.r_Rofd
        
    def s2U(self, s):
        """ return U(s), accounting for segment length adjustments"""
        return np.interp(s, self.snodes, self.Unodes)
    def U2u(self, U):
        """ return u(U), accounting for segment length adjustments"""
        return np.interp(U, self.Unodes, self.unodes)
    def s2u(self, s):
        """ return u(s), accounting for segment length adjustments"""
        return np.interp(s, self.snodes, self.unodes)

    def Rofd(self, d):
        """ return dR(d), scaling only, no translation"""
        return d * self.r_Rofd
    def rofd(self, d):
        """ return dr(d), scaling only, no translation"""
        return d * self.r_rofd
    def rofR(self, R):
        """ return dr(R), scaling only, no translation. R is in units of U"""
        return R * self.r_rofR

    # if these continue to use np.interp, then rename to z2V, V2v, adn z2v.
    def Vofz(self, z):
        """ return V(z) """
        return np.interp(z, self.zlims, self.Vlims)
    def vofz(self, z):
        """ return v(z) """
        return np.interp(z, self.zlims, self.vlims)
    def vofV(self, V):
        """ return v(V) """
        return np.interp(V, self.Vlims, self.vlims)
    
    ######################### Drawing components ###############################    
    def draw_gridlines(self, D):  
        """
        Draw horizontal elevation gridlines.
        
        Notes
        -----
        o   The major and minor gridline elevations are determined elsewhere.
        o   Uses ulims as the grid line left and right limits.
        """
        u0,u1 = self.ulims
        minorlegend = self.dlegend['gridminor']
        majorlegend = self.dlegend['gridmajor']
        v = self.vofz
        for z in self.minor_gridz:
            v = self.vofz(z)
            uv = ((u0,v), (u1,v))
            L = geometry_base.Line(uv, zorder=0, label=f'{z}',  **minorlegend)
            D.line(L)
        for z in self.major_gridz:
            v = self.vofz(z)
            uv = ((u0,v), (u1,v))
            L = geometry_base.Line(uv, zorder=0, label=f'{z}',  **majorlegend)
            D.line(L)

    def draw_strat(self, D):
        """
        Illustrate the well stratigraphy
        
        Uses dlz_strat.strat, dw_strat
        """
        legend = self.dlegend['stratlegend']
        v = self.vofz
        
        for wid in self.data.wids:
            if not wid in self.data.dlz_strat:
                continue
            
            try:
                uc = self.d_unodes[wid]
                ro = self.rofd(self.dw_strat[wid])
    #             logger.debug(f"draw_strat {wid} d={self.dw_strat[wid].d}, r={ro}, {dw_strat[wid]}" ) 
                for s in self.data.dlz_strat[wid]:
                    ztop, zbot, code = s.ztop, s.zbot, s.strat
    #                 print ('draw_strat',wid, int(uc), ztop, zbot, code)
                    logger.debug(f"draw_strat {wid}, {ro}, {ztop}, {zbot}, {code}")
                    try:
                        g = legend.get(code, legend.get('missing', None))
                        r = geometry_base.cRectangle((uc, ro), (v(zbot),v(ztop)), zorder=2, **g)
                        D.rect(r)
                    except Exception as e:
                        logger.error ('%s %s'%(wid, e))
                        print (s)
                        print (ztop,zbot,code)
                        print ( (uc, ro), v(zbot), v(ztop) ) 
                        print (code, g)
            except KeyError:
                print (f"KeyError {wid} in draw_strat()")
                     
                
                    
                  
    def draw_wellgrout(self, D, w=4):
        """
        Try to represent the well grout.
        
        Arguments
        ---------
        D : drawing module
        w : a width parameter 
            The grout is drawn as a pair of rectangles outside of the casing.
            Each rectangle has a width of w in world component diameter units.
            
        Notes
        -----
        o   The grout should be drawn in the annular space, but the database may
            not provide sufficiently explict information on both the inner and
            outer diameters and vertical limits of each grout interval.  
        
        o   The present code guesses which casing(s) or annular spaces can be 
            shown as grouted, see xsec_data_MNcw.py: update_grout_diameters(). 
            It guesses that the grout is outside of the casing if the bottom
            elevation of the grout is abover or equal to the casing. 
            stored in dlz_grout, which is read from c4c2, as the inner diamter,
            and makes a simple guess of the outer diameter.
        """
        logger.debug ("draw_wellgrout %s"%(len(self.data.dlz_grout)))
        legend = self.dlegend['groutlegend']
        for wid in self.data.wids:
            try:
                if not wid in self.data.dlz_grout:
                    continue
                 
                uc = self.d_unodes[wid]
                for g in self.data.dlz_grout[wid]:
                    logger.debug(str(g))
                    # d, ztop, zbot = g.d, g.ztop, g.zbot
                    # m = g.material 
                    # ri = self.rofd(d)
                    # ro = ri + self.rofd(w)
                    di,do, ztop, zbot = g.din, g.dout, g.ztop, g.zbot
                    m = g.material 
                    ri = self.rofd(di)
                    ro = self.rofd(do)
  
                    logger.debug(f"draw grout: {wid}, ({di},{do}), ({ri},{ro}), ({ztop},{zbot})")
                    r1,r2 = geometry_base.pairRectangles(uc, ri, ro, (zbot, ztop), zorder=2, **legend[m])
                    D.rect(r1)
                    D.rect(r2)
            except KeyError:
                print (f"KeyError {wid} in draw_wellgrout()")
                 
    def draw_wellcasing2(self, D, c0=0.5, c1=3):
        """ 
        Draw all well casings for a well.
        
        The casing thickness should be large enough to be visible.
        Uses  dlz_casing2
        """
        logger.debug("draw_wellcasing2  %s"%( len(self.data.dlz_casing2)))
        legend = self.dlegend['caselegend']
        v = self.vofz
        for wid in self.data.wids:
            uc = self.d_unodes[wid]
            try:
                if not wid in self.data.dlz_casing2:
                    d = self.data.d_diameter[wid]
                    ztop = self.data.dz_grade[wid]
                    zbot = self.data.dz_casing[wid]
                    ri = self.rofd(d)
                    ro = ri + self.rofd(c0) * c1 
                    logger.debug(f"draw casing2A: {wid}, {d}, {ri},{ro}, {ztop},{zbot}")
                    r1,r2 = geometry_base.pairRectangles(uc, ri, ro, (zbot, ztop), 
                                                         zorder=2, 
                                                         label=f'{d}" casing',
                                                         **legend)
                    D.rect(r1)
                    D.rect(r2)
                    continue
                
                for c in self.data.dlz_casing2[wid]:
                    d, ztop, zbot = c.d, c.ztop, c.zbot
                    ri = self.rofd(d)
                    ro = ri + self.rofd(c0) * c1
                    logger.debug(f"draw casing2B: {wid}, {d}, {ri},{ro}, {ztop},{zbot}")
                    r1,r2 = geometry_base.pairRectangles(uc, ri, ro, (zbot, ztop), 
                                                         zorder=2, 
                                                         label=f'{d}" casing',
                                                         **legend)
                    D.rect(r1)
                    D.rect(r2)
            except KeyError:
                print (f"KeyError {wid} in draw_wellcasing2()")
        
    def draw_wellcasing1(self, D, c0=0.5, c1=3):
        """ 
        Draw a single well casings for a well.
        
        The casing thickness should be large enough to be visible.
        Uses  dz_casing, which holds only a single casing depth as scalar.
        Uses  d_diameter, which holds only a single diameter as scalar.
        """
        logger.debug("draw_wellcasing1  %s"%( len(self.data.dz_casing)))
        legend = self.dlegend['caselegend']
        v = self.vofz
        for wid in self.data.wids:
            if not wid in self.data.dz_casing2:
                self.draw_wellcasing1(D,c0,c1)

            try:
                uc = self.d_unodes[wid]
                for c in self.data.dlz_casing2[wid]:
                    d, ztop, zbot = c.d, c.ztop, c.zbot
                    ri = self.rofd(d)
                    ro = ri + self.rofd(c0) * c1
                    logger.debug(f"draw casing2: {wid}, {d}, {ri},{ro}, {ztop},{zbot}")
                    r1,r2 = geometry_base.pairRectangles(uc, ri, ro, (zbot, ztop), 
                                                         zorder=2, 
                                                         label=f'{d}" casing',
                                                         **legend)
                    D.rect(r1)
                    D.rect(r2)
            except KeyError:
                print (f"KeyError {wid} in draw_wellcasing1()")

          
    def draw_openhole(self, D):
        """
        Illustrate the aquifer code over the length of the openhole
        
        The openhole itself is not really illustrated.
        
        If the openhole is not entered in dz_openhole, then other sources are 
        examined to find a best way to illustrate the aquifer code.
         
        Uses dz_openhole, dz_bot, dz_casing, dz_grade, dw_aquifer
        dlz_screen might also be used, but that is not implemented here.
        """
        logger.debug(f"draw_openhole: {len(self.data.dz_openhole)}, {len(self.data.d_aquifer)}")  
                             
        legend = self.dlegend['aquiferlegend']
        v = self.vofz

        for wid in self.data.wids:
            try:
                if wid in self.data.dz_openhole:
                    ztop = self.data.dz_openhole[wid].ztop
                    zbot = self.data.dz_openhole[wid].zbot
                elif wid in self.data.dz_bot and wid in self.data.dz_casing:
                    ztop, zbot = self.data.dz_casing[wid], self.data.dz_bot[wid]
                elif wid in self.data.dz_bot and wid in self.data.dz_grade:
                    ztop, zbot = self.data.dz_grade[wid], self.data.dz_bot[wid]
                else:
                    continue
                d = self.dw_aquifer[wid]  
    
                ro = self.rofd(d)
                uc = self.d_unodes[wid]
                logger.debug(f"dbg draw_ohole {wid} d={d}, r={ro} (d=dw_aquifer[wid] * 1.5)" )
                aquifer = self.data.d_aquifer.get(wid, '')
                g = legend.get(aquifer, legend.get('missing', None))
                
                # simply draw the openhole behind the other well parts, but twice as wide.
                if d and ztop and zbot: 
                    vb,vt = v(zbot), v(ztop)
                    r = geometry_base.cRectangle((uc, ro), (vb,vt), zorder=0, **g)
                    D.rect(r)
                elif (d and aquifer and wid in self.data.dz_grade 
                                    and wid in self.data.dz_bot): 
                    vb,vt = v(zbot), v(ztop)
                    ztop, zbot = self.data.dz_grade[wid], self.data.dz_bot[wid]
                    r = geometry_base.cRectangle((uc,ro), (vb,vt), zorder=0, **g)
                    D.rect(r)
            except KeyError:
                print (f"KeyError {wid} in draw_openhole()")
         
    def draw_screen(self, D):
        """
        Illustrate the well screens
        
        Uses dlz_screen 
        """
        logger.debug(f"draw_screen: {len(self.data.dlz_screen)}")  
                             
        legend = self.dlegend['screenlegend']
        v = self.vofz

        for wid in self.data.wids:
            if not wid in self.data.dlz_screen:
                continue
            try:
                uc = self.d_unodes[wid]
                for c in self.data.dlz_screen[wid]:
                    d, ztop, zbot = c.d, c.ztop, c.zbot
                    ri = self.rofd(d)
                    logger.debug(f"draw screen: {wid}, {d}, {ri}, {ztop},{zbot}")
                    
                    D.line( geometry_base.Plyline(((uc-ri,ztop), (uc-ri,zbot)), zorder=2, **legend) )
                    D.line( geometry_base.Plyline(((uc+ri,ztop), (uc+ri,zbot)), zorder=2, **legend) )
            except KeyError:
                print (f"KeyError {wid} in draw_screen()")


         
    def draw_perfs(self, D, w=3):
        """ 
        Represent the well perforation intervals
        
        Perforation intervals are not entered in CWI.
        Uses dlz_perf  
        """
        logger.debug (f"draw_perfs: {len(self.data.dlz_perf)}")
        legend = self.dlegend['perflegend']
        v = self.vofz

        for wid in self.data.wids:
            if not wid in self.data.dlz_perf:
                continue
            try:
                uc = self.d_unodes[wid]
                for o in self.data.dlz_perf[wid]:
                    d, ztop, zbot = o.d, o.ztop, o.zbot
                    ri = self.rofd(d)
                    ro = ri + self.rofd(w)
                    logger.debug (f"draw perf:  {wid}, {d}, {ri},{ro}, {ztop},{zbot}")
                    r1,r2 = geometry_base.pairRectangles(uc, ri, ro, (zbot, ztop), 
                                                         zorder=2, 
                                                         label=f'{d}" perf',
                                                         **legend)
                    D.rect(r1)
                    D.rect(r2)
            except KeyError:
                print (f"KeyError {wid} in draw_perfs()")

    def draw_hydrofrac(self, D):
        """ 
        Represent the hydrofrac intervals
        
        Uses dz_hydrofrac, dw_hydrofrac
        """
        logger.debug (f"draw_hydrofrac: {len(self.data.dz_hydrofrac)}")
        if len(self.data.dz_hydrofrac) == 0: 
            return 
        legend = self.dlegend['hfraclegend']
        v = self.vofz

        for wid in self.data.wids:
            if not wid in self.data.dz_hydrofrac:
                continue
            try:
                ztop = self.data.dz_hydrofrac[wid].ztop
                zbot = self.data.dz_hydrofrac[wid].zbot
                uc = self.d_unodes[wid]
                id, od = self.dw_hydrofrac[wid]
                ri = self.rofd(id)
                ro = self.rofd(od)  
                r1,r2 = geometry_base.pairRectangles(uc, ri, ro, (zbot, ztop), 
                                                     label='hydrofrac', 
                                                     zorder=2, **legend )
                D.rect(r1)
                D.rect(r2)
            except KeyError:
                print (f"KeyError {wid} in draw_hydrofrac()")

    def draw_swl(self, D):
        """ 
        Draw a swl symbol 
        
        A symbol and a short horizontal line are drawn left of the well casing.
        Uses  data.dz_swl, dw_swl
        """ 
        logger.info (f"draw_swl: {len(self.data.dz_swl)}")
        legend = self.dlegend['swllegend']
        Z = self.Vofz
        R = self.Rofd
        u = self.U2u
        r = self.rofR
        v = self.vofV

        for wid in self.data.wids:
            if not wid in self.data.dz_swl:
                continue
            try:
                z = self.data.dz_swl[wid]
                Uc = self.d_Unodes[wid]
                b = r(R(self.dw_swl[wid]))
                uc = u(Uc)
               
                # horizontal SWL line
                ul, ur, v1 = uc-b, uc-b/2, v(Z(z))
                SWL_baseline = ((ul,v1), (ur,v1))
                D.line( geometry_base.Plyline(SWL_baseline, zorder=2, **legend) )
                D.symbol(ul, v1, '>', legend['linecolor'])
                logger.debug (f"DBG1159_draw_swl   {wid} d={self.dw_swl[wid]:4.2f}, r={b} (z={z}, v={v1})" )
            except KeyError:
                print (f"KeyError {wid} in draw_swl()")
            
    def draw_bdrk(self, D):
        """ 
        Draw a bedrock symbol (horizontal line with symbol at one end) 
                
        A symbol and a short horizontal line are drawn right of the well casing.
        Uses  data.dz_bdrk, dw_swl
        """ 
        logger.debug (f"draw_bdrk: {len(self.data.dz_bdrk)}")
        legend = self.dlegend['bdrklegend']
        Z = self.Vofz
        R = self.Rofd
        u = self.U2u
        r = self.rofR
        v = self.vofV

        for wid in self.data.wids:
            if not wid in self.data.dz_bdrk:
                continue
            try:
                z = self.data.dz_bdrk[wid]
                Uc = self.d_Unodes[wid]
                ri = r(R(self.dw_strat[wid]))
                ro = r(R(self.dw_swl[wid]))
                uc = u(Uc)
                # horizontal bdrk line
                ul, ur, v1 = uc+ri, uc+ro, v(Z(z))
                bdrk_baseline = ((ul,v1), (ur,v1))
                D.line( geometry_base.Plyline(bdrk_baseline, zorder=2, **legend) )
                D.symbol(ur, v1, '<', legend['linecolor'])
                logger.debug (f"DBG1190_draw_bdrk  {wid} d={self.dw_swl[wid]}, ru={ri,ro} (z={z}, v={v1})" )
            except KeyError:
                print (f"KeyError {wid} in draw_bdrk()")
            
    def draw_pump(self, D):
        """
        Draw a pump symbol  
                
        The symbol is drawn at the elevation of the bottom of the drop pipe,
        and offset to the left of center by dw_pump[wid]
        Uses  data.dz_droppipe, dw_pump
        """ 
        logger.debug (f"draw_pump: {len(self.data.dz_droppipe)}")
        legend = self.dlegend['droppipelegend']
        Z = self.Vofz
        u = self.U2u
        v = self.vofV
        r = self.rofd

        for wid in self.data.wids:
            if not wid in self.data.dz_droppipe:
                continue
            try:
                zbot = self.data.dz_droppipe[wid].zbot
                d = self.dw_pump[wid]
    
                Uc = self.d_Unodes[wid]
                uc = u(Uc)
                vc = v(Z(zbot))
                ur = r(d)
                D.symbol(uc-ur, vc, **legend['pump'] )
                logger.debug(f"dbg draw_pump: {wid} zbot={zbot}, {d}, {ur}" )
            except KeyError:
                print (f"KeyError {wid} in draw_pump()")
            
    def label_wells(self, D, l=5):
        """
        Draw a well label above the well in the cross section.
        
        Arguments
        ---------
        D : Drawing object
        
        l : number
            Vertical spacing in world coords for label above top of well.
        
        Uses d_label, dz_grade
        """
        v = self.vofz
        for wid in self.data.wids:
            if (wid in self.data.d_label and 
                wid in self.d_unodes and 
                wid in self.data.dz_grade):
                D.label(self.d_unodes[wid], v(self.data.dz_grade[wid]+l), 
                        self.data.d_label[wid],
                        horizontalalignment='center')

        
    
if __name__ == '__main__':
    db_name = "/home/bill/data/MN/OWI/OWI40.sqlite"
    from xsec_cl import xsec_parse_args 
    cmds = xsec_parse_args('-i 593637')
    cmds = xsec_parse_args('-i 520048')
#    cmds = xsec_parse_args('-i 509077')
#    cmds = xsec_parse_args('-i 449114') #not working for grout
    xsec = Xsec_main(cmds, db_name=db_name)
      
    print (r'\\\\\\\\\\\\ --DONE xsec_main -- //////////////')