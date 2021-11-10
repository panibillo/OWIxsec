"""
Data module for a well cross section drawing tool for well construction 
and stratigraphic layers

Classes
-------
xsec_data_MNcwi
 

Notes
-----
o   A data module that gathers the information requested by the section_line 
        module. 

    -   The xsec_data class must inherit the abstract base class xsec_data_abc.
    
    -   The abstract base class xsec_data_abc defines the methods that the 
        xsec_data module must support.
     
o   Outline of data reading process:
    
    -   The data module is given an unordered, unverified list of well 
        identifiers.   
        
    -   The data module populates the data dictionaries required in xsec_main. 
        +   The dictionaries are listed and described in xsec_data_abc.
        +   The dictionary keys are the CWI wellid (numeric values)
    
"""     
#import abc
from collections import defaultdict

from cwi_db import c4db
from xsec_data_abc import * # xsec_data_abc, isnum
import logging
logger = logging.getLogger('xsec_data_MNcwi')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.INFO)

class  xsec_data_MNcwi(xsec_data_abc):  
    """
    Attributes
    ----------
    All attributes are defined and self-described in module xsec_data_abc. This
    module is responsible for implementing all attributes available in the CWI
    database and needed by the xsec_main module.
             
    Notes
    -----
    o   The data module is responsible for converting depths to elevations.  To
        do that it gets the elevation at the well from table c4ix or c4locs
         
    o   This module knows only world coordinates and world dimensions.
        It does not convert anything to output window coordinates or dimensions.
    """

    def __init__(self, default_display_diameter=4, min_display_diameter=1):
        super().__init__()
        self.default_display_diameter = default_display_diameter
        self.min_display_diameter = min_display_diameter
        pass

    def read_database(self, identifiers, db_name=None):
        """ 
        Read the well data from the databases
        
        Arguments
        ---------
        cmds.identifiers : list of strings.  The list of Unique Well Numbers.
           
        Returns
        -------
        True / False
       
        Notes:
        ------
        o   When reading the data, ording of wellist does not matter.
                                      
        o   Fill or nullify each of the attributes required by the 
            Abstract Base Class.  Data are stored in three different units:
            
            -   Vertical dimensions are stored as depths, lengths, and 
                elevations.  The elevations are computed using the land
                elevation at the well as stored in c4locs (or c4ix if missing 
                from c4locs).  In CWI these are all in units of feet.  
                
            -   Locations (x,y) are in world coordinates.  In CWI these are in
                units of meters (coming from UTM coordinates)
            
            -   Well diameters in CWI are in units of inches
    
        o   Data is read from several tables. Merging of data from the different 
            tables is attempted in order to reduce the chance of having an
            incomplete record.  When sources are in conflict.  Note that 
            different data sources may be preferred for differnt data components.  
            That logic can be split between this module and the individual 
            component drawing methods in xsec_main. 

        o   Order of computation matters because some calculations are 
            dependent on others.  In particular get the elevation, total depths, 
            diameters early.
            
        o   Data is stored in data dictionaries described in xsec_data_abc.
            Some dictionaries use namedtuples.  When creating a named tuple, you
            must pass a value for each field, and in order.  The namedtuples are
            also defined in xsec_data_abc.
            
        o   In addition to filling the drawing element dictionaries, also return
            the domain limits:  min and max elevations, and min and max 
            diameters from among all elements of all wells.
            
        o   Data peculiarities in cwi data as served on MGS website
        
            -   Missing text or numeric data in .csv files may be entered with 
                nothing between commas at that position, or possibly as empty
                quotes.  In some cases CWI enters '0' for numeric values not 
                entered in original data sources, and in other cases it enters
                null or missing values.  Missing values and empty quotes are 
                imported as Null, but 0 values are imported as 0's, even when 
                that seems to signify missing data, for example: Casing depth=0. 
            
            -   The shape files have some data mis-matches with the .csv files.
                These can include missing values and missing records. 
        
            -   Some wells do not have elevations in c4locs or c4ix.
                (The elevation is probably entered as '0' in c4locs)
            
                +   Singletons are handeled easily: just set z=0 at the land 
                    surface.
                    
                +   If all wells are missing elevation, then draw them all with
                    z=0 at the surface. They will be mis-alligned vertically if
                    if they do not have the same land elevations in fact.
                
                +   If some wells have elevations and some do not, then look at 
                    the command line setting "-R E", meaning 'Requires Elevation'.
                    If 'Requires Elevation' is True, then exclude all wells that
                    lack elevations. (This should be the default behavior)
                    If 'Requires Elevation' is False, then draw all wells as if 
                    none of them have elevations. 
                
                +   Because Elevation is used throughout the data ingest steps, 
                    it is essential to evaluate the elevations right away. It can not
                    only remove wells from the include list, but also change a
                    multi-well line to a singleton. 
        """
        # Database connection
        c4 = c4db(open_db=True, commit=False, db_name=db_name) 
        query = c4.cur.execute
        self.datasource = c4.db_name
        logger.info(f"read_database {self.datasource}")

        ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
        """ 
        We first require a list of unique wellid values using the list of 
        Unique Well Numbers supplied by the user.  These are searched for in 
        c4-tables in 2 steps: first searching 3 fields in c4ix, and then
        searching the identifiers field in c4id. When an identifier is found,
        its wellid is added to the set wids, and the identifier is added to the
        dictionary self.d_label. self.d_iwid is the inverse of self.d_label; its
        only use is to enumerate identifiers that are not found at all.
        
        ! Assumes that text searches in CWI are not case sensitive !
        """
        identifiers = self.identifiers = tuple(identifiers)
        qmarks = c4.qmarks(identifiers)
          
        s1 = """select wellid, %s from c4ix where %s in (%s);"""

        wids = set()
        for col in 'UNIQUE_NO RELATEID'.split():
            data1 = query(s1%(col, col, qmarks), identifiers).fetchall()
            for wid, wname in data1:
                if wid in wids: 
                    # The columns are in order of decreasing preference, if an
                    # identifier is already found, then discontinue this column
                    continue
                wids.add(wid) 
                self.d_label[wid] = wname
                self.d_iwid[wname] = wid
            if len(wids) == len(self.identifiers):
                break
        
        if len(wids) < len(self.identifiers):
            s2 = f"""select wellid, cast(wellid as text) from c4locs 
                     where relateid in ({qmarks});"""
            relateids = tuple((f"000000{v}"[-10:] for v in identifiers))
            data2 = query(s2, relateids).fetchall()
            for wid, wname in data2:
                if wid in wids: continue
                wids.add(wid) 
                self.d_label[wid] = wname
                self.d_iwid[wname] = wid
        
        
        if len(wids) < len(self.identifiers):
            s1 = f"""select wellid, identifier from c4id 
                     where identifier in ({qmarks});"""
            for wid, wname in data1:
                if wid in wids: continue
                wids.add(wid) 
                self.d_label[wid] = wname
                self.d_iwid[wname] = wid
        
        wids = list(wids)   
        
        # Ensure that every wid has a label
        for wid in wids:
            if not wid in self.d_label:
                self.d_label[wid] = f"wellid {wid}"         
        
        # Document identifiers that have not been found.
        self.missing_identifiers = list()
        if len(wids) < len(self.identifiers):
            for identifier in self.identifiers:
                if not identifier in self.d_iwid:
                    self.missing_identifiers.append(identifier)

        # Document identifiers that have been found in duplicate.
        self.duplicate_wids = list()
        if len(wids) > len(self.identifiers):
            w = set()
            for wname, wid in self.d_label.items():
                if wid in w:
                    self.duplicate_wids.append(wid)
                w.add(wid)

        logger.debug (f"identifiers = {identifiers}")
        logger.debug (f"wids = {wids}")
        if self.missing_identifiers:
            logger.warning (f"missing_identifiers = {self.missing_identifiers}")
        if self.duplicate_wids:
            logger.warning (f"duplicate_wids = {self.duplicate_wids}")
        
                
        ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
        # Compose the common selection criteria on wids.
        # Compose the database queries as simple queries without joins that 
        # store results as namedtuples.  Joining or sorting out information from 
        # multiple tables into the value dictionaries and component dictionaries
        # is done in Python code on the namedtuple's.  
        # !!! The namedtuple field names are strictly lower case!!!  
 
        dat = {}
        qmarks = c4.qmarks(wids)
        where = f"where wellid in ({qmarks})"
        for tbl,flds in {
            'c4ix'  :"""wellid  unique_no  elevation  case_diam  aquifer  
                        case_depth  depth_comp  depth_drll  depth2bdrk""",  
            'c4locs':"""wellid  elevation  case_diam  aquifer   
                        case_depth  depth_comp  depth_drll  
                        depth2bdrk  swlcount  swlavgmeas  utme  utmn""",  
            'c4c1'  :"""wellid  ohtopfeet  ohbotfeet    
                        dropp_len  hydrofrac  hffrom  hfto""",
            'c4c2'  :"""wellid  constype  diameter  from_depth  to_depth
                        slot  length  material  amount  units""",
            'c4st'  :"""wellid  depth_top  depth_bot 
                        drllr_desc  color  hardness  strat  
                        lith_prim  lith_sec  lith_minor"""            
            }.items():
            flds = flds.split()
            sql = f"select {', '.join(flds)} from {tbl} {where};"   
            ntup = namedtuple(tbl, flds) 
            dat[tbl] = [ntup(*row) for row in query(sql, wids).fetchall()]   

        #debugging
        logger.debug (', '.join((f"{tbl}:{len(dat[tbl])}" for tbl in dat.keys()))) 
        if 0:
            print ('dat.values():  DEBUG265')
            spacer = '\n         '
            for tbl,items in dat.items():
                print (f"{tbl:6} - ", end='')
                print (f"{spacer.join((str(i) for i in items))}")
        

        ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
        # Table c4ix and c4locs 
        #   
        # c4locs is a union of shape file tables wells.dbf and unlocwells.dbf.
        #
        # Note that several fields have data shared between c4ix and c4locs, so
        # that both tables must be queried to obtain a full data set.  In cases
        # that data is present in both tables and is unequal, we currently 
        # assume that c4locs is more reliable.
        # Having an xy coordinate could be required at this point, but is not.
        for row in dat['c4ix']:
            i,z,d,a = row.wellid, row.elevation, row.case_diam, row.aquifer
            if not i in wids: 
                continue
            
            if i and z and z>500:
                self.dz_grade[i] = z

            if i and d and d > 0.001:
                self.d_diameter[i] = max(d, self.min_display_diameter)

            if i and a:
                self.d_aquifer[i] = a
        
        logger.debug (f"A {len(self.dz_grade)}, {len(self.d_diameter)}, {len(self.d_aquifer)}" )     
        for row in dat['c4locs']:
            i,z,d,a = row.wellid, row.elevation, row.case_diam, row.aquifer
            x,y = row.utme, row.utmn
            if not i in wids: 
                continue

            if i and x and y:
                self.d_xy[i] = Coord(x,y)
            
            if i and z and z>500:
                self.dz_grade[i] = z
           
            #TODO: move max() func to update_diameters() ??
            if i and d and d > 0.001:
                self.d_diameter[i] = max(d, self.min_display_diameter)
            
            if i and a:
                self.d_aquifer[i] = a

        logger.debug (f"B {len(self.dz_grade)}, {len(self.d_diameter)}, {len(self.d_aquifer)}")      
        
        # local shorthand dicts, D and Z
        D = dict(self.d_diameter)        
#         Z = dict(self.dz_grade)
        
        #logger.debug (f"C {self.dmin}, {self.dmax}")     
        
        for row in dat['c4ix']:
            i,c,b = row.wellid, row.case_depth, row.depth2bdrk 
            p,d   = row.depth_comp, row.depth_drll 
            logger.debug (f"D {row}")
            if not i in wids: 
                continue

            if isnum(c) and c>0:   #CASE_DEPTH
                self.dz_casing[i] =  c
            
            if isnum(p) and p>0:   #DEPTH_COMP
                self.dz_bot[i] = p
            
            elif isnum(d) and d>0: # DEPTH_DRLL
                self.dz_bot[i] = d 

            if isnum(b):   # DEPTH2BDRK
                self.dz_bdrk[i] = b                        
        
        logger.debug (f"E {len(self.dz_casing)}, {len(self.dz_bot)}, {len(self.dz_bdrk)}")     

        for row in dat['c4locs']:
            i,c,b = row.wellid, row.case_depth, row.depth2bdrk 
            p,d   = row.depth_comp, row.depth_drll 
            n,s   = row.swlcount, row.swlavgmeas
            
            if not i in wids: 
                continue

            if c and c> 0:    # CASE_DEPTH              
                self.dz_casing[i] = c  

            if p and p> 0:    # DEPTH_COMP           
                self.dz_bot[i] = p     
            elif d and d>0:   # DEPTH_DRLL 
                self.dz_bot[i] = d
            
            if b and b>0:     # DEPTH2BDRK
                self.dz_bdrk[i] = b
            
            if isnum(n) and n>0 and isnum(s):      # SWLAVGELEV
                self.dz_swl[i] = s  
            
        logger.debug (f"F {len(self.dz_casing)}, {len(self.dz_bot)}, {len(self.dz_bdrk)}, {len(self.dz_swl)}")      

        ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
        # Table c4c1:
        # wellid, ohtopfeet, ohbotfeet, dropp_len, hydrofrac,  hffrom,  hfto  
        for row in dat['c4c1']:
            i, t,b  = row.wellid, row.ohtopfeet, row.ohbotfeet   
            p, h,ht,hb = row.dropp_len, row.hydrofrac, row.hffrom, row.hfto
            
#             if not i in Z: continue
            d = D.get(i,None)
            #d2 = self.d_maxdia[i]
            label = self.d_label[wid]
            
            if t and b and t>=0 and b>0:
                self.dz_openhole[i] = Openhole(wid, label, d, t, b, 
                                               None, None, b-t)

            if p and p>0:
                self.dz_droppipe[i] = Droppipe(wid, label, None, 0, p, None, None, p)

            if h and ht and hb and h=='Y' and ht>=0 and hb>0:
                self.dz_hydrofrac[i] = Hydrofrac(wid, label, ht, hb, 
                                                None, None, hb-ht)

        logger.debug (f"G {len(self.dz_openhole)}, {len(self.dz_droppipe)}, {len(self.dz_hydrofrac)}")      

        ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
        # Table c5c2: 
        # CONSTYPE: C:casing, G:grout, H-drillhole, S-screen
        # One well can have multiple entries for any CONSTYPE.
        # Attributes read differ by CONSTYPE, and may be blank:
        #    hole:   (diameter, top, bottom) *
        #    casing: (diameter, top, bottom)
        #    grout:  (diameter, top, bottom, material, amount, units) **
        #    screen: (diamter, top, bottom, slot, length)
        #
        for row in dat['c4c2']:
            i,constype, d = row.wellid, row.constype, row.diameter
            t,b, s,l  = row.from_depth, row.to_depth, row.slot, row.length
            m,a,u     = row.material, row.amount, row.units
#             if not i in Z: continue
            label = self.d_label[i]

            # Casing: If From_depth missing, assume it is at grade
            if constype=='C' and isnum(b): 
                if t is None: t = 0
                if b>t:
                    self.dlz_casing2[i].append(Casing(i,label, d, t, b, 
                                                      None, None, b-t))

            # Screen: If From_ depth missing, do not read 
            elif constype=='S' and isnum(t) and b and b>t:
                self.dlz_screen[i].append(Screen(i,label, d, t, b, 
                                                 None, None, l, m, s))
            
            # Grout: If From_depth missing, assume it is at grade
            elif constype=='G' and isnum(b):
                if t is None: t = 0
                if b>t:
                    self.dlz_grout[i].append(Grout(i,label, d, t, b, 
                                                   None, None, b-t, m, a, u ))
            
            # Hole: If From_depth is missing, assume it is at grade
            elif constype=='H' and isnum(b):
                if t is None: t = 0
                if b>t:
                    self.dlz_hole[i].append( Hole(i,label, d, t, b, 
                                                  None, None, b-t))

        logger.debug (f"H {len(self.dlz_casing2)}, {len(self.dlz_screen)}, {len(self.dlz_grout)}, {len(self.dlz_hole)}")      

        ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
        # Table c5st
        # One well can have multiple strat layers.
        for row in dat['c4st']:
            i, t,b  = row.wellid, row.depth_top, row.depth_bot 
            r,c,h,s = row.drllr_desc, row.color, row.hardness, row.strat  
            l1,l2,lm = row.lith_prim, row.lith_sec, row.lith_minor
            
            if isnum(t) and isnum(b) and (b>t) and s:
                label = self.d_label[i]
                self.dlz_strat[i].append(
                    Strat(i, label, t, b, None, None, b-t,
                          r, c, h, s, l1, l2, lm))
                logger.debug (f"I {row}, z={z}")

        logger.debug (f"J {len(self.dlz_strat)}")      
                   
        c4.close_db()    
        self.wids = tuple(wids)
        return (len(self.d_xy) > 0)

    
if __name__=='__main__':
    from xsec_cl import xsec_parse_args
    
    if 1:
        D = xsec_data_MNcwi()
        muns = '0000195748 0000200828 0000200830 0000233511 524756 0000200852 0000207269 0000509077'
        muns = '0000200852 0000207269' 
        muns = '200852'
        commandline =  f"-i {muns}"
        cmds = xsec_parse_args(commandline.split())
        D.read_database(cmds)
    print (D)

    print (r'\\\\\\\\\\ DONE - data cwi /////////////')


