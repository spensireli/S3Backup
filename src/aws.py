"""
AWS usage of S3 Backup.
"""
import boto3


class AWS():
    """
    Class for all AWS resources that will be used.
    """
    def configure_aws_profile(self, key, secret, region):
        """
        Function for configuration of AWS with access key and region.
        """
        session = boto3.Session(
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name=region
        )
        return session
    
    def list_objects(self, session, bucket, prefix):
        client = session.client('s3')
        response = client.list_objects(
            Bucket=bucket,
            Prefix=prefix
        )
        return response
    
    def put_object(self, session, body, bucket, key):
        client = session.client('s3')
        response = client.put_object(
            Body=body, 
            Bucket=bucket,
            Key=key
        )

    def get_object(self, session, bucket, key):
        client = session.client('s3')
        response = client.get_object(
            Bucket=bucket,
            Key=key
            )
        return response

    def upload_object(self, session, bucket, local_file, remote_file):
        client = session.resource('s3')
        uploading = client.Bucket(bucket).upload_file(local_file, remote_file)
        return(uploading)

