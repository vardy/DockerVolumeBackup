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
import tarfile
import time
from datetime import datetime

# Third party libraries
import schedule
import boto3  # S3 API interface

# Local source
from utils import logging_setup
from config.config import Config
import s3

config = Config()


def main():
    logging_setup.setup()
    schedule_tasks()
    logging.info('Tasks scheduled')
    if config.get_do_backup_on_startup():
        logging.info('Running scheduled tasks...')
        schedule.run_all(1)
    logging.info('Tasks: %s' % schedule.jobs)
    while True:
        logging.info('Running pending tasks...')
        schedule.run_pending()
        time.sleep(30)


def schedule_tasks():
    snapshot_interval = config.get_snapshot_interval()
    schedule.every(snapshot_interval).hours.do(backup)
    #schedule.every(10).seconds.do(backup)


def backup():
    if os.getenv('Disabled') == 'yes':
        return

    logging.info('Contents of host volumes directory...')
    logging.info(os.listdir('/HostVolumeData'))

    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        aws_access_key_id=config.get_s3_access_key(),
        aws_secret_access_key=config.get_s3_secret_key(),
        region_name=config.get_s3_region(),
        endpoint_url=config.get_s3_endpoint(),
    )

    if s3_client is not None:
        volumes_to_backup = config.get_volumes_to_backup()
        if not '' == volumes_to_backup:

            # Generating temporary directory
            if not os.path.exists('temp'):
                os.makedirs('temp')

            # Check if each volume listed in environment variables exists within host filesystem
            arr_volumes = [x.strip() for x in volumes_to_backup.split(',')]
            for vol in arr_volumes:
                if vol not in os.listdir('/HostVolumeData'):
                    arr_volumes.remove(vol)
                    logging.error('Volume \'%s\' is not in host\'s Docker filesystem.' % vol)

            # # # S3 directory structure
            #
            # env_bucket_name/
            #     env_directory_name/
            #         volume_name/
            #             BACKUP_<date-time>.tar.gz
            #             BACKUP_<date-time>.tar.gz
            #             ...
            #             SNAPSHOT_<snapshot-number>.tar.gz
            for vol_name in arr_volumes:

                # Open archive file to pack backup data into
                tar = tarfile.open('./temp/archive_build.tar.gz', 'w:gz')
                for file_name in os.listdir('/HostVolumeData/%s/_data/' % vol_name):
                    # File name to archive
                    file_path = '/HostVolumeData/%s/_data/%s' % (vol_name, file_name)
                    tar.add(file_path, arcname=file_name)
                tar.close()

                latest_snapshot_path = s3.get_key_from_prefix(
                    '%s/%s/SNAPSHOT-' % (config.get_directory_name(), vol_name), 
                    s3_client
                )
                if latest_snapshot_path is not False:
                    latest_snapshot_number = latest_snapshot_path[
                        latest_snapshot_path.index('SNAPSHOT-') + len('SNAPSHOT-'):-7
                    ]
                else:
                    latest_snapshot_number = 0

                if int(latest_snapshot_number) > 0:
                    if not int(latest_snapshot_number) + 1 > config.get_backup_interval():
                        response = s3.delete_objects_by_prefix(
                            '%s/SNAPSHOT-' % vol_name,
                            s3_client
                        )
                    else:
                        # Copy file to new object name and then delete old version
                        s3_client.copy(  # From here
                                       {
                                           'Bucket': config.get_bucket_name(),
                                           'Key': s3.get_key_from_prefix('%s/%s/SNAPSHOT-' % (
                                                          config.get_directory_name(), vol_name
                                                      ), s3_client
                                                  )
                                       },
                                       # To here
                                       config.get_bucket_name(),
                                       '%s/%s/BACKUP-%s.tar.gz' % (
                                           config.get_directory_name(),
                                           vol_name,
                                           datetime.now().strftime('%Y%m%d-%H%M%S')
                                       )
                        )
                        s3.delete_objects_by_prefix('%s/SNAPSHOT-' % vol_name, s3_client)
                        latest_snapshot_number = '0'
                
                response = s3.upload_file('./temp/archive_build.tar.gz', s3_client, '%s/SNAPSHOT-%s.tar.gz' % (
                    vol_name,
                    str(int(latest_snapshot_number) + 1)
                ))
        else:
            logging.critical('No volumes were specified.')
            sys.exit(1)
    else:
        logging.critical('Client failed to be instantiated.')
        sys.exit(1)


if __name__ == '__main__':
    main()
