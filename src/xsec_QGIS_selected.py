#qgis.gui
"""
Demonstration of running the xsec program for wells.

Requirements:
    The MNcwixsec scripts & data resources. 
        Verify that the xsec_demo.py runs.
    This script should be in the same folder.
    An OWI.sqlite database 
        (see https://github.com/panibillo/MNcwi.git)
        Edit variable wells_db below to point to this database,
    A legend database - as used by xsec_demo.py.
    A wells GIS layer.  
        This should be a point theme, for example the wells.shp served by MGS.
        It should have an integer field named 'wellid'.
        The wellid values should match those in the OWI database.
    A sectionline layer.
        This script is expecting a layer named 'xsec_lines' to be loaded
        That theme should have these 3 fields (at least).
            Xid      integer
            Xpart    text
            Xcommand text
    Edit this script so that it passes the desired argument values to xsec_cl.

Running
    Load this script into the QGIS python script window.
    Load the wells layer into the map window.
    Make the wells layer the active layer.
    Select one or more wells.
    Run this script.
    
This script reads the wellid from the active theme, assembles them into a 
command line string, and calls xsec_cl, and then Xsecmain.
Xsec_main draws the cross section on a pop-up matplotlib window, and returns 
the xsec object.
This script gets the cross-section line definitions and uses them to add 
features to the xsec_lines layers.

Not yet implemented:
    There is no way for the user to choose the drawing parameters.
    There is no way for the user to suggest the line orientation. 
"""
from qgis.utils  import iface
from qgis.PyQt.QtCore import QVariant
import os

import xsec_cl
from xsec_main import Xsec_main as Xsecmain
import xsec_legend

# Hard code the wells database name. This will be unique to your system.
homedir = os.path.expanduser("~")
wells_db = os.path.join(homedir, 'data/MN/OWI/OWI40.sqlite')

# Hard code the legend database name. This will be unique to your system.
# Here we use the legend db provided with the demo data.
### scriptdir = os.path.abspath(__file__)
### legend_db = scriptdir.replace('src/xsec_QGIS_selected.py','demo_data/xsec_legend.sqlite')
print (os.path.abspath('.'))
legend_db = None

# Get the list of selected wellids from the seelected wells layer
flayer = iface.activeLayer()
print (flayer)
for f in flayer.selectedFeatures():
    print (f['wellid'])
wellids = ' '.join([str(f['wellid']) for f in flayer.selectedFeatures()])
assert len(wellids) > 0

# Compose the command line, convert it to cmds, and call xsec_Main()
commandline = f"-p -i {wellids}"
print (commandline)
cmds = xsec_cl.xsec_parse_args(commandline)
xsec =  Xsecmain(cmds, db_name = wells_db)

# Add the xsec line feature to the xsec_lines layer
#   xid      : a unique id to the xsec line and it's normals. 
#   xpart    : 'L' for the xsec-line and 'N' for each normal.
#   xcommand : the commandline that was passed to xsec_cl.
try:
    xlayer = QgsProject.instance().mapLayersByName('xsec_lines')[0]
except Exception as e:
    # The default exception is hard to interpret, this seems more informative.
    # The 'from None' at the end removes a confusing exception within an exception.
    # This is the last task, so we can just halt here if needed.
    raise Exception('---WARNING---, layer "xsec_lines" is not found') from None

# Initialize xid
try:
    xid = xlayer.maximumValue(1) + 1
except:
    # An exception will occur if the layer is empty. Assume that is the cause.
    xid = 1

caps = xlayer.dataProvider().capabilities()

if caps & QgsVectorDataProvider.AddFeatures:
    x,y = xsec.sectionline.x, xsec.sectionline.y
    pts = [QgsPoint(u,v) for u,v in zip(x,y)]
    xline = QgsGeometry.fromPolyline(pts)

    feat = QgsFeature(xlayer.fields())
    feat.setGeometry(xline)
    feat.setAttribute('xid', xid)
    feat.setAttribute('xpart','L')
    feat.setAttribute('xcommand',commandline)
    xfeatures = [feat]
    if xsec.normals:
        for n in xsec.normals:
            #print (n)
            x,y = n.x, n.y
            pts = [QgsPoint(u,v) for u,v in zip(x,y)]
            feat = QgsFeature(xlayer.fields())
            feat.setGeometry(QgsGeometry.fromPolyline(pts))
            feat.setAttribute('xid', xid)
            feat.setAttribute('xpart','N')
            xfeatures.append(feat)
        
    (res, outFeats) = xlayer.dataProvider().addFeatures(xfeatures)

    # Update the map view after adding features to the xsec_lines layer.
    xlayer.updateExtents()
    if iface.mapCanvas().isCachingEnabled():
        xlayer.triggerRepaint()
    else:
        iface.mapCanvas().refresh()

#print ('xlayer.isValid() =',xlayer.isValid())
#rint ('xlayer=',str(xlayer))
#print ('prov.fields',prov.fields())
#print ('prov.featureCount',prov.featureCount())

#e = xlayer.extent()
#print ('xlayer.extent', e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())
# 
#for f in xlayer.getFeatures():
#    print("Feature:", f.id(), f.attributes(), f.geometry() )
#
#QgsMapLayerRegistry.instance().addMapLayers([xlayer])

#QgsProject.instance().addMapLayer(xlayer)
#layers_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
#print(f"layers TOC = {layers_names}")
#xsec =  Xsec_main(cmds, db_name="../demo_data/MNcwi_demo.sqlite")



