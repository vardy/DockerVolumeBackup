#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Utility object that is used to print the progress of
    file uploads.
"""

# Standard library
import os
import sys
import threading

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                '\r%s  %s / %s  (%.2f%%)\n' % (
                    self._filename, 
                    self._seen_so_far, 
                    self._size,
                    percentage
                )
            )
            sys.stdout.flush()