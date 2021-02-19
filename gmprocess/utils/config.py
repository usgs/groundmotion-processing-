#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import pkg_resources
from configobj import ConfigObj

from gmprocess.utils import constants


def update_dict(target, source):
    """Merge values from source dictionary into target dictionary.

    Args:
        target (dict):
            Dictionary to be updated with values from source dictionary.

        source (dict):
            Dictionary with values to be transferred to target dictionary.
    """
    for key, value in source.items():
        if not isinstance(value, dict) or \
                key not in target.keys() or \
                not isinstance(target[key], dict):
            target[key] = value
        else:
            update_dict(target[key], value)
    return


def merge_dicts(dicts):
    """Merges a list of dictionaries into a new dictionary.

    The order of the dictionaries in the list provides precedence of the
    values, with values from subsequent dictionaries overriding earlier
    ones.

    Args:
        dicts (list of dictionaries):
            List of dictionaries to be merged.

    Returns:
        dictionary: Merged dictionary.
    """
    target = dicts[0].copy()
    for source in dicts[1:]:
        update_dict(target, source)
    return target


def get_config(config_file=None, section=None):
    """Gets the user defined config and validates it.

    Args:
        config_file:
            Path to config file to use. If None, uses defaults.
        section (str):
            Name of section in the config to extract (i.e., 'fetchers',
            'processing', 'pickers', etc.) If None, whole config is returned.

    Returns:
        dictionary:
            Configuration parameters.
    Raises:
        IndexError:
            If input section name is not found.
    """

    if config_file is None:
        # Try not to let tests interfere with actual system:
        if os.getenv('CALLED_FROM_PYTEST') is None:
            # Not called from pytest
            local_proj = os.path.join(os.getcwd(), constants.PROJ_CONF_DIR)
            local_proj_conf = os.path.join(local_proj, 'projects.conf')
            if os.path.isdir(local_proj) and os.path.isfile(local_proj_conf):
                PROJECTS_PATH = local_proj
            else:
                PROJECTS_PATH = constants.PROJECTS_PATH
            PROJECTS_FILE = os.path.join(PROJECTS_PATH, 'projects.conf')
            projects_conf = ConfigObj(PROJECTS_FILE, encoding='utf-8')
            project = projects_conf['project']
            current_project = projects_conf['projects'][project]
            conf_path = current_project['conf_path']
            config_file = os.path.join(conf_path, 'config.yml')
        else:
            data_dir = os.path.abspath(
                pkg_resources.resource_filename('gmprocess', 'data'))
            config_file = os.path.join(data_dir, constants.CONFIG_FILE_TEST)

    if not os.path.isfile(config_file):
        fmt = ('Missing config file: %s.')
        raise OSError(fmt % config_file)
    else:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

    if section is not None:
        if section not in config:
            raise IndexError('Section %s not found in config file.' % section)
        else:
            config = config[section]

    return config
