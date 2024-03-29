#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides interface for accessing environment variables
    as configuration.
"""

# Standard library
import os


class Config:
    __S3_Endpoint = os.getenv('S3_Endpoint')
    __S3_Region = os.getenv('S3_Region')
    __S3_Access_Key = os.getenv('S3_Access_Key')
    __S3_Secret_Key = os.getenv('S3_Secret_Key')
    __S3_Bucket = os.getenv('S3_Bucket_Name')
    __S3_Directory_Name = os.getenv('S3_Directory_Name', 'docker_backups')
    __Volumes_To_Backup = os.getenv('Volumes_To_Backup')
    __Backup_On_Startup = os.getenv('backup_on_startup', 'yes')
    __Snapshot_Interval = os.getenv('snapshot_interval', 2)
    __Backup_Interval = os.getenv('backup_interval', 12)

    def get_s3_endpoint(self):
        return self.__S3_Endpoint

    def get_s3_region(self):
        return self.__S3_Region

    def get_s3_access_key(self):
        return self.__S3_Access_Key

    def get_s3_secret_key(self):
        return self.__S3_Secret_Key

    def get_bucket_name(self):
        return self.__S3_Bucket

    def get_directory_name(self):
        return self.__S3_Directory_Name

    def get_volumes_to_backup(self):
        return self.__Volumes_To_Backup

    def get_do_backup_on_startup(self):
        return self.__Backup_On_Startup == 'yes'

    def get_snapshot_interval(self):
        return int(self.__Snapshot_Interval)

    def get_backup_interval(self):
        return int(self.__Backup_Interval)
