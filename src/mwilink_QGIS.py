'''
Created on Oct 25, 2022

@author: William Olsen

Demonstrate opening MWI well log page or well index page in your default browser
from a tab separated list of wellids.  
This can be called from another Python script, for example in a GIS application.
'''

from qgis.utils  import iface
from qgis.PyQt.QtCore import QVariant
import os
import webbrowser
import time, pyautogui

# Get the list of selected wellids from the selected wells layer
flayer = iface.activeLayer()
print (flayer)
for f in flayer.selectedFeatures():
    print (f['wellid'])
wellids = '\t'.join([str(f['wellid']) for f in flayer.selectedFeatures()])
assert len(wellids) > 0

# Timing delays permit opening multiple logs in different browser windows.  
# Setting the correct delays is by trial and error.
opendelay = 1.0
closedelay = 0.25

for wellid in wellids.split('\t'):
    """
    The url is hard coded here.  Two options are shown.  It is best to start out
    using the 'index' url because that one provides access to all of the others,
    of which only the 'welllog' is provided below.
    """ 
    url = f"https://mnwellindex.web.health.state.mn.us/mwi/index.xhtml?wellId={wellid}"
    #url = f"https://mnwellindex.web.health.state.mn.us/mwi/welllog.xhtml?wellId={wellid}"
    
    print (url)
    webbrowser.open_new_tab(url)
    time.sleep(opendelay)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(closedelay)
    pyautogui.hotkey('ctrl', 'w')
    pyautogui.hotkey('alt', 'tab')
    print(f"tab closed {wellid}")