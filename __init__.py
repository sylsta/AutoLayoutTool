# -*- coding: utf-8 -*-
"""
/***************************************************************************
 createLayout
                                 A QGIS plugin
 Creates a layout with the current map canvas extent
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-11-19
        copyright            : (C) 2021 by Sylvain Théry
        email                : sylvain.thery@cnrs.fr
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load createLayout class from file createLayout.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .create_layout import createLayout
    return createLayout(iface)
