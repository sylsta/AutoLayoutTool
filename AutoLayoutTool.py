# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoLayoutTool : One-click print layout creator

                                 A QGIS3 plugin

This plugin creates in one click a layout based on the extent of a QGIS
project main window. It also adds a legend, a scale bar and a north arrow to
the layout. The size of the map is calculated to occupy the maximum space
on the page and the orientation of the page is determined by the extent of
the map.

Ce plugin crée en un clic une mise en page basée sur l'étendue de la fenêtre
principale d'un projet QGIS. Il ajoute également une légende, une barre
d'échelle et une flèche du nord à la mise en page. La taille de la carte est
calculée pour occuper l'espace maximum sur la page et l'orientation de la
page est déterminée par l'étendue de la carte.

Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
Icon from   https://www.freepik.com/free-icon/layout_14181101.htm
            https://www.flaticon.com/free-icon/website_1238251


                              -------------------
        begin                : 2021-11-19
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Sylvain Théry
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

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QColor, QKeySequence
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QShortcut
from qgis.core import QgsProject, QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLegend, QgsLayoutPoint, \
    QgsLayoutItemScaleBar, QgsUnitTypes, QgsLayoutItemPicture, QgsLayoutSize, QgsApplication, QgsLayoutItemPage

import os.path
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .AutoLayoutTool_dialog import AutoLayoutToolDialog

class AutoLayoutTool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # debug state for pycharm (pro version only :-() python debug server
        self.debug = True
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AutoLayoutTool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
        try:
            locale.setlocale(
                locale.LC_ALL,
                QSettings().value('locale/userLocale')
            )
        except:
            pass

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&AutoLayoutTool')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # Use pyCharm debug server
        if self.debug:
            try:
                import pydevd_pycharm
                #pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
                pydevd_pycharm.settrace('localhost', port=53100, suspend=False)
            except:
                pass
        self.default_values()


    def tr(self, message):
        """
        Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AutoLayoutTool', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # will be set False in run()
        self.first_start = True

        # Run entry menu
        text = self.tr(u'Create a new layout based on current extent ')
        action = QAction(QIcon(':/plugins/AutoLayoutTool/images/layout.png'), text, self.iface.mainWindow())
        self.iface.registerMainWindowAction(action, "Ctrl+F4")
        self.iface.addPluginToMenu(self.menu, action)
        action.triggered.connect(self.run)
        self.actions.append(action)
        action.setStatusTip(text)
        action.setWhatsThis(text)
        self.iface.addToolBarIcon(action)
        self.actions.append(action)

        # Config entry menu
        text = self.tr("AutoLayoutTool configuration")
        action = QAction(QIcon(':/plugins/AutoLayoutTool/images/config.png'), text, self.iface.mainWindow())
        self.iface.registerMainWindowAction(action, "Ctrl+Shift+F4")
        self.iface.addPluginToMenu(self.menu, action)
        action.triggered.connect(self.config)
        self.actions.append(action)

        self.default_values()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&AutoLayoutTool'),
                action)
            self.iface.removeToolBarIcon(action)


    def create_layout(self, layout_name):
        """
        Layout Management: creates new layout and delete previous
        :param layout_name:
        :return
        :rtype:QgsLayout, QgsProject.instance().layoutManager()
        """
        project = QgsProject.instance()
        manager = project.layoutManager()
        layouts_list = manager.printLayouts()
        for layout in layouts_list:
            if layout.name() == layout_name:
                reply = QMessageBox.question(None, self.tr(u'Delete layout...'),
                                             self.tr(
                                                 u"There's already a layout named '%s'\nDo you want to delete it?")
                                             % layout_name,
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                try:
                    if reply == QMessageBox.No:
                        return
                    else:
                        manager.removeLayout(layout)
                        print(self.tr(u"Previous layout named '%s' removed... ") % layout_name)
                except:
                    # in case ESC key is pressed to escape the dialog
                    return

        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        return layout, manager

    def compute_layout_orientation(self, e, layout):
        """
        Determine and set best layout orientation
        :param e: iface.mapCanvas().extent()
        :param layout: QgsLayout
        :rtype: bool, float, float, float, float, float
        """
        print('Creating layout')
        map_width = e.xMaximum() - e.xMinimum()
        map_height = e.yMaximum() - e.yMinimum()

        page_size = QgsApplication.pageSizeRegistry().find(layout.pageCollection().page(0).pageSize())  # eg. 'A4' str
        landscape = False
        if map_width <= map_height:
            # portrait
            if self.debug: print("Portrait")
            layout.pageCollection().page(0).setPageSize(page_size, QgsLayoutItemPage.Orientation.Portrait)
        else:
            # landscape
            if self.debug: print("Landscape")
            layout.pageCollection().page(0).setPageSize(page_size, QgsLayoutItemPage.Orientation.Landscape)
            landscape = True
        # Calculate scale ratio between layout size and map size
        layout_width = layout.pageCollection().page(0).pageSize().width()
        layout_height = layout.pageCollection().page(0).pageSize().height()
        if landscape:
            scale_ratio = (layout_width / map_width)
            if map_height * scale_ratio > layout_height:
                scale_ratio = map_height / layout_height
        else:
            scale_ratio = layout_height / map_height
            if map_width * scale_ratio > layout_width:
                scale_ratio = map_height / layout_height
        return landscape, layout_height, layout_width, map_height, map_width, scale_ratio

    def calculate_map_scale(self, landscape, layout, layout_height, layout_width, map_height, map_width, scale_ratio):
        """
        Calculate map scale
        :param landscape: boolean
        :param layout: QgsLayout
        :param layout_height: float
        :param layout_width: float
        :param map_height: float
        :param map_width: float
        :param scale_ratio: float
        :rtype: float, float, QgsLayoutItemMap
        """
        print(self.tr(u'Calculating scale'))
        my_map = QgsLayoutItemMap(layout)
        if self.debug: print("mapw: %r / maph: %r" % (map_width, map_height))
        if self.debug: print("scale ratio: %r" % scale_ratio)
        previous_height = map_height
        previous_width = map_width
        if landscape:
            if self.debug: print("Landscape")
            map_width = layout_width
            map_height = round(map_height * scale_ratio, 3)  # makes qgis bug if not rounded 3
            if self.debug: print("ori_mapw: %r / ori_maph: %r" % (map_width, map_height))
            # workaround don't now why in special case it has to be changed !:#
            if map_height > layout_height:
                map_height = layout_height
                map_width = round(previous_width / scale_ratio, 3)
                if self.debug: print("corr_mapw: %r / corr_maph: %r" % (map_width, map_height))
        else:
            if self.debug: print("Portrait")
            map_width = round(map_width * scale_ratio, 3)
            map_height = layout_height
            if self.debug: print("ori_mapw: %r / ori_maph: %r" % (map_width, map_height))
            # workaround: don't now why in special case it has to be changed ! (extent is nearly a square 4 instance)
            if map_width > map_height:
                map_width = layout_width
                map_height = round(previous_height / scale_ratio, 3)
                if self.debug: print("corr_mapw: %r / corr_maph: %r" % (map_width, map_height))

        if self.debug: print("final_mapw: %r / final_maph: %r" % (map_width, map_height))
        return map_height, map_width, my_map

    def add_map(self, e, layout, layout_height, layout_width, map_height, map_width, margin, my_map):
        """
        Add map to the layout
        :param e: iface.mapCanvas().extent()
        :param layout: QgsLayout
        :param layout_height: float
        :param layout_width: float
        :param map_height: float
        :param map_width: float
        :param margin: float
        :param my_map: QgsLayoutItemMap
        :rtype: float, float, float, float
        """
        print('Adding map')
        map_width = map_width - margin
        map_height = map_height - margin
        my_map.setRect(0, 0, map_width, map_height)
        my_map.setExtent(e)
        layout.addLayoutItem(my_map)
        my_map.refresh()
        map_real_width = my_map.rect().size().width()
        map_real_height = my_map.rect().size().height()
        x_offset = (layout_width - map_real_width) / 2
        y_offset = (layout_height - map_real_height) / 2
        if self.debug: print("x_offset: %r / y_offset: %r" % (x_offset, y_offset))
        if self.debug: print("real_mapw: %r / real_maph: %r" % (map_real_width, map_real_height))
        my_map.setBackgroundColor(QColor(255, 255, 255, 255))
        my_map.setFrameEnabled(True)
        my_map.attemptMove(QgsLayoutPoint(x_offset, y_offset, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(my_map)
        return map_real_height, map_real_width, x_offset, y_offset

    def add_legend(self, layout, x_offset, y_offset):
        """
        Add legend to the layout
        :param layout: QgsLayout
        :param x_offset: float
        :param y_offset: float
        :return: None
        """
        print(self.tr(u"Adding legend"))
        layers_to_add = [l for l in QgsProject().instance().layerTreeRoot().children() if l.isVisible()]
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle(self.tr(u'Legend'))
        legend.setAutoUpdateModel(False)
        group = legend.model().rootGroup()
        group.clear()
        for l in layers_to_add:
            if l.nodeType() == 0:
                subgroup = group.addGroup(l.name())
                checked = l.checkedLayers()
                for c in checked:
                    subgroup.addLayer(c)
            elif l.nodeType() == 1:
                group.addLayer(l.layer())
        layout.addItem(legend)
        legend.adjustBoxSize()
        legend.setFrameEnabled(True)
        legend.attemptMove(QgsLayoutPoint(x_offset, y_offset, QgsUnitTypes.LayoutMillimeters))
        legend.refresh()

    def add_scalebar(self, layout, map_real_height, map_real_width, my_map, x_offset, y_offset):
        """
        Add scalebar to the layout
        :param layout: QgsLayout
        :param map_real_height: float
        :param map_real_width: float
        :param my_map: QgsLayoutItemMap
        :param x_offset: float
        :param y_offset: float
        :return: None
        """
        print(self.tr(u'Adding scale bar'))
        scalebar = QgsLayoutItemScaleBar(layout)
        scalebar.setStyle('Single Box')
        scalebar.setLinkedMap(my_map)
        scalebar.applyDefaultSize()
        scalebar.applyDefaultSettings()
        scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
        scalebar.setUnitsPerSegment(scalebar.unitsPerSegment() / 1000)
        scalebar.setUnitLabel('km')
        scalebar.update()
        layout.addLayoutItem(scalebar)
        scalebar.attemptMove(QgsLayoutPoint(map_real_width + x_offset - scalebar.rect().size().width() - 5,
                                            map_real_height + y_offset - scalebar.rect().size().height() - 5,
                                            QgsUnitTypes.LayoutMillimeters))

    def add_north_arrow(self, layout, manager, map_real_height, x_offset, y_offset):
        """
        Adds north arrow to the layout
        :param layout: QgsLayout
        :param manager: QgsProject.instance().layoutManager()
        :param map_real_height: float
        :param x_offset: float
        :param y_offset: float
        :return: None
        """
        print(self.tr(u"Adding north arrow"))
        north = QgsLayoutItemPicture(layout)
        north.setPicturePath(os.path.dirname(__file__) + "/images/north-arrow.svg")
        layout.addLayoutItem(north)
        north.attemptResize(QgsLayoutSize(8, 13, QgsUnitTypes.LayoutMillimeters))
        north.attemptMove(QgsLayoutPoint(3 + x_offset, map_real_height + y_offset - 15, QgsUnitTypes.LayoutMillimeters))

    def config(self):
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = AutoLayoutToolDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass

        # Do something useful here - delete the line containing pass and
        # substitute with your code.

    def run(self):
        """
        Creates a layout with a map of the current interface extent, with legend, scalebar and north arrow
        :return: None
        """



        print('--------------------------------')
        print(self.tr(u'AutoLayoutTool starts'))
        print('--------------------------------')
        e = self.iface.mapCanvas().extent()
        map_width = e.xMaximum() - e.xMinimum()
        map_height = e.yMaximum() - e.yMinimum()
        if (map_height==0) or (map_width==0):
            print(self.tr(u'No loaded data - aborting'))
            print('--------------------------------')
            return


        # Create layout
        try:
            layout, manager = self.create_layout(self.layout_name)
        except:
            # Quick and dirty. In case people decide not to replace previous layout
            print(self.tr(u'Cancelled by user'))
            print('--------------------------------')
            return

        # Determine and set best layout orientation
        landscape, layout_height, layout_width, map_height, map_width, scale_ratio = self.compute_layout_orientation(
                                                                            e, layout)

        # Calculate scale
        map_height, map_width, my_map = self.calculate_map_scale(landscape, layout, layout_height, layout_width,
                                                                 map_height, map_width, scale_ratio)

        # Add map
        map_real_height, map_real_width, x_offset, y_offset = self.add_map(e, layout,
                                                                           layout_height, layout_width, map_height,
                                                                           map_width, self.margin, my_map)

        # Add legend
        self.add_legend(layout, x_offset, y_offset)

        # Add scale bar
        self.add_scalebar(layout, map_real_height, map_real_width, my_map, x_offset, y_offset)

        # Add north arrow
        self.add_north_arrow(layout, manager, map_real_height, x_offset, y_offset)

        # Finally add layout to the project via its manager
        manager.addLayout(layout)
        self.iface.openLayoutDesigner(layout)
        print('--------------------------------')
        print("♪♪ This is the end, my friend ♪♪")
        print('--------------------------------')


    def default_values(self):
        # default values for parameters
        self.margin = 10
        self.layout_name = self.tr('Automatic layout')
