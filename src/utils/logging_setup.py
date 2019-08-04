#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Basic setup for root logger
"""

# Standard library
import os
import logging


def setup():
    log_level = os.environ.get('Log_Level', 'INFO').upper()

    logging.basicConfig(
        format='%(asctime)s: %(levelname)s: %(message)s',
        level=log_level
    )
