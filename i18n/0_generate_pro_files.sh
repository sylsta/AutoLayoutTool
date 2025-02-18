#!/usr/bin/bash
# -*- encoding: UTF-8 -*-
DIRECTORY=..
PREFIX="AutoLayoutTool"
I18N_LIST="ar es fr pt ru zh"
FORMS="FORMS = "
SOURCES="SOURCES = "
TRANSLATIONS="TRANSLATIONS = "
for f in $DIRECTORY/*.ui; do
    FORMS="${FORMS} ${f}"
done
for f in $DIRECTORY/*.py; do
    if [[ "${f}" != "../__init__.py" ]] && [[ "${f}" != "../resources.py" ]]; then
        SOURCES="${SOURCES} ${f}"
    fi
done
for e in $I18N_LIST; do    
    TRANSLATIONS="${TRANSLATIONS} ${PREFIX}_${e}.ts"
done  
echo $FORMS >"${PREFIX}.pro"
echo $SOURCES >>"${PREFIX}.pro"
echo $TRANSLATIONS >>"${PREFIX}.pro"
