#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Main class of DockerVolumeBackup.
    Carries out procedure of retrieving data from Docker
    volumes specified and snapshotting data backups.
"""

# Standard library
import os
import sys
import json
import uuid
import collections
import logging
import time
from datetime import datetime

# Third party libraries
import schedule
import boto3  # S3 API interface

# Local source
from utils import logging_setup
from utils import validator
from config.config import Config
import s3

config = Config()


def main():
    logging_setup.setup()
    schedule_tasks()
    logging.info('Tasks scheduled')
    if config.get_do_backup_on_startup():
        logging.info('Running scheduled tasks...')
        schedule.run_all(0)
    logging.info('Tasks: %s' % schedule.jobs)
    while True:
        logging.info('Running pending tasks...')
        schedule.run_pending()
        time.sleep(30)


def schedule_tasks():
    snapshot_interval = config.get_snapshot_interval()
    schedule.every(snapshot_interval).hours.do(backup)


def gen_uuid():
    return uuid.uuid4().hex[:6]


def backup():
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
        if not ''.__eq__(volumes_to_backup):

            # Adding metafile to S3 directory if it does not already exist
            # stores data relevant to tracking snapshot/backup progress
            if not s3.check_if_object_exists('metafile', s3_client):
                s3.upload_file('metafile_base.json', s3_client, 'metafile')

            # Generating temporary directory
            if not os.path.exists('temp'):
                os.makedirs('temp')

            # Download metafile locally to temporary directory, to be edited and
            # re-uploaded once all backups have finished.
            s3.download_object('metafile', s3_client, '/temp/metafile')
            with open('./temp/metafile') as metafile_bin:
                metafile_json = json.load(metafile_bin)
                metafile_bin.close()

            validator.validate_json(metafile_json)
            meta_vols = metafile_json['volumes']

            # Check if each volume listed in environment variables exists within host filesystem
            arr_volumes = [x.strip() for x in volumes_to_backup.split(',')]
            for vol in arr_volumes:
                if vol in os.listdir('/HostVolumeData'):
                    found = False
                    for i in range(0, len(meta_vols)):
                        if meta_vols[i]['volume_name'].__eq__(vol):
                            # Volume exists in both metafile and filesystem
                            found = True
                    if not found:
                        # Volume exists but is not in metafile
                        # Add to metafile
                        meta_vols.append({
                            'volume_name': vol,
                            'current_snapshot_id': gen_uuid(),
                            'snapshot_num': 0
                        })
                else:
                    logging.error('Volume \'%s\' is not in host\'s Docker filesystem.' % vol)

            for i in range(0, len(meta_vols)):
                meta_obj = meta_vols[i]
                meta_obj['snapshot_num'] = meta_obj['snapshot_num'] + 1
                vol_name = meta_obj['volume_name']
                for file_name in os.listdir('/HostVolumeData/%s/_data/' % vol_name):
                    file_path = '/HostVolumeData/%s/_data/%s' % (vol_name, file_name)

                    if meta_obj['snapshot_num'] - 1 > 0:
                        if not meta_obj['snapshot_num'] > config.get_backup_interval():
                            response = s3.delete_directory(
                                '%s/%s_%d' % (
                                    meta_obj['volume_name'],
                                    meta_obj['current_snapshot_id'],
                                    meta_obj['snapshot_num'] - 1
                                ),
                                s3_client
                            )
                        else:
                            meta_obj['current_snapshot_id'] = gen_uuid()
                            meta_obj['snapshot_num'] = 1
                    response = s3.upload_file(file_path, s3_client, '%s/%s_%d_%s/%s' % (
                        meta_obj['volume_name'],
                        meta_obj['current_snapshot_id'],
                        meta_obj['snapshot_num'],
                        datetime.now().strftime('%Y-%m-%d-%H%M'),
                        file_name
                    ))

            # Write new metafile json to temp filesystem
            with open('./temp/metafile', 'w+') as json_bin:
                json.dump(metafile_json, json_bin, indent=4)

            # Upload new metafile from temp filesystem to S3 for use
            # in next backup.
            response = s3.upload_file(
                './temp/metafile',
                s3_client,
                'metafile'
            )
        else:
            logging.critical('No volumes were specified.')
            sys.exit(1)
    else:
        logging.critical('Client failed to be instantiated.')
        sys.exit(1)


if __name__ == '__main__':
    main()
