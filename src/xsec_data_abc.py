'''
Created on May 16, 2021

classes
-------
xsec_data_abc

namedtuples
-----------
Casing
Openhole
Droppipe
Hydrofrac
Hole
Screen
Strat
Grout
Perf

methods
-------
isnum

Notes
----- 
o   xsec_data_abc is a base class that should be inherited by your specific 
    concrete data source class.  
    
o   xsec_data_abc names 1 abstract method that your concrete class must 
    implement:
    +   read_database()
    
o   Your read_database() method should perform the following steps in order:
    1   Read raw data into the source data dictionaries define in xsec_data_abc
        __init__() method.
    2   Call self.remove_wid_if_missing_required_components
    3   Call self.find_zlims
    4   Call self.update_diameters
    5   Call self.ensure_points_have_spread
    6   Return True if data remains, or False if there is nothing to draw.

o   xsec_data_abc implements 3 methods do not need to be overridden.  These 
    methods should be the same for all concrete classes that inherit the abc.
    +   __init__()
    +   __str__()
    +   ensure_points_have_spread()    

o   xsec_data stores data in value dictionaries and component dictionaries.
    +   Value dictionaries store a single value for each entry.  The values may
        be used for one or more drawing components.
    +   Component dictionaries store namedtuple's describing a particular 
        well component or drawing element.  namedtuples are used so that the  
        modules can reference values explicitly by the variable names rather 
        than by index numbers.

    +   All dictionaries use the same keys. The keys are unique well record 
        identifiers, such as the database relation identifier, or a Unique Well 
        Number (with limitations). The index is commonly referred to as "wid" or 
        "i" in all xsec python modules.
    
o   Notes on using namedtuple's
    -   A namedtuple must be initialized with a complete, and correcty ordered, 
        set of values. e.g.:
        +   d[wid] = Coord(x,y)
        +   d[wid] = Label(*row)  # where row is a complete tuple of values
    
    -   A namedtuple is immutable, but can be updated using method ._replace()
        which takes on or more keyword arguments. e.g.
        +   NT = NT._replace(diameter=12) o
        +   NT = NT._replace(**{'diameter':12})



Notes Oct 30, 2021
    xsec_data_base has only one abstract method:
        read_database
        
    It has several generic methods that synchronize with xsec_cl, xsec ...
        remove_wid_if_missing_required_components
        find_zlims
        update_diameters
        ensure_points_have_spread
    inherited by xsec_data_<mydatasrc>
        read_database
        
    -   read_database reads everything from the db and stores in data structures 
        defined (here?) includeing dz_<component> & dlz_<component>.
        calls remove_wid_if_missing_required_components()
        calls find_zlims()
        calls update_diameters()
        calls ensure_points_have_spread()

@author: Bill Olsen
'''

import abc
from collections import defaultdict , namedtuple
from dataclasses import dataclass
import unittest

def isnum(n):
    """ Return True if n is a number, else False """
    try:
        y = n+1
        return True
    except:
        return False


'''
Define Dataclasses used in the data dictionaries.
The Dataclasses with elevation data all inherit the mixin class z_updater.
When filling the Dataclasses with data, use None for missing data.

Coord is defined as a namedtuple rather than a Dataclass, because it is simpler
and is often accessed as a tuple.
'''

Coord = namedtuple('Coord',   ['x','y'])

class z_updater:
    """ 
    A mixin class for updating z values from depths and a given datum
    """
    def updatez(self, datum):
        try:
            self.ztop = datum - self.depth_top
            self.zbot = datum - self.depth_bot
        except Exception as e:
            print (f"Error in updatez {self.ztop}, {self.zbot}, {datum}\n{e}")
            
@dataclass
class Casing(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
 
@dataclass
class Droppipe(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
 
@dataclass
class Grout(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
    material : str
    amount : str
    units : str

@dataclass
class Hole(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
 
@dataclass
class Hydrofrac(z_updater):
    wid : int
    label : str
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
 
@dataclass
class Openhole(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
 
@dataclass
class Perf(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
    method : str
 
@dataclass
class Screen(z_updater):
    wid : int
    label : str
    d : float
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
    material : str
    slot : int
 
@dataclass
class Strat(z_updater):
    wid : int
    label : str
    depth_top : float
    depth_bot : float
    ztop : float
    zbot : float
    length : float
    drllr_desc : str
    color : str
    hardness : str
    strat : str
    lith_prim : str
    lith_sec : str
    lith_minor : str
    

class xsec_data_abc(abc.ABC):
    """
    Provide generic methods & base class representation for an actual data class.
    
    Methods
    -------
    __init__ : Initialize all of the drawing component containers
    
    read_database : Must be implemented by inheriting class
    
    remove_wid_if_missing_required_components : Implements command-line option "-R" 
    
    ensure_points_have_spread : Handles one special degenerate locations case.
    
    
    Notes
    -----
    o   Initialization of all component dictionaries in the init method puts 
        them all in a common place for reference.

    o   The wids are the unique well identifiers.  They can be any immutable
        type, but are anticipated to be strings or numbers.

    o   The component dictionaries are all indexed by wid. 

    o   Components that can have only one value per well, such as location 
        or total depth, are kept in single level dictionaries named either
        d_<item> or dz_<item>.  The 'z' in 'dz_' is a reminder that the 
        attributes include depths, and that the depths have been expressed as
        elevations (z).

    o   Components that can have multiple entries per well, such as casing
        or grout, are kept in 2-level dictionaries named dlz_<item>. The 
        second level is a list of the entries.  The 'l' in 'dlz_' is a reminder
        that the dictionary values are lists of entries.

    o   The entries are either individual objects, like a string label or a  
        number elevation, or they are named tuples.  
        
    o   The namedtuple field names are strictly lower case!  

    o   The component dictionaries store all data in world units.  The read_data
        method does not do coordinate or unit conversions other that to keep the
        units consistent:
        -   Locations are stored using the x,y coordinates in the data source.
        -   Vertical information is stored as elevations above Mean Sea Level.
        -   Well component diameters are stored as diameters in consistent units.
    """ 
    def __init__(self):
        self.datasource = 'Data not yet read from source'
        self.wids = []
        
        # These dictionarys have one value or one namedtuple for each wid.
        self.d_label    = dict() #{wid : well_label,...}
        self.d_iwid     = dict() #{identifier : wid... }
        self.d_xy       = dict() #{wid : Coord,...     }
        self.d_aquifer  = dict() #{wid : aquifer,...   }
        self.dz_grade   = dict() #{wid : grade elevation,...}
        self.d_diameter = dict() #{wid : inner diameter,...}
        self.d_maxdia   = dict() #{wid : maximum well part diameter,...}
        self.dz_bot     = dict() #{wid : well bottom elev, ...}
        self.dz_swl     = dict() #{wid : static water level, ...}
        self.dz_bdrk    = dict() #{wid : bedrock elevation, }
        self.dz_casing  = dict() #{wid : casing bottom elev, ... }
        self.dz_openhole= dict() #{wid : Openhole(),... }
        self.dz_droppipe= dict() #{wid : Droppipe(),... }
        self.dz_hydrofrac = dict() #{wid : Hydrofrac(),... }
            
        # These dictionaries have a list of namedtuples for each wid
        self.dlz_casing2 = defaultdict(list) #{wid : [Casing(),..], ...}  
        self.dlz_perf    = defaultdict(list) #{wid : [Perf(),..], ...} 
        self.dlz_hole    = defaultdict(list) #{wid : [Hole(),..], ...} 
        self.dlz_grout   = defaultdict(list) #{wid : [Grout(), ...}
        self.dlz_screen  = defaultdict(list) #{wid : [Screen, ...], ...}
        self.dlz_strat   = defaultdict(list) #{wid : [Strat, ...], ...}
        
#         # Provide a list of all of the commonent dictionaries
#         self.componentdicts = (
#             self.d_label, 
#             self.d_xy,
#             self.d_aquifer,
#             self.dz_grade,
#             self.d_diameter,
#             self.d_maxdia,
#             self.dz_bot,
#             self.dz_swl,
#             self.dz_bdrk,
#             self.dz_casing,
#             self.dz_openhole,
#             self.dz_droppipe,
#             self.dz_hydrofrac,
#             self.dlz_casing2,
#             self.dlz_perf,
#             self.dlz_hole,
#             self.dlz_grout,
#             self.dlz_screen,
#             self.dlz_strat) 
        
       
    def __str__(self):  
        rv = [f"{25*'='}  xsec xsec_data_MNcwi  {25*'='}", 
              f'xsec_data_MNcwi source = {self.datasource}']
        if not self.datasource:
            return '\n'.join(rv)
        rv.append(f"There are {len(self.wids)} wells")
        for wid in self.wids:
            rv.append(f"well({wid}) : {self.d_label[wid]}")
            for n,d in (('xy'       , self.d_xy        ),
                        ('aquifer'  , self.d_aquifer   ),
                        ('grade'    , self.dz_grade    ),
                        ('diameter' , self.d_diameter  ),
                        ('maxdia'   , self.d_maxdia    ),
                        ('bot'      , self.dz_bot      ),
                        ('swl'      , self.dz_swl      ),
                        ('bdrk'     , self.dz_bdrk     ),
                        ('casing'   , self.dz_casing   ),
                        ('openhole' , self.dz_openhole ),
                        ('droppipe' , self.dz_droppipe ),
                        ('hydrofrac', self.dz_hydrofrac) ):
                if wid in d:
                    rv.append(f"  {n:<9s}: {d[wid]}")        
                        
            for n,d in (('casing2'  , self.dlz_casing2 ),  
                        ('perf'     , self.dlz_perf    ),  
                        ('hole'     , self.dlz_hole    ),
                        ('grout'    , self.dlz_grout   ),  
                        ('screen'   , self.dlz_screen  ),  
                        ('strat'    , self.dlz_strat   ) ):
                if not wid in d:
                    continue
                rv.append (f"  {n:<9s}:")
                for v in d[wid]:
                    rv.append (f"{' ':13}{str(v)}")

        rv.append(f"{63*'='}")
        return '\n'.join(rv)      
                          
    @abc.abstractmethod
    def read_database(self, cmds):
        """ 
        Retrieve & store well xsec_data_MNcwi required by class xsec_main for wells in identifiers
         
        Arguments
        ---------
        cmds : Namespace as returned by argparse.
            The namespace is defined in xsec_cl.py.  The only property that is 
            required to be defined is cmds.identifiers
         
        Returns
        -------
        True  : if successful and xsec_data_MNcwi is likely to generate a valid section line, 
        False : if an error occurs
         
        Notes
        -------
        This abstract base class defines the basic functions that return xsec_data_MNcwi
        needed by the xsec drawing algorithms. Data requests are per well, using
        the wid. The wid is the unique well identifier used throughout. It might
        be a Unique Well Number, but is more likely a relational identifier.
         
        The concrete class that inherits this base class must:
        -   Implement methods to query a xsec_data_MNcwi source, such as CWI, to obtain the  
        required well xsec_data_MNcwi, given a list of wid values.
        -   Store the xsec_data_MNcwi in Python dictionaries indexed by wid.  
         
        The functions defined here in the abstract base class illustrate what 
        xsec_data_MNcwi is needed, and how it can be stored.  
         
        The methods defined in this abstract base class assume that the vertical 
        coordinate information is stored as elevations above a common datum.
        A concrete implementation may  store the information in another manner 
        if it also overwrites these abstract methods.  A concrete implementation 
        may not need all of these methods, and is free to implement additional 
        methods and xsec_data_MNcwi components.
        """
        raise NotImplementedError

    def read_data(self,cmds):
        """
        Read data from data source, assign to elements, and filter using cmds.
        
        Arguments
        ---------
        cmds :    
        
        Notes
        -----
        o   Performs central orchestration of data reading and preparation.
        
        o   Knowledge of how to get the data and assign to the xsec drawing
            elements is delegated to read_database().
        
        o   
        """ 
        self.read_database(cmds.identifiers)
        self.remove_wid_if_missing_required_components(cmds.required)
        self.find_zlims()
        self.update_diameters()
        self.ensure_points_have_spread()
        return ( len(self.d_xy) > 0 )


#     @abc.abstractmethod
#     def remove_wid_if_missing_required_components(self, required):   
#         """ 
#         Remove data if well is missing required components.
#         
#         Arguments
#         ---------
#         required : list
#             Elements of the list are symbols corresponding to required well
#             components as specified in xsec_cl -R --required choices.  Each 
#             choice is associated with a drawing method in xsec_main, and the
#             data dictionary(s) that are required to have data for each drawing
#             component can be determined by examining those methods.  
#         """
#         raise NotImplementedError

    def remove_wid_if_missing_required_components(self, required):
        """ 
        Remove data if well is missing required components.
        
        Arguments
        ---------
        required : list
            Elements of the list are symbols corresponding to required well
            components as specified in xsec_cl -R --required choices.  Each 
            choice is associated with a drawing method in xsec_main, and the
            data dictionary(s) that are required to have data for each drawing
            component can be determined by examining those methods.  
        
        Modifies
        --------
        self.wids : removes values that will not end up in final drawing
        self.d_xy : removes values that will not end up in final drawing
            
        Notes
        -----
        o   Implementation of a drawing component requrires synchronizing of the
            component dictionaries in several places:
            
            -   xsec_main: drawing methods will refer to specific data dict(s)
                for drawing of each well component. 
                dictionaries in the data module
            
            -   xsec_data_abc.__init__() must initialze the dictionary(s),
#                 and add them to the list "componentdicts"
            
            -   xsec_data.read_data() must read the data into the dictionary(s)
            
            -   xsec_cl interprets user directives to include, exclude, require, 
                or not-require specific drawing elements. Each directive needs
                to be handled.  This method verifies that it handles each 
                required component defined in xsec_cl under components2_choices
            
        o   Any well missing one or more required elements is removed from 
            self.wids.  The final set of wids is computed as the intersection of 
            the sets of wids that are linked to each of the required elements.
        """
        from xsec_cl import components2_choices 
        cl_choices = list(components2_choices)
        
        wids = set(self.wids)
        cl_unhandled = []
        for c in cl_choices:
            if   c=='B':  # bdrk_depth
                if c in required:
                    wids = wids.intersection(set(self.dz_bdrk.keys()))
            elif c=='C':  # casings 
                if c in required:
                    wids = wids.intersection(set(self.dlz_casing2.keys()))
            elif c=='E':  # Elevation
                if c in required:
                    wids = wids.intersection(set(self.dz_grade.keys()))
            elif c=='F':  # hydrofrac 
                if c in required:
                    wids = wids.intersection(set(self.dz_hydrofrac.keys()))
            elif c=='G':  # grout 
                if c in required:
                    wids = wids.intersection(set(self.dlz_grout.keys()))
            elif c=='H':  # hole 
                if c in required:
                    i = set(self.dz_casing.keys()).union(self.dz_grade)
                    wids = wids.intersection(i)
                    wids = wids.intersection(set(self.dz_bot.keys()))
            elif c=='M':  # pump, uses droppipe length
                if c in required:
                    wids = wids.intersection(set(self.dz_droppipe.keys()))
            elif c=='P':  # perforations 
                if c in required:
                    wids = wids.intersection(set(self.dlz_perf.keys()))
            elif c=='S':  # screen 
                if c in required:
                    wids = wids.intersection(set(self.dlz_screen.keys()))
            elif c=='W':  # static_water_level 
                if c in required:
                    wids = wids.intersection(set(self.dz_swl.keys()))
            elif c=='T':  # stratigraphy 
                if c in required:
                    wids = wids.intersection(set(self.dlz_strat.keys()))
            elif c=='U':  # labels
                pass
            else:
                cl_unhandled.append(c)

        assert not(cl_unhandled), f'Unhandled required elements: {cl_unhandled}'  
                
        if len(wids) != len(self.wids):
            omitted  = set(self.wids) - wids
            print ('The following wells are ommitted because they lack one' +
                   ' or more required components: ' + str(required))
            print (', '.join((str(o) for o in omitted)))
            self.wids = tuple(wids)
            self.d_xy = {wid: self.d_xy[wid] for wid in self.wids}
        
#             self.wids = list(wids)
#             for wid in omitted:
#                 for d in self.componentdicts:
#                     if wid in d:
#                         d.pop(wid)

    def _update_zminmax(self, z): 
            self.zmin = min(self.zmin, z)   
            self.zmax = max(self.zmax, z)  

    def find_zlims(self):
        """ 
        Look through all data dictionaries to find min and max z values.
        
        Notes
        -----
        o   We assume that all identifiers in self.wids are to be included in 
            the cross section, but we do not assume the same of all identifiers
            in the component dictionaries - even though it might be true.
            
        o   This may be called after a well is removed from the cross section
            for any reason at any time.
        """
        BIGNUM = 9e9
        self.zmin, self.zmax = BIGNUM, -BIGNUM

        for wid in self.wids:
            # First work through dictionaries with scalar values
            if wid in self.dz_grade:
                self._update_zminmax(self.dz_grade[wid])
            if wid in self.dz_bot:
                self._update_zminmax(self.dz_bot[wid]) 
            if wid in self.dz_swl:          
                self._update_zminmax(self.dz_swl[wid])
            if wid in self.dz_bdrk:          
                self._update_zminmax(self.dz_bdrk[wid])
            if wid in self.dz_casing:          
                self._update_zminmax(self.dz_casing [wid])
            
            # Second work through dictionaries with namedtuple values.
            if wid in self.dz_openhole:          
                self._update_zminmax(self.dz_openhole[wid].zbot)
            if wid in self.dz_droppipe:          
                self._update_zminmax(self.dz_droppipe[wid].zbot)
            if wid in self.dz_hydrofrac:          
                self._update_zminmax(self.dz_hydrofrac[wid].zbot)

            # Third work through dictionaries with lists of namedtuples.
            if wid in self.dlz_casing2:    
                for rec in self.dlz_casing2[wid]:      
                    self._update_zminmax(rec.zbot)
            if wid in self.dlz_perf:    
                for rec in self.dlz_perf[wid]:      
                    self._update_zminmax(rec.zbot)
            if wid in self.dlz_screen:    
                for rec in self.dlz_screen[wid]:      
                    self._update_zminmax(rec.zbot)
            if wid in self.dlz_hole:    
                for rec in self.dlz_hole[wid]:      
                    self._update_zminmax(rec.zbot)
            if wid in self.dlz_grout:    
                for rec in self.dlz_grout[wid]:      
                    self._update_zminmax(rec.zbot)
            if wid in self.dlz_strat:    
                for rec in self.dlz_strat[wid]:      
                    self._update_zminmax(rec.zbot)

        self.zlims = [self.zmin, self.zmax]    

    def update_zelevations(self, z_required):
        """
        Fill-in or update z-vals, and update z range variables.
        
        Arguments
        ---------
        
        Modifies
        --------
        All dataclasses having elevation properties .ztop & .zbot 
        self.zmin
        self.zmax 
        
        Notes
        -----
        -   Works through every dataclass, so it must know of every dataclass 
            with elevation properties .ztop & .zbot
        -   Because this updates zmin and zmax, only wids that will be included 
            in the drawing should be touched.  Be sure to call this after wids
            have been filtered for final inclusion.
        -   When this is called, 
        -   self.dz_grade = dict(wid, z_elevation). If the data source is 
            missing an elevation, then the key (wid) is missing. I.e, missing
            elevations are not entered as 0 or None.
        """    
        #         # Global limits
        if len(self.wids) == 0:
            return False
        elif len(self.wids) == 1 and not self.dz_grade:
            if z_required:
                print(f"No elevation. cannot draw section: {self.wids}")
                return False
            else:
                # Special case: 1 well, no z elevation: set z = 0 and plot as depth
                self.dz_grade[self.wids[0]] = 0
        else:
            m = set(self.wids) - set(self.dz_grade.keys()) 
            if not len(m)==0:
                if z_required:
                    print(f"Missing elevations. Cannot draw section: {(str(v) for v in m)}")
                    return False
                else:
                    # Arrive here if z_required==False, and at least one well
                    # is missing from dz_grade.  
                    # In this case, we have to set dz_grade to 0 for all wids.
                    self.dz_grade = {wid:0 for wid in self.wids}

        BIGNUM = 9e9
        self.zmin, self.zmax = BIGNUM, -BIGNUM

        for wid in self.wids:
            z = self.dz_grade[wid]
            self._update_zminmax(z)

            # First work through dictionaries with scalar values.  
            # Upon entry, all except dz_swl are filled with depths rather than 
            # elevations. dz_swl might have either, and the distinguishing 
            
            for dz in (self.dz_bot,
                       self.dz_swl,
                       self.dz_bdrk,
                       self.dz_casing):
                if wid in dz:
                    dz[wid] = z - dz[wid]
                    self._update_zminmax(dz[wid])
            
            # Second work through dictionaries with Dataclass values.
            # Upon entry, these have depths but not elevations entered.
            for dz in (self.dz_openhole,
                       self.dz_droppipe,
                       self.dz_hydrofrac):
                if wid in dz:
                    dz[wid].updatez(z)
                    self._update_zminmax(dz[wid].zbot)
            
            # Third work through dictionaries with lists of namedtuples.
            # Upon entry, these have depths but not elevations entered.
            for dz in (self.dlz_casing2,
                       self.dlz_perf,
                       self.dlz_screen,
                       self.dlz_hole,
                       self.dlz_grout,
                       self.dlz_strat):
                if wid in dz:
                    for dc in dz[wid]:
                        dc.updatez(z)
                        self._update_zminmax(dc.zbot)
                        
        self.zlims = [self.zmin, self.zmax]     
     
            
    def update_diameters(self):
        """
        Fill-in or update diameter, and update diameter range variables.
        
        Modifies
        --------
        .d property (diameter) of any dataclass object when value is missing 
        self.d_maxdia[wid]  (max diameter among all elements at each well)
        self.dmin           (min diameter among all elements among all wells)
        self.dmax           (max diameter among all elements among all wells) 
        
        Notes
        -----
        -   Works through every dataclass, so it must know every dataclass 
            with that has a .d property (diameter).
        -   Because this updates global dmin and dmax, only wids that will be  
            included in the drawing should be touched.  Be sure to call this 
            after wids have been filtered for final inclusion.
        
        TODO: The min_display_diameter is used as a default, but it may draw a
              component on the inside of a well that logically belongs on the 
              outside, such as drawing construction grout inside of a casing.
              The solution is to break this algorithm down into more steps that 
              build in the kind of logic that knows how different well 
              components should relate to each other.  A hazard of doing this
              however is that it may misleadingly display a correct looking 
              construction when there is no actual evidence for that.
        """
        self.dmin = self.dmax = self.min_display_diameter 

        for wid in self.wids:
            dmin = dmax = self.min_display_diameter 
            dz = self.dz_openhole
            if wid in dz:
                if dz[wid].d:
                    diameter = dz[wid].d
                    dz[wid].d = max(diameter, self.min_display_diameter)
                    dmin = min(dmin, diameter)
                    dmax = max(dmax, diameter)
                else:
                    dz[wid].d = self.min_display_diameter
            
            for dlz in (self.dlz_casing2,
                       self.dlz_screen,
                       self.dlz_hole,
                       self.dlz_grout):
                for dc in dlz.get(wid, []):
                    if dc.d:
                        diameter = dc.d
                        dc.d = max(diameter, self.min_display_diameter)
                        dmin = min(dmin, diameter)
                        dmax = max(dmax, diameter)
                    else:
                        dc.d = self.min_display_diameter                    
            
            self.d_maxdia[wid] = dmax
            
            self.dmin = min(self.dmin, dmin)
            self.dmax = max(self.dmax, dmax)
        
        self.dlims = [self.dmin, self.dmax]
    
        
    def ensure_points_have_spread(self, xspace=10):
        """ 
        Ensure that all coordinates are not on the same coordinate
        
        Arguments
        ---------
        xspace : numeric
            
            -   Nominal horizontal distance for separating points that are
                on top of each other. 
        
        Assumptions
        -----------
        o   self.wids and self.d_xy have been thinned to include only wells that 
            will be drawn.
            
        Notes
        -----
        o   No action is required for a singleton.
        
        o   No action is required if at least two wells have different 
            coordinates.
        
        o   If all of the selected wells are on the same coordinate, then the 
            section line will have zero length. Other parts of the code might 
            become confused by that.  Therefore in that case, we simply sort the 
            wells out alphabetically, and space them apart arbitrarily from 
            west to east, centered on the given coordinate.  The spacing 
            distance is set by xspace, but any non-zero number should
            work alright.            
        """
        if len(self.wids) <= 1: 
            return 
        xyset = set(self.d_xy.values())   
        if len(xyset) > 1:
            return 
        # If we get here, then d_xy has more than one entry, but all (x,y) 
        # coordinate pairs are identical, and we will modify them.
        N = len(self.d_xy)
        Lx = (N+1) * xspace
        x, y = xyset.pop()
        x -= Lx/2   
        for wid in sorted(self.wids):
            self.d_xy[wid] = Coord(x, y)
            x += xspace
            

class dummy(xsec_data_abc):
    def __init__(self):
        super().__init__()
    def read_database(self):
        pass
    def remove_wid_if_missing_required_components(self):
        pass
    
class Test(unittest.TestCase):    
    def test_ensure_points_have_spread(self):
        xsec_data = dummy()
        xsec_data.d_xy = {1 :Coord(225,300),
                          2 :Coord(225,300),
                          3 :Coord(225,300)}
        xsec_data.wids = list(xsec_data.d_xy.keys())
        xspace = 5
        xsec_data.ensure_points_have_spread(xspace=xspace)
        d = xsec_data.d_xy
        self.assertAlmostEqual(d[1].x + xspace, d[2].x, 6)
        self.assertAlmostEqual(d[2].x + xspace, d[3].x, 6)
        self.assertAlmostEqual(d[1].y, d[2].y, 6)
        self.assertAlmostEqual(d[2].y, d[3].y, 6)
 

if __name__ == "__main__":  
    unittest.main()   
                
