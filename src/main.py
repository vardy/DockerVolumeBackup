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

# Third party libraries
from botocore.exceptions import ClientError

# Local source
from client import Client
from progress import ProgressPercentage

def main():
    log_level = os.environ.get('Log_Level', 'INFO').upper()

    logging.basicConfig(
        format='%(asctime)s: %(levelname)s: %(message)s', 
        level=log_level
    )

    logging.info('Contents of host volumes directory...')
    logging.info(os.listdir('/HostVolumeData'))

    client = Client()

    if client.get_s3_client() is not None:
        volumes_to_backup = client.get_volumes_to_backup()
        if not ''.__eq__(volumes_to_backup):
            arr_volumes = [x.strip() for x in volumes_to_backup.split(',')]
            # If metafile does not exist in directory, generate metafile
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

def upload_file(file_name, client, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param client: Client object
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    s3_client = client.get_s3_client()

    # Upload the file
    try:
        response = s3_client.upload_file(
            file_name, client.get_bucket_name(), object_name, 
            Callback=ProgressPercentage(file_name)
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True

if __name__ =='__main__':
    main()