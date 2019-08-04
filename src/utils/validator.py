#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides interface for managing JSON
"""

# Standard library
import collections
import logging
import sys


def validate_json(json_obj):
    # Check if the json object is a dictionary
    if not isinstance(json_obj, collections.Mapping):
        logging.critical('Supplied metafile is not a valid json object')
        sys.exit(1)

    # Check if 'volumes' array is in root of json object
    try:
        json_obj['volumes']
    except KeyError as ex:
        logging.critical('Supplied metafile does not have a \'volumes\' array in its root object')
        sys.exit(1)

    # Check if objects are correctly formatted
    for obj in json_obj['volumes']:
        if len(obj.keys()) < 3:
            logging.critical('Too few elements in an object in the \'volumes\' array (3 elements expected)')
            sys.exit(1)
        for key in obj.keys():
            f1 = key.__eq__('volume_name')
            f2 = key.__eq__('current_snapshot_id')
            f3 = key.__eq__('snapshot_num')
            if (not f1) and (not f2) and (not f3):
                logging.critical('Unexpected element found in an object in the \'volumes\' array')
                logging.critical('Unexpected key: %s' % key)
                sys.exit(1)
