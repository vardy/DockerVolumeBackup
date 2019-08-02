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
import logging
from datetime import datetime

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
            
            if not os.path.exists('temp'):
                os.makedirs('temp')
            
            # Download metafile locally to be edited re-upload
            # once all backups have finished.
            s3_util.download_object('metafile', client, '/temp/metafile')
            with open('./temp/metafile') as metafile_bin:
                metafile_json = json.load(metafile_bin)
                metafile_bin.close()

            arr_volumes = [x.strip() for x in volumes_to_backup.split(',')]
            for vol in arr_volumes:
                if vol in os.listdir('/HostVolumeData'):
                    found = False
                    for i in range(0, len(metafile_json['volumes'])):
                        if metafile_json['volumes'][i]['volume_name'].__eq__(vol):
                            found = True
                    if not found:
                        # Volume exists but is not in metafile
                        metafile_json['volumes'].append({
                                'volume_name': vol, 
                                'current_snapshot_id': uuid.uuid4().hex, 
                                'snapshot_num': 0
                        })
                else:
                    logging.error('Volume from env \'%s\' is not in host\'s Docker filesystem.' % (vol))

            for i in range(0, len(metafile_json['volumes'])):
                metafile_json['volumes'][i]['snapshot_num'] = metafile_json['volumes'][i]['snapshot_num'] + 1
                for file_name in os.listdir('/HostVolumeData/%s/_data/' % (metafile_json['volumes'][i]['volume_name'])):
                    file_path = '/HostVolumeData/%s/_data/%s' % (metafile_json['volumes'][i]['volume_name'], file_name)

                    current_datetime = datetime.now().strftime('%Y-%m-%d-%H%M')
                    if metafile_json['volumes'][i]['snapshot_num'] - 1 > 0:
                        if not metafile_json['volumes'][i]['snapshot_num'] > int(os.getenv('backup_interval')):
                            response = s3_util.delete_directory(
                                metafile_json['volumes'][i]['volume_name'] + '/' + 
                                metafile_json['volumes'][i]['current_snapshot_id'] + '_' +
                                str(metafile_json['volumes'][i]['snapshot_num'] - 1), 
                                client
                            )
                        else:
                            metafile_json['volumes'][i]['current_snapshot_id'] = uuid.uuid4().hex
                            metafile_json['volumes'][i]['snapshot_num'] = 1
                    response = s3_util.upload_file(file_path, client, '%s/%s_%d_%s/%s' % (
                        metafile_json['volumes'][i]['volume_name'],
                        metafile_json['volumes'][i]['current_snapshot_id'],
                        metafile_json['volumes'][i]['snapshot_num'],
                        current_datetime, 
                        file_name
                    ))

            # Write new metafile json to temp filesystem
            with open('./temp/metafile', 'w') as json_bin:
                json.dump(metafile_json, json_bin, indent=4)
            
            # Upload new metafile from temp filesystem to S3 for use
            # in next backup.
            response = s3_util.upload_file(
                './temp/metafile',
                client, 
                'metafile'
            )
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