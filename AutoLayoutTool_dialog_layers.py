# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoLayoutTool
                                 A QGIS plugin
 Dialog to choose the layers whose extent is used to create a layout
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

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
                                 QSpinBox, QDialogButtonBox, QPushButton)
from qgis.core import QgsProject, QgsLayerTree, QgsSettings, QgsApplication

from .compat import (CHECKED, UNCHECKED, ITEM_USER_CHECKABLE, ITEM_AUTO_TRISTATE, ITEM_ENABLED, USER_ROLE,
                     BUTTONBOX_OK as BTN_OK, BUTTONBOX_CANCEL as BTN_CANCEL)

BUFFER_SETTINGS_KEY = 'AutoLayoutTool/LAYERS_DIALOG/buffer_percent'
DEFAULT_BUFFER_PERCENT = 5


def layer_has_extent(layer):
    """
    :return: True if the layer can be used to compute an extent
    """
    return (layer is not None and layer.isValid() and layer.isSpatial()
            and not layer.extent().isNull())


# Data providers of online services and tiles (WMS / WMTS / XYZ tiles all use the 'wms' provider)
ONLINE_PROVIDERS = {'wms', 'arcgismapserver', 'arcgisfeatureserver', 'wcs', 'wfs', 'oapif',
                    'xyzvectortiles', 'arcgisvectortileservice', 'mbtilesvectortiles', 'vtpkvectortiles'}


def is_online_or_tiles(layer):
    """
    :return: True for online services and tiled layers (basemaps), which usually cover a much larger area
             than the data and should not drive the layout extent by default
    """
    try:
        if layer.providerType() in ONLINE_PROVIDERS:
            return True
    except AttributeError:
        pass
    try:
        from qgis.core import QgsVectorTileLayer  # QGIS >= 3.14
        return isinstance(layer, QgsVectorTileLayer)
    except ImportError:
        return False


def layer_icon(layer):
    """
    Icon of a layer, as in the QGIS Layers panel (QgsIconUtils exists since QGIS 3.20)
    """
    try:
        from qgis.core import QgsIconUtils
        return QgsIconUtils.iconForLayer(layer)
    except (ImportError, AttributeError):
        return QgsApplication.getThemeIcon('/mIconLayer.png')


class AutoLayoutToolDialogLayers(QDialog):
    """
    Shows the project layer tree (groups and spatial layers) with checkboxes, and a buffer percentage.
    Checked layers are only used to compute the layout extent.
    Visible layers are pre-checked, except online services and tiles (basemaps).
    """

    def __init__(self, parent=None):
        super(AutoLayoutToolDialogLayers, self).__init__(parent)
        self.setWindowTitle(self.tr(u'Create a layout from layers extent'))
        self.resize(420, 520)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel(self.tr(u'Layers used to compute the layout extent:')))

        # Layer tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        main_layout.addWidget(self.tree)
        root = QgsProject.instance().layerTreeRoot()
        self._fill_tree(self.tree.invisibleRootItem(), root)
        self.tree.expandAll()

        # Check / uncheck all
        buttons_row = QHBoxLayout()
        self.pb_check_all = QPushButton(self.tr(u'Check all'))
        self.pb_uncheck_all = QPushButton(self.tr(u'Uncheck all'))
        self.pb_check_all.clicked.connect(lambda: self._set_all(CHECKED))
        self.pb_uncheck_all.clicked.connect(lambda: self._set_all(UNCHECKED))
        buttons_row.addWidget(self.pb_check_all)
        buttons_row.addWidget(self.pb_uncheck_all)
        buttons_row.addStretch()
        main_layout.addLayout(buttons_row)

        # Buffer
        buffer_row = QHBoxLayout()
        buffer_row.addWidget(QLabel(self.tr(u'Buffer (% on each side):')))
        self.sb_buffer = QSpinBox()
        self.sb_buffer.setRange(0, 50)
        self.sb_buffer.setSingleStep(1)
        self.sb_buffer.setSuffix(' %')
        self.sb_buffer.setToolTip(self.tr(u'Space added around the layers extent, as a percentage of its width '
                                          u'and height, on each side'))
        self.sb_buffer.setValue(self._load_buffer())
        buffer_row.addWidget(self.sb_buffer)
        buffer_row.addStretch()
        main_layout.addLayout(buffer_row)

        # OK / Cancel
        self.button_box = QDialogButtonBox(BTN_OK | BTN_CANCEL)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.tree.itemChanged.connect(self._update_ok_button)
        self._update_ok_button()

    def _fill_tree(self, parent_item, group):
        """
        Recursively add groups and layers of the project layer tree.
        Non spatial layers (tables) are not listed; layers without extent are shown disabled.
        :return: number of layer items added under parent_item
        """
        count = 0
        for node in group.children():
            if QgsLayerTree.isGroup(node):
                item = QTreeWidgetItem([node.name()])
                item.setIcon(0, QgsApplication.getThemeIcon('/mActionFolder.svg'))
                item.setFlags(ITEM_ENABLED | ITEM_USER_CHECKABLE | ITEM_AUTO_TRISTATE)
                item.setCheckState(0, UNCHECKED)
                parent_item.addChild(item)
                children = self._fill_tree(item, node)
                if children == 0:
                    # Group without any spatial layer
                    parent_item.removeChild(item)
                count += children
            elif QgsLayerTree.isLayer(node):
                layer = node.layer()
                if layer is None or not layer.isSpatial():
                    continue
                item = QTreeWidgetItem([layer.name()])
                item.setIcon(0, layer_icon(layer))
                item.setData(0, USER_ROLE, layer.id())
                if layer_has_extent(layer):
                    item.setFlags(ITEM_ENABLED | ITEM_USER_CHECKABLE)
                    # Pre-check layers visible on the map (layer and all its parent groups checked),
                    # except basemaps (online services, tiles) whose extent is often the whole world
                    online = is_online_or_tiles(layer)
                    item.setCheckState(0, CHECKED if node.isVisible() and not online else UNCHECKED)
                    if online:
                        item.setToolTip(0, self.tr(u'Online service or tiles: not used for the extent by default'))
                else:
                    # Invalid or empty layer: listed for information, not selectable
                    item.setFlags(ITEM_USER_CHECKABLE)
                    item.setCheckState(0, UNCHECKED)
                    item.setToolTip(0, self.tr(u'This layer has no extent (empty or invalid layer)'))
                parent_item.addChild(item)
                count += 1
        return count

    def _layer_items(self, parent_item=None):
        """
        Yield layer items (leaves) in tree order
        """
        if parent_item is None:
            parent_item = self.tree.invisibleRootItem()
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.data(0, USER_ROLE):
                yield child
            else:
                yield from self._layer_items(child)

    def _set_all(self, state):
        for item in self._layer_items():
            if item.flags() & ITEM_ENABLED:
                item.setCheckState(0, state)

    def _update_ok_button(self, *args):
        self.button_box.button(BTN_OK).setEnabled(len(self.selected_layer_ids()) > 0)

    def selected_layer_ids(self):
        """
        :return: ids of checked layers, in layer tree order
        """
        return [item.data(0, USER_ROLE) for item in self._layer_items()
                if (item.flags() & ITEM_ENABLED) and item.checkState(0) == CHECKED]

    def buffer_percent(self):
        return self.sb_buffer.value()

    @staticmethod
    def _load_buffer():
        try:
            return int(QgsSettings().value(BUFFER_SETTINGS_KEY, DEFAULT_BUFFER_PERCENT))
        except (TypeError, ValueError):
            return DEFAULT_BUFFER_PERCENT

    def accept(self):
        # Remember buffer for next time
        QgsSettings().setValue(BUFFER_SETTINGS_KEY, self.sb_buffer.value())
        super(AutoLayoutToolDialogLayers, self).accept()
