# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordConvert
                                 A QGIS plugin
 Converts coordinates between WGS84, GCJ02, and BD09
                              -------------------
        begin                : 2025
        copyright            : (C) 2025
        email                : solidjerryc@gmail.com
 ***************************************************************************/


/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def classFactory(iface):
    """Load CoordConvert class from file CoordConvert.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .coord_convert import CoordConvert
    return CoordConvert(iface)