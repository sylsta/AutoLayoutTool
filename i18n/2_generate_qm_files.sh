#!/usr/bin/bash
# -*- encoding: UTF-8 -*-

# generate compiled translation files (*.qm) from translation files (*.ts) files
# cf. https://docs.qgis.org/3.10/fr/docs/pyqgis_developer_cookbook/plugins/plugins.html#files-and-directory

for f in $( ls ./*.ts -R )
  do
    lrelease $f
  done
