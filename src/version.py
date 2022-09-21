'''
Created on Jun 2, 2021

Well cross section version information

Version 0.1  2021-05-26
    Data dictionaries use simple tuples.
    Demonstration implementation of CWI data source (in SQLite)
    Prototypes of sample and Dakota Co data sources.

Version 0.2  2021-06-02
    Data dictionaries use namedtuple's
    Prototypes of sample and Dakota Co data sources removed as obsolete forms.
    Improvements to documentation
    Misc. bug fixes.
    
Version 0.3  2021-11-09
    Project name change from "Crosssection" to "MNcwixsec", so it will be less 
       harder to pronounce.
    Data dictionaries use Dataclasses (excepth d_xy is still a namedtuple)
    Demo_data files provided.
    Improvements to documentation.
    Cleaner & less buggy algorithm to find best fitted projection line.
    Many bug fixes.
    Re-initialized git repo under the new name, deleting prior version istory.
    
Version 0.4  2022-09-20
    Project name changed again, from "MNcwixsec" to "OWIxsec", reflecting its
    common origin with project OWI.
    Grout interval is given better logic for finding inner and outer diameter
    of grout intervals. Both inner and outer diameters are not given explicitly
    in the OWI database, nor in the Minnesota CWI database that OWI is based on.
    
@author: Bill Olsen
'''

__version__ = 0.3