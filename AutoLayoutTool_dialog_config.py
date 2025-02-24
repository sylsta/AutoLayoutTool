# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoLayoutTool
                                 A QGIS plugin
 Creates a layout with the current map canvas extent
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-11-19
        git sha              : $Format:%H$
        copyright            : (c) 2021-2025 by Sylvain Théry
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

import os

from qgis.PyQt import uic, QtCore
from qgis.PyQt import QtWidgets
from configparser import ConfigParser

from qgis.core import QgsApplication, QgsPrintLayout, QgsProject

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'AutoLayoutTool_dialog_config.ui'))


class AutoLayoutToolDialogConfig(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AutoLayoutToolDialogConfig, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.plugin_dir = os.path.dirname(__file__)

        # North arrow, scale and legend combobox placement management management
        self.comboBox_list = [self.cbb_north, self.cbb_scalebar, self.cbb_legend]
        self.comboBox_value = [self.tr(u'Top left corner'), self.tr(u'Top right corner'),
                               self.tr(u'Bottom left corner'), self.tr(u'Bottom right corner'), self.tr('None')]
        for i in range(len(self.comboBox_list)):
            self.comboBox_list[i].addItems(self.comboBox_value)
            # Cant understand why this do not work
            # comboBox.currentTextChanged.connect(lambda x: self.cbb_state_changed(x, i))
            # self.comboBox_list[i].currentTextChanged.connect(lambda x: self.cbb_state_changed(x, i))
        self.cbb_north.currentTextChanged.connect(lambda x: self.cbb_state_changed(x, 0))
        self.cbb_scalebar.currentTextChanged.connect(lambda x: self.cbb_state_changed(x, 1))
        self.cbb_legend.currentTextChanged.connect(lambda x: self.cbb_state_changed(x, 2))

        for entry in QgsApplication.pageSizeRegistry().entries():
            self.cbb_page_format_name.addItem(entry.displayName)
        self.cbb_page_format_name.currentTextChanged.connect(self.items_changed)

        # # buttons action
        self.pb_restore.clicked.connect(self.load_default)
        self.pb_save.clicked.connect(self.write_custom_values)

        # # other staff signals
        self.le_layout_name.editingFinished.connect(self.items_changed)
        self.le_legend_title.editingFinished.connect(self.items_changed)
        self.sb_margin_value.editingFinished.connect(self.items_changed)
        self.set_form_values(False)



    def write_custom_values(self):
        """
        Write custom ini file if button pressed
        :return:
        """
        pass
        config_object = ConfigParser()
        config_object["ITEMS_PLACEMENT"] = {
            "cbb_north_value": self.cbb_north.currentIndex(),
            "cbb_scalebar_value": self.cbb_scalebar.currentIndex(),
            "cbb_legend_value_value": self.cbb_legend.currentIndex(),
            "le_legend_title_value": self.le_legend_title.text(),
            "sb_margin_value_value": self.sb_margin_value.value(),
            "le_layout_name_value": self.le_layout_name.text(),
            "cbb_page_format_value": self.cbb_page_format_name.currentText()
        }
        with open(self.plugin_dir + '/config/custom.ini', 'w') as conf:
            config_object.write(conf)
        self.pb_save.setEnabled(False)

    #
    def load_default(self, value):
        """
        Workaround. Action launched by restore button click
        :param value: boolean. True to load from default config file
        :return:
        """
        pass
        self.set_form_values(True)
    #
    def set_form_values(self, default):
        """
        Either load default or custom values from file and feed form components
        :param default:
        :return:
        """
        print(self.plugin_dir)
        config_object = ConfigParser()
        if not default and os.path.isfile(self.plugin_dir + '/config/custom.ini'):
            config_object.read(self.plugin_dir + '/config/custom.ini')
            self.pb_restore.setEnabled(True)
            self.pb_save.setEnabled(False)
        else:
            config_object.read(self.plugin_dir + '/config/default.ini')
            self.pb_restore.setEnabled(False)
            self.pb_save.setEnabled(False)
            try:
                os.remove(self.plugin_dir + '/config/custom.ini')
            except:
                pass
        file_values = config_object["ITEMS_PLACEMENT"]
        self.cbb_north.setCurrentIndex(int(file_values["cbb_north_value"]))
        self.cbb_scalebar.setCurrentIndex(int(file_values["cbb_scalebar_value"]))
        self.cbb_legend.setCurrentIndex(int(file_values["cbb_legend_value_value"]))
        self.le_legend_title.setText(self.tr(file_values["le_legend_title_value"]))
        self.sb_margin_value.setValue(int(file_values["sb_margin_value_value"]))
        self.le_layout_name.setText(self.tr(file_values["le_layout_name_value"]))
        # Since default layout size is not define in default config file, we have to set right index of the combobox
        # from qgis default size
        try:
            self.cbb_page_format_name.setCurrentIndex(int(file_values["cbb_page_format_value"]))
        except:
            tmp_layout = QgsPrintLayout(QgsProject.instance())
            tmp_layout.initializeDefaults()
            text = QgsApplication.pageSizeRegistry().find(tmp_layout.pageCollection().page(0).pageSize())
            try:
                match_fixed_string = QtCore.Qt.MatchFlag.MatchFixedString # PyQt6
            except AttributeError:
                match_fixed_string = QtCore.Qt.MatchFixedString  # PyQt5



            index = self.cbb_page_format_name.findText(text, match_fixed_string)
            if index >= 0:
                self.cbb_page_format_name.setCurrentIndex(index)

        if not default and os.path.isfile(self.plugin_dir + '/config/custom.ini'):

            self.pb_restore.setEnabled(True)
            self.pb_save.setEnabled(False)
        else:

            self.pb_restore.setEnabled(False)
            self.pb_save.setEnabled(False)


    def cbb_state_changed(self, text, i):
        """
        Check if other comboxbox index has to be changed, since placements have to be differents.
        :param text: string, combobox current text
        :param i: int, combobox id
        :return:
        """
        nb_of_cbb = len(self.comboBox_list)
        nb_of_cbbox_values = len(self.comboBox_value) - 1
        if text != self.comboBox_value[nb_of_cbbox_values]:  # value "None"
            list_id_combobox_tocheck = set(range(nb_of_cbb)) - set([i])
            for j in list_id_combobox_tocheck:
                if self.comboBox_list[j].currentText() == text:
                    self.comboBox_list[j].setCurrentIndex(nb_of_cbbox_values)
        self.items_changed()

    def items_changed(self):
        """
        Enable saving/restoring default values
        """
        self.pb_restore.setEnabled(True)
        self.pb_save.setEnabled(True)