#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Selection of functions for accessing, creating and manipulating
    objects stored in the S3 filesystem.
"""

# Standard library
import logging
import os

# Third party libraries
from botocore.exceptions import ClientError

# Local source
from progress import ProgressPercentage

def check_if_object_exists(object_name, client):
    """ Check if a object exists in an S3 bucket

    :param object_name: Object name in bucket to check
    :param client: Client object
    :return: True if file exists, else False
    """

    s3_client = client.get_s3_client()

    object_path = '%s/%s' % (client.get_directory_name(), object_name)

    # Perform HEAD on object to check if it exists
    try:
        s3_client.head_object(Bucket=client.get_bucket_name(), Key=object_path)
    except ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            return False
        else:
            logging.error(ex)
            return
    else:
        return True

def delete_object(object_name, client):
    """ Delete an object in an S3 bucket

    :param object_name: Object name in bucket to delete
    :param client: Client object
    :return: True if file deleted, else False
    """

    s3_client = client.get_s3_client()

    object_path = '%s/%s' % (client.get_directory_name(), object_name)

    # Delete the file
    try:
        response = s3_client.delete_object(
            Bucket=client.get_bucket_name(), 
            Key=object_path
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True

def upload_file(file_name, client, object_name=None):
    """ Upload a file to an S3 bucket

    :param file_name: File to upload
    :param client: Client object
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    s3_client = client.get_s3_client()

    object_path = '%s/%s' % (client.get_directory_name(), object_name)

    # Upload the file
    try:
        response = s3_client.upload_file(
            file_name, client.get_bucket_name(), object_path, 
            Callback=ProgressPercentage(file_name)
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True

def download_object(object_name, client, file_name=None):
    """ Download an object from an S3 bucket

    :param object_name: Object to download
    :param client: Client object
    :param file_name: Name of file to save
    :return: True if downloaded, else False
    """

    if file_name is None:
        file_name = object_name
    
    s3_client = client.get_s3_client()

    object_path = '%s/%s' % (client.get_directory_name(), object_name)
    root_dir_path = os.path.abspath(os.curdir)
    file_path = root_dir_path + file_name

    # Download the file
    try:
        response = s3_client.download_file(
            Bucket=client.get_bucket_name(), 
            Key=object_path, 
            Filename=file_path
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True