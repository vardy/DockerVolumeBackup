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
from utils.progress import ProgressPercentage
from config.config import Config

config = Config()


def check_if_object_exists(object_name, client):
    """ Check if a object exists in an S3 bucket

    :param object_name: Object name in bucket to check
    :param client: S3 client object
    :return: True if file exists, else False
    """

    object_path = '%s/%s' % (config.get_directory_name(), object_name)

    # Perform HEAD on object to check if it exists
    try:
        client.head_object(Bucket=config.get_bucket_name(), Key=object_path)
    except ClientError as ex:
        if ex.response['Error']['Code'] == "404":
            return False
        else:
            logging.error(ex)
            return
    else:
        return True


def delete_object(object_name, client, **kwargs):
    """ Delete an object in an S3 bucket

    :param object_name: Object name in bucket to delete
    :param client: S3 client object
    :return: True if file deleted, else False
    """

    absolute_path = False
    if kwargs is not None:
        for key, value in kwargs.items():
            if key == 'abs_path' and value:
                absolute_path = True

    object_path = object_name if absolute_path else '%s/%s' % (config.get_directory_name(), object_name)

    # Delete the object
    try:
        response = client.delete_object(
            Bucket=config.get_bucket_name(),
            Key=object_path
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True


def delete_objects_by_prefix(prefix, client, **kwargs):
    """ Delete an object in an S3 bucket by its specified prefix

    :param prefix: Partial of object's key
    :param client: S3 client object
    :return: True if file deleted, else False
    """

    absolute_path = False
    if kwargs is not None:
        for key, value in kwargs.items():
            if key == 'abs_path' and value:
                absolute_path = True

    object_path = prefix if absolute_path else '%s/%s' % (config.get_directory_name(), prefix)

    # Delete all object matching prefix
    for element in list_objects_in_dir(object_path, client)['Contents']:
        try:
            delete_object(element['Key'], client, abs_path=True)
        except ClientError as ex:
            logging.error(ex)


def upload_file(file_name, client, object_name=None):
    """ Upload a file to an S3 bucket

    :param file_name: File to upload
    :param client: S3 client object
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    object_path = '%s/%s' % (config.get_directory_name(), object_name)

    # Upload the file
    try:
        response = client.upload_file(
            file_name, config.get_bucket_name(), object_path,
            Callback=ProgressPercentage(file_name)
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True


def download_object(object_name, client, file_name=None):
    """ Download an object from an S3 bucket

    :param object_name: Object to download
    :param client: S3 Client object
    :param file_name: Name of file to save
    :return: True if downloaded, else False
    """

    if file_name is None:
        file_name = object_name

    object_path = '%s/%s' % (config.get_directory_name(), object_name)
    root_dir_path = os.path.abspath(os.curdir)
    file_path = root_dir_path + file_name

    # Download the file
    try:
        response = client.download_file(
            Bucket=config.get_bucket_name(),
            Key=object_path,
            Filename=file_path
        )
    except ClientError as ex:
        logging.error(ex)
        return False
    return True


def list_objects_in_dir(dir_name, client):
    """ Lists objects in specified directory in S3

    :param dir_name: The directory to list recursively from
    :param client: S3 client object
    :return: Dictionary response
    """

    return client.list_objects_v2(
        Bucket=config.get_bucket_name(),
        Prefix=dir_name
    )


def delete_directory(directory_path, client):
    """ Delete all objects in S3 directory

    :param directory_path: Path to directory to delete
    :param client: S3 client object
    :return: True if deleted successfully, else False
    """

    # For each item in directory, pass to delete_file with abs_path kwarg
    try:
        for element in list_objects_in_dir('docker_backups/' + directory_path, client)['Contents']:
            delete_object(element['Key'], client, abs_path=True)
    except KeyError as ex:
        return
    return


def get_key_from_prefix(prefix, client):
    """ Get object's key from its prefix (first found)

    :param prefix: Prefix of key to find
    :param client: S3 client object
    :return: True if deleted successfully, else False
    """

    try:
        for element in list_objects_in_dir(prefix, client)['Contents']:
            # Return first key
            return element['Key']
    except KeyError as ex:
        logging.error(ex)
