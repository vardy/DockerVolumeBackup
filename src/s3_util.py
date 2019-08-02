#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Selection of functions for accessing, creating and manipulating
    objects stored in the S3 filesystem.
"""

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

    # Perform HEAD on object to check if it exists
    try:
        s3_client.head_object(Bucket=client.get_bucket_name(), Key=object_name)
    except ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            return False
        else:
            logging.error(ex)
    else:
        return True

def delete_object(object_name, client):
    """ Delete an object in an S3 bucket

    :param object_name: Object name in bucket to delete
    :param client: Client object
    :return: True if file deleted, else False
    """

    s3_client = client.get_s3_client()

    # Delete the file
    try:
        response = s3_client.delete_object(
            Bucket=client.get_bucket_name(), 
            Key=object_name
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