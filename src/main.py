"""
Takes backups off of a linux machine and sends them
to AWS S3.
"""
import logging
import sys
import os
import argparse
import yaml
import base64
import boto3
import time
import json
from aws import *
from backup_info import *

# Configure logging to std out.
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Uploads files in a directory to AWS s3.')
parser.add_argument('-c', '--config', type=str, help='Relative path to the configuration file.')
parser.add_argument('-k', '--key', type=str, help='Access key')
parser.add_argument('-s', '--secret', type=str, help='Secret key')
parser.add_argument('-b', '--bucket', type=str, help='The name of the s3 bucket.')
parser.add_argument('-r', '--region', type=str, help='The region you are using s3 in.')
parser.add_argument('-d', '--directory', type=str, help='The linux full directory path you are uploading files from')
args = parser.parse_args()
parser_config_file = args.config
parer_access_key = args.key
parser_secret_key = args.secret
parser_bucket_name = args.bucket
parser_directory = args.directory
parser_region = args.region

if __name__ == "__main__":
    # Load variables from configuration file.
    try:
        config_data = yaml.load(open(parser_config_file), Loader=yaml.BaseLoader)
        if config_data is not None:
            log.info("Configuration file found...")
            access_key = config_data.get('AWS').get('AccessKey')
            if access_key is not None:
                log.info("Access key loaded..")
                log.info("Access Key: %s", access_key)
            secret_key = config_data.get('AWS').get('SecretKey')
            if secret_key is not None:
                log.info("Secret key loaded...")
            remote_bucket = config_data.get('AWS').get('Bucket')
            if remote_bucket is not None:
                log.info("Remote bucket location established...")
                log.info('Bucket: %s', remote_bucket)
            directory_path = config_data.get('System').get('Directory')
            if directory_path is not None:
                log.info("Initializing directory %s...", directory_path)
            region = config_data.get('AWS').get('Region')
            if region is not None:
                log.info("Using region %s...", region)

    except Exception as e:
        log.error(e)

    # Load variables from commandline.

    try:
        if parer_access_key is not None:
            access_key = parer_access_key
            log.info("Access key loaded...")
            log.info("Access Key: %s", access_key)
        if parser_secret_key is not None:
            secret_key = parser_secret_key
            log.info("Secret key loaded...")
        if parser_bucket_name is not None:
            remote_bucket = parser_bucket_name
            log.info("Remote bucket location established...")
            log.info('Bucket: %s', remote_bucket)
        if parser_directory is not None:
            directory_path = parser_directory
            log.info("Initializing directory %s...", directory_path)
        if parser_region is not None:
            region = parser_region
            log.info("Using region %s...", region)
    except Exception as e:
        log.error(e)


    # Create a list of files in the target directory.
    try:
        located_files = os.listdir(directory_path)
        log.debug('Found the following files: %s', located_files)
    except Exception as e:
        log.error(e)

    # Getting the manifest from S3 if one exists. If not then we will create one. 
    try:
        client = AWS().configure_aws_profile(access_key, secret_key, region)
        manifest = AWS().list_objects(client, remote_bucket, prefix='manifest/manifest.json')
        if manifest.get('Contents') is None:
            manifest_init = { "manifest_bucket": remote_bucket, "manifest_creation_timestamp": int(time.time())}
            create_manifest = AWS().put_object(client, body=json.dumps(manifest_init), bucket=remote_bucket, key='manifest/manifest.json')
        log.info("Trying to get manifest file...")
        get_manifest = AWS().get_object(client, remote_bucket, key='manifest/manifest.json')
        loaded_manifest = json.loads(get_manifest.get('Body').read().decode('utf-8'))
        log.info("Loaded manifest successfully...")
    except Exception as e:
        log.error(e)


    try:
        manifested_files = loaded_manifest.get('manifested_files')
        s3_file_list = []
        if manifested_files is None:
            manifested_files = []
        
        for file in manifested_files:
            file_name = file.get('file_name')
            s3_file_list.append(file_name)

        for local_file in located_files:
            if local_file not in s3_file_list:
                log.info(f'Local file not found in s3 manifest for {local_file} !!!')
                file_size = Backups().file_size(directory_path, local_file)
                log.info(f'{local_file} has been determined to be {file_size} bytes...')
                s3_upload_dir = time.strftime("%Y/%m/%d/")
                now = int(time.time())
                s3_upload_file_name = f'{s3_upload_dir}{str(now)}-{local_file}'
                log.info(f'Starting upload to bucket {remote_bucket} prefix {s3_upload_file_name}...')
                upload = AWS().upload_object(client, bucket=remote_bucket, local_file=f'{directory_path}/{local_file}', remote_file=s3_upload_file_name)
                print(upload)
                update_dic = {'file_name': local_file, 'prefix': s3_upload_file_name, 'file_size': file_size, 'timestamp': now}
                manifested_files.append(update_dic)

        manifest_update = {"manifested_files": manifested_files}
        loaded_manifest.update(manifest_update)
        push_manifest_s3 = AWS().put_object(client, body=json.dumps(manifest_update), bucket=remote_bucket, key='manifest/manifest.json')


    except Exception as e:
        log.error(e)