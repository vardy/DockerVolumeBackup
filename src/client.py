#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides interface for accessing S3 API connection
    as a custom Client object.
"""

# Standard library
import os

# Third-party sources
import boto3  # S3 API interface

class Client:
    __S3_Endpoint = os.getenv('S3_Endpoint')
    __S3_Region = os.getenv('S3_Region')
    __S3_Access_Key = os.getenv('S3_Access_Key')
    __S3_Secret_Key = os.getenv('S3_Secret_Key')
    __S3_Bucket = os.getenv('S3_Bucket_Name')
    __S3_Directory_Name = os.getenv('S3_Directory_Name')
    __Volumes_To_Backup = os.getenv('Volumes_To_Backup')

    __S3_Client = None
    
    def __init__(self):
        session = boto3.session.Session()
        s3_client = session.client(
            service_name='s3',
            aws_access_key_id=self.__S3_Access_Key,
            aws_secret_access_key=self.__S3_Secret_Key,
            region_name=self.__S3_Region,
            endpoint_url=self.__S3_Endpoint,
        )

        self.__S3_Client = s3_client
    
    def get_s3_client(self):
        return self.__S3_Client

    def get_volumes_to_backup(self):
        return self.__Volumes_To_Backup

    def get_directory_name(self):
        return self.__S3_Directory_Name
    
    def get_bucket_name(self):
        return self.__S3_Bucket