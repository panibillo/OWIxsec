'''
Created on Jan 9, 2021

@author: Bill Olsen

Read a legend file into legend objects for cross section.

Methods
-------
xsec_legends
map_legends

Notes
-----
o   This implementation demonstrates hardcoding legends and reading legends from
    an sqlite database.  

o   Each method returns a dictionary with different legends for each of the
    drawing components in the cross section figure or the map view figure.
    
o   The legend properties need to correspond both to the drawing components, the
    properties present in the data, and the requirements of the drawing module.
    
o   The current implementation corresponds to drawing components findable in the
    CWI database (version c4/c5), plus the Perforations table available in the 
    Dakota County wellwater database.  The legend attributes are appropriate
    for drawing in Python's matplotlib module
'''
import os
import sqlite3 as sqlite
import unittest

# set the full pathname for the legend database
LEGEND_DB = os.path.abspath(__file__).replace('src/xsec_legend.py','demo_data/xsec_legend.sqlite')  
                        



def stratlegend(cur):
    ''' Read legend dict for strat layter 
    
    Attributes 
    ----------
    key : string
        CWI 4 character strat code
    
    value : polygonlegend
    '''
    fields = """code 
           label fillcolor 
           patterncolor pattern 
           linecolor linethick linestyle""".split()
    s = f"select {', '.join(fields)} from STRAT_polygon;"
    d = {}
    for row in cur.execute(s).fetchall():
        d[row[0]] = {k:v for k,v in zip(fields, row)}
    return d

def aquiferlegend(cur):
    ''' Read legend dict for strat layter 
    
    Attributes 
    ----------
    key : string
        CWI 4 character aquifer code
    
    value : polygonlegend
    '''
    fields = """code 
           label fillcolor 
           patterncolor pattern 
           linecolor linethick linestyle""".split()
    s = f"select {', '.join(fields)} from STRAT_polygon;"
    d = {}
    for row in cur.execute(s).fetchall():
        d[row[0]] = {k:v for k,v in zip(fields, row)}
        d[row[0]]['linecolor'] = 'red'
        d[row[0]]['linethick'] = 0.75
    return d

def casinglegend(cur):
    fields = """fillcolor patterncolor pattern 
                linecolor linethick linestyle""".split()
    s = f"select {', '.join(fields)} from MISC_polygon where layer = 'CASING';"
    d = {}
    vals = cur.execute(s).fetchall()[0]
    d = {k:v for k,v in zip(fields, vals)}
    return d

def screenlegend(cur):
    fields = 'linecolor linethick linestyle'.split()
    s = f"select {', '.join(fields)} from MISC_polyline where layer = 'screen';"
    data = cur.execute(s).fetchall()
    if data:
        d = {k:v for k,v in zip(fields, data[0])}
    return d
    
def swllegend(cur):
    """ 
    Example of a hardcoded legend, does not use the legend database.
    """
    d = {'linecolor' : '#0505ff',
         'linethick' : 2,
         'linestyle': '-'}
    return d

def bdrklegend(cur):
    fields = 'linecolor linethick linestyle'.split()
    s = f"select {', '.join(fields)} from MISC_polyline where layer = 'bdrk';"
    data = cur.execute(s).fetchall()
    if data:
        d = {k:v for k,v in zip(fields, data[0])}
    return d

def perflegend(cur):
    fields = """fillcolor patterncolor pattern 
                linecolor linethick linestyle""".split()
    s = f"select {', '.join(fields)} from MISC_polygon where layer = 'PERF';"
    d = {}
    vals = cur.execute(s).fetchall()[0]
    d = {k:v for k,v in zip(fields, vals)}
    return d

def hfraclegend(cur):
    fields = """fillcolor patterncolor pattern 
                linecolor linethick linestyle""".split()
    s = f"select {', '.join(fields)} from MISC_polygon where layer = 'HFRAC';"
    d = {}
    vals = cur.execute(s).fetchall()[0]
    d = {k:v for k,v in zip(fields, vals)}
    return d
        
def groutlegend(cur):
    fields = """code 
           label fillcolor 
           patterncolor pattern 
           linecolor linethick linestyle""".split()
    s = f"select {', '.join(fields)} from GROUT_polygon;"
    d = {}
    for row in cur.execute(s).fetchall():
        d[row[0]] = {k:v for k,v in zip(fields, row)}
    return d

def droppipelegend(cur):
    d = {'droppipe': {'linecolor' : '#000000',
                      'linethick' : 1,
                      'linestyle': '-'},
         'pump'    : {'marker'   : '>',
                      'color': '#ff0000'}
        }
    return d

def gridlegend(cur, gridpart):
    """ Return grid line definitions. 
    
        This implementation ignores cur and just hard codes the defs here.
    """
    if gridpart == 'gridmajor':
        d = {'linecolor' : '#f5a142',
             'linethick' : 1.5,
             'linestyle': '-'}
    else:
        d = {'linecolor' : '#f5b942',
             'linethick' : 0.75,
             'linestyle': '-'}
    return d    

def check_legend_path():
    assert os.path.exists(LEGEND_DB), f"not found: {LEGEND_DB}"
    return LEGEND_DB

def xsec_legends():
    """
    Initialize the dictionary of legend definitions from the legend database.
    """ 
    con = sqlite.connect(LEGEND_DB)
    cur = con.cursor()
    d = {}
    d['stratlegend']    = stratlegend(cur)
    d['caselegend']     = casinglegend(cur)
    d['screenlegend']   = screenlegend(cur)
    d['swllegend']      = swllegend(cur)
    d['bdrklegend']     = bdrklegend(cur)
    d['aquiferlegend']  = aquiferlegend(cur)
    d['perflegend']     = perflegend(cur)
    d['hfraclegend']    = hfraclegend(cur)
    d['droppipelegend'] = droppipelegend(cur)
    d['groutlegend']    = groutlegend(cur)
    d['gridmajor']      = gridlegend(cur,'gridmajor')
    d['gridminor']      = gridlegend(cur,'gridminor')
    cur.close()
    con.close()
    return d     
        
def map_legends():
    d = {'xsecline':{'linecolor' : '#0505ff',
                     'linethick' : 2,
                     'linestyle': '-'},
         'normals': {'linecolor' : '#0505ff',
                     'linethick' : 1,
                     'linestyle': '-'},
         'points':  {'color' : '#0909ff',
                     'marker' : 'o'}
        }  
    return d
          
class Test(unittest.TestCase):
    def test_xsec_legends(self):
        dbname = r'F:\Bill\Workspaces\Py1\CrossSection\src\xsec_legend.sqlite'
        d = xsec_legends(dbname)
        import pprint 
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(d)

if __name__ == "__main__":
    unittest.main()