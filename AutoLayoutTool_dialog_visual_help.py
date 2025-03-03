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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import (Qt, QSize,QByteArray, pyqtSlot, pyqtSignal, QThread)
from qgis.PyQt.QtGui import (QMovie)
from qgis.PyQt.QtWidgets import ( QWidget,QSizePolicy,QVBoxLayout, QLabel,
                             QDialogButtonBox)
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'AutoLayoutTool_visual_help.ui'))
#

class AutoLayoutToolDialogVisualHelp(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Load the file into a QMovie
        self.plugin_dir = os.path.dirname(__file__)
        self.movie = QMovie(f"{self.plugin_dir}/help/AutoLayoutTool_visual_demo.gif", QByteArray(), self)
        size = self.movie.scaledSize()
        self.setGeometry(200, 200, size.width(), size.height())
        self.setWindowTitle(self.tr("AutoLayoutTool visual help"))

        self.movie_screen = QLabel()
        # Make label fit the gif
        try:
            expanding = QSizePolicy.Policy.Expanding  # Compatible PyQt6
        except AttributeError:
            expanding = QSizePolicy.Expanding  # Compatible PyQt5

        self.movie_screen.setSizePolicy(expanding, expanding)
        try:
            align_center = Qt.AlignmentFlag.AlignCenter  # PyQt6
        except AttributeError:
            align_center = Qt.AlignCenter  # PyQt5

        self.movie_screen.setAlignment(align_center)

        # Create the layout
        main_layout = QVBoxLayout()

        try:
            close_button = QDialogButtonBox.StandardButton.Close  # PyQt6
        except AttributeError:
            close_button = QDialogButtonBox.Close  # PyQt5

        self.button_box = QDialogButtonBox(close_button)

        self.button_box.rejected.connect(self.close)
        main_layout.addStretch()  # Ajoute un espace flexible
        main_layout.addWidget(self.button_box)  # Ajoute le QDialogButtonBox en bas
        main_layout.addWidget(self.movie_screen)
        self.button_box2 = QDialogButtonBox(close_button)
        self.button_box2.rejected.connect(self.close)
        main_layout.addStretch()  # Ajoute un espace flexible
        main_layout.addWidget(self.button_box2)  # Ajoute le QDialogButtonBox en bas
        self.setLayout(main_layout)

        # Add the QMovie object to the label
        try:
            cache_all = QMovie.CacheMode.CacheAll  # PyQt6
        except AttributeError:
            cache_all = QMovie.CacheAll  # PyQt5

        self.movie.setCacheMode(cache_all)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()

