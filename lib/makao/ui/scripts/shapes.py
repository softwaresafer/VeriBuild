# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is MAKAO.
#
# The Initial Developer of the Original Code is
# Bram Adams (bramATcsDOTqueensuDOTca).
# Portions created by the Initial Developer are Copyright (C) 2006-2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# ***** END LICENSE BLOCK *****

from java.awt.geom import GeneralPath
from java.awt import Polygon
import jarray
 
xpoints = jarray.array((10,5,0,5),'i')
ypoints = jarray.array((5,10,5,0),'i')
diamond = Polygon(xpoints,ypoints,4);
shapeDB.addShape(104,diamond)
 
#xpoints = jarray.array((55, 67, 109, 73, 83, 55, 27, 37, 1, 43),'i')
xpoints = jarray.array((110, 134, 218, 146, 166, 110, 54, 74, 2, 86),'i')
#ypoints = jarray.array((0, 36, 36, 54, 96, 72, 96, 54, 36, 36),'i')
ypoints = jarray.array((0, 72, 72, 108, 192, 144, 192, 108, 72, 72),'i')
star = Polygon(xpoints,ypoints,10)
shapeDB.addShape(105,star)
 
triangle = GeneralPath()
triangle.moveTo(10,0)
triangle.lineTo(20,10)
triangle.lineTo(0,10)
triangle.lineTo(10,0)
shapeDB.addShape(106,triangle)

xpoints = jarray.array((6,3,0,0,3,6,9,9),'i')
ypoints = jarray.array((9,9,6,3,0,0,3,6),'i')
hexagon = Polygon(xpoints,ypoints,8);
shapeDB.addShape(107,hexagon)
