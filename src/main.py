#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Main class of DockerVolumeBackup.
    Carries out procedure of retrieving data from Docker
    volumes specified and snapshotting data backups.
"""

# Standard library
import os
import sys
import logging
import subprocess  # Module used for shell commands

# Local source
import logging_setup
import s3_util
from client import Client

def main():
    logging.info('Contents of host volumes directory...')
    logging.info(os.listdir('/HostVolumeData'))

    client = Client()

    if client.get_s3_client() is not None:
        volumes_to_backup = client.get_volumes_to_backup()
        if not ''.__eq__(volumes_to_backup):

            metafile_exists = s3_util.check_if_object_exists('metafile', client)
            if not metafile_exists:
                s3_util.upload_file('metafile_base.json', client, 'metafile')

            arr_volumes = [x.strip() for x in volumes_to_backup.split(',')]
            for vol in arr_volumes:
                return
                # Check if volume exists, if not throw error and move on
                # Check if entry for volume exists in metafile volumes array
                #   If entry exists move on
                #   else add entry, generate snapshotID, init snapshot num to 0
                # Check metafile
                #   Increment snapshot number
                #   If snapshot number > interval, create new file and save first snapshot, reset snapshot num, generate new snapshot id
                #   else overwrite current snapshot with new interval number
                #
                ## S3 Directory Structure
                #
                # s3_directory/
                #     metafile
                #     volume_name/
                #         snapshotID_Interval_DateTime/
                #             data~
                #     volume_name/
                #         snapshotID_Interval_DateTime/
                #             data~
                #         snapshotID_Interval_DateTime/
                #             data~
                #
                ## Metafile Structure (JSON)
                #
                # {
                #     "volumes": [
                #         {
                #              "volume_name": "loyalbot_db-data",
                #              "current_snapshot_id": "uuid",
                #              "snapshot_num": 1
                #         },
                #         {
                #              "volume_name": "onebillionquacks_db-data",
                #              "current_snapshot_id": "uuid",
                #              "snapshot_num": 1
                #         }
                #     ]
                # }
                #
                # Add system for how long to keep backups
                # Add options for verbosity (file upload progress in stdout) (logging levels)
        else:
            logging.critical('No volumes were specified.')
            sys.exit(1)
            return
    else:
        logging.critical('Client failed to be instantiated.')
        sys.exit(1)
        return

if __name__ =='__main__':
    main()