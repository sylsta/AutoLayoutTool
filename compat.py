# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoLayoutTool
                                 A QGIS plugin
 Compatibility constants: PyQt5 / PyQt6 (QGIS 3 / QGIS 4) and old / new QGIS enums.

 PyQt6 only accepts scoped enums (Qt.AlignmentFlag.AlignCenter), PyQt5 also
 accepts (and older versions only accept) unscoped ones (Qt.AlignCenter).
 QGIS 3.30 moved many enums to the Qgis class (Qgis.LayoutUnit...), and
 QGIS 4 removed the old ones. Each constant is resolved once here, so the
 rest of the plugin has a single code path.
                             -------------------
        copyright            : (c) 2021-2026 by Sylvain Théry
        email                : sylvain.thery@cnrs.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QMovie
from qgis.PyQt.QtWidgets import QMessageBox, QDialogButtonBox, QSizePolicy
from qgis import core as qgis_core  # old classes accessed through the module: they may not exist in QGIS 4
from qgis.core import Qgis, QgsLayoutItem


def _first(*getters):
    """
    Return the value of the first getter that does not raise AttributeError
    (new / scoped name first, then old / unscoped name)
    """
    for getter in getters:
        try:
            return getter()
        except AttributeError:
            continue
    raise AttributeError('No compatible value found')


# --- Qt (PyQt6 scoped enums first, then PyQt5)

# Window modality
APPLICATION_MODAL = _first(lambda: Qt.WindowModality.ApplicationModal, lambda: Qt.ApplicationModal)

# Alignment, item flags, check states, roles, match flags
ALIGN_CENTER = _first(lambda: Qt.AlignmentFlag.AlignCenter, lambda: Qt.AlignCenter)
CHECKED = _first(lambda: Qt.CheckState.Checked, lambda: Qt.Checked)
UNCHECKED = _first(lambda: Qt.CheckState.Unchecked, lambda: Qt.Unchecked)
ITEM_ENABLED = _first(lambda: Qt.ItemFlag.ItemIsEnabled, lambda: Qt.ItemIsEnabled)
ITEM_USER_CHECKABLE = _first(lambda: Qt.ItemFlag.ItemIsUserCheckable, lambda: Qt.ItemIsUserCheckable)
ITEM_AUTO_TRISTATE = _first(lambda: Qt.ItemFlag.ItemIsAutoTristate, lambda: Qt.ItemIsAutoTristate)
USER_ROLE = _first(lambda: Qt.ItemDataRole.UserRole, lambda: Qt.UserRole)
MATCH_FIXED_STRING = _first(lambda: Qt.MatchFlag.MatchFixedString, lambda: Qt.MatchFixedString)

# Widgets
SIZE_POLICY_EXPANDING = _first(lambda: QSizePolicy.Policy.Expanding, lambda: QSizePolicy.Expanding)
MOVIE_CACHE_ALL = _first(lambda: QMovie.CacheMode.CacheAll, lambda: QMovie.CacheAll)

# Dialog buttons
BUTTONBOX_OK = _first(lambda: QDialogButtonBox.StandardButton.Ok, lambda: QDialogButtonBox.Ok)
BUTTONBOX_CANCEL = _first(lambda: QDialogButtonBox.StandardButton.Cancel, lambda: QDialogButtonBox.Cancel)
BUTTONBOX_CLOSE = _first(lambda: QDialogButtonBox.StandardButton.Close, lambda: QDialogButtonBox.Close)

# Message boxes
MSGBOX_ROLE_DESTRUCTIVE = _first(lambda: QMessageBox.ButtonRole.DestructiveRole, lambda: QMessageBox.DestructiveRole)
MSGBOX_ROLE_ACCEPT = _first(lambda: QMessageBox.ButtonRole.AcceptRole, lambda: QMessageBox.AcceptRole)
MSGBOX_CANCEL = _first(lambda: QMessageBox.StandardButton.Cancel, lambda: QMessageBox.Cancel)

# --- QGIS (Qgis.* enums since QGIS 3.30, required for QGIS 4; QgsUnitTypes / QgsWkbTypes before)

LAYOUT_MM = _first(lambda: Qgis.LayoutUnit.Millimeters, lambda: qgis_core.QgsUnitTypes.LayoutMillimeters)
DISTANCE_M = _first(lambda: Qgis.DistanceUnit.Meters, lambda: qgis_core.QgsUnitTypes.DistanceMeters)
POLYGON_GEOMETRY = _first(lambda: Qgis.GeometryType.Polygon, lambda: qgis_core.QgsWkbTypes.PolygonGeometry)

# Layout item reference points (used to anchor the legend by one of its corners)
REF_UPPER_LEFT = _first(lambda: QgsLayoutItem.ReferencePoint.UpperLeft, lambda: QgsLayoutItem.UpperLeft)
REF_UPPER_RIGHT = _first(lambda: QgsLayoutItem.ReferencePoint.UpperRight, lambda: QgsLayoutItem.UpperRight)
REF_LOWER_LEFT = _first(lambda: QgsLayoutItem.ReferencePoint.LowerLeft, lambda: QgsLayoutItem.LowerLeft)
REF_LOWER_RIGHT = _first(lambda: QgsLayoutItem.ReferencePoint.LowerRight, lambda: QgsLayoutItem.LowerRight)
