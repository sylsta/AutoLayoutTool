# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoLayoutTool
                                 A QGIS plugin
 Persistence of user parameters.

 Default values are read from config/default.ini (shipped with the plugin,
 read-only). Custom values are stored in the QGIS user profile through
 QgsSettings, so they survive plugin updates and do not require write access
 to the plugin directory.
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

import os
from configparser import ConfigParser

from qgis.core import QgsSettings

PLUGIN_DIR = os.path.dirname(__file__)
DEFAULT_INI = os.path.join(PLUGIN_DIR, 'config', 'default.ini')
LEGACY_CUSTOM_INI = os.path.join(PLUGIN_DIR, 'config', 'custom.ini')

SETTINGS_ROOT = 'AutoLayoutTool'
SECTIONS = ('ITEMS_PLACEMENT', 'UI_OPTIONS')


def load_defaults():
    """
    Read default values shipped with the plugin
    :return: dict {section: {key: str}}
    """
    config = ConfigParser()
    config.read(DEFAULT_INI, encoding='utf-8')
    return {section: dict(config[section]) if config.has_section(section) else {}
            for section in SECTIONS}


def has_custom():
    """
    :return: True if custom values have been saved in the QGIS profile
    """
    settings = QgsSettings()
    settings.beginGroup(SETTINGS_ROOT)
    groups = settings.childGroups()
    settings.endGroup()
    return any(section in groups for section in SECTIONS)


def load(use_custom=True):
    """
    Load parameters: defaults, overridden by custom values if any
    :param use_custom: bool, False to get default values only
    :return: dict {section: {key: str}}
    """
    migrate_legacy_ini()
    values = load_defaults()
    if use_custom and has_custom():
        settings = QgsSettings()
        for section in SECTIONS:
            settings.beginGroup(f'{SETTINGS_ROOT}/{section}')
            for key in settings.childKeys():
                value = settings.value(key)
                if value is not None:
                    values[section][key] = str(value)
            settings.endGroup()
    return values


def save(values):
    """
    Save custom values in the QGIS profile
    :param values: dict {section: {key: value}}
    """
    settings = QgsSettings()
    for section, entries in values.items():
        for key, value in entries.items():
            settings.setValue(f'{SETTINGS_ROOT}/{section}/{key}', str(value))
    settings.sync()


def clear_custom():
    """
    Remove custom values from the QGIS profile
    """
    settings = QgsSettings()
    for section in SECTIONS:
        settings.remove(f'{SETTINGS_ROOT}/{section}')
    settings.sync()


def to_bool(value, default=True):
    """
    Convert a stored value to bool
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def migrate_legacy_ini():
    """
    One-shot migration: versions <= 2.3 stored custom values in config/custom.ini
    inside the plugin directory. Import them into QgsSettings, then try to remove the file.
    """
    flag = f'{SETTINGS_ROOT}/legacy_ini_migrated'
    if not os.path.isfile(LEGACY_CUSTOM_INI):
        return
    settings = QgsSettings()
    if to_bool(settings.value(flag), default=False):
        return
    if not has_custom():
        config = ConfigParser()
        config.read(LEGACY_CUSTOM_INI, encoding='utf-8')
        save({section: dict(config[section]) for section in SECTIONS if config.has_section(section)})
    # Flag avoids re-importing the file if it cannot be deleted and the user later restores defaults
    settings.setValue(flag, 'true')
    try:
        os.remove(LEGACY_CUSTOM_INI)
    except OSError:
        # Read-only plugin directory: the file will simply be ignored from now on
        pass
