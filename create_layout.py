# -*- coding: utf-8 -*-
"""
/***************************************************************************
 createLayout
                                 A QGIS plugin
 Creates a layout with the current map canvas extent
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
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

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QColor, QFont
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsProject, QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLegend, QgsLayoutPoint, \
    QgsLayoutItemScaleBar, QgsUnitTypes, QgsLayoutItemPicture, QgsLayoutSize, QgsApplication

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .create_layout_dialog import createLayoutDialog
import os.path


class createLayout:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'createLayout_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&createLayout')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('createLayout', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # https://www.freepik.com/free-icon/layout_14181101.htm
        icon_path = ':/plugins/create_layout/layout.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Create a new layout based on current extent '),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&createLayout'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        # if self.first_start == True:
        #     self.first_start = False
        #     self.dlg = createLayoutDialog()
        #
        # # show the dialog
        # self.dlg.show()
        # # Run the dialog event loop
        # result = self.dlg.exec_()
        # # See if OK was pressed
        # if result:
        # Do something useful here - delete the line containing pass and
        # substitute with your code.
        e = self.iface.mapCanvas().extent()
        e.xMaximum()
        e.yMaximum()
        e.xMinimum()
        e.yMinimum()
        print(e)
        project = QgsProject.instance()
        manager = project.layoutManager()
        layoutname = 'Automatic layout'
        layouts_list = manager.printLayouts()
        # remove any duplicate layouts
        for layout in layouts_list:
            if layout.name() == layoutname:
                reply = QMessageBox.question(None, self.tr(u'Delete layout...'),
                                             self.tr(
                                                 u"There's already a layout named '%s'\nDo you want to delete it?" % layoutname),
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                else:
                    manager.removeLayout(layout)
                    print(self.tr(u"Previous layout names '%s' removed... " % layoutname))

        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        manager.addLayout(layout)
        layout.setName(layoutname)
        # Add map
        print("Adding map")
        map = QgsLayoutItemMap(layout)
        map.setRect(0, 0, 297, 210)
        map.setExtent(e)
        map.setBackgroundColor(QColor(255, 255, 255, 0))
        layout.addLayoutItem(map)

        ## Add legend
        print(self.tr(u"Adding legend"))
        lyrs_to_add = [l for l in QgsProject().instance().layerTreeRoot().children() if l.isVisible()]
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle('Legend')
        legend.setAutoUpdateModel(False)
        group = legend.model().rootGroup()
        group.clear()
        for l in lyrs_to_add:
            if l.nodeType() == 0:
                subgroup = group.addGroup(l.name())
                checked = l.checkedLayers()
                for c in checked:
                    subgroup.addLayer(c)
            elif l.nodeType() == 1:
                group.addLayer(l.layer())
        layout.addItem(legend)
        legend.adjustBoxSize()
        legend.refresh()

        ## Add scale bar
        print(self.tr(u"Adding scale bar"))
        scalebar = QgsLayoutItemScaleBar(layout)
        scalebar.setStyle('Single Box')
        scalebar.setLinkedMap(map)
        scalebar.applyDefaultSize()
        scalebar.applyDefaultSettings()
        scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
        scalebar.setUnitsPerSegment(scalebar.unitsPerSegment() / 1000)
        scalebar.setUnitLabel('km')
        scalebar.update()
        layout.addLayoutItem(scalebar)
        scalebar.attemptMove(QgsLayoutPoint(220, 190, QgsUnitTypes.LayoutMillimeters))

        ## Add north arrow
        print(self.tr(u"Add north arrow"))
        north = QgsLayoutItemPicture(layout)
        north.setPicturePath(os.path.dirname(__file__) + "/north-arrow.svg")
        layout.addLayoutItem(north)
        north.attemptResize(QgsLayoutSize(8, 13, QgsUnitTypes.LayoutMillimeters))
        north.attemptMove(QgsLayoutPoint(3, 190, QgsUnitTypes.LayoutMillimeters))
        manager.addLayout(layout)

        self.iface.openLayoutDesigner(layout)
        # new_rect=my_map.get
        # pass
