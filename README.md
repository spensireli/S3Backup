# S3Backup
Python application to backup large files from a Linux server to S3. This application uses a manifest file located in the target bucket. 

This manifest file `manifest/manifest.json` contains metadata about your backed up files such as `file_name`, `prefix`, `file_size`, and `timestamp` of when the file was uploaded. 


## Usage

It is reccomended that you use a configuration file in yaml format. See the Config Section.
```
python3 src/main.py -c ./config.yml
```


You may also use the argument parser directly. 
```
Uploads files in a directory to AWS s3.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Relative path to the configuration file.
  -k KEY, --key KEY     Access key
  -s SECRET, --secret SECRET
                        Secret key
  -b BUCKET, --bucket BUCKET
                        The name of the s3 bucket.
  -r REGION, --region REGION
                        The region you are using s3 in.
  -d DIRECTORY, --directory DIRECTORY
                        The linux full directory path you are uploading files from
```

## Config File

Configuration file example.

```yaml
AWS:
  Region: us-east-1
  Bucket: your-bucket-name
  AccessKey: 'your-access-key'
  SecretKey: 'your-secret-key'
System:
  Directory: '/full/path/to/your/directory'

```


## Manifest File Example

```json
{
    "manifested_files": [
        {
            "file_name": "spencer.tar",
            "prefix": "2022/03/28/1648523098-spencer.tar",
            "file_size": 7,
            "timestamp": 1648523098
        },
        {
            "file_name": "testerino.txt",
            "prefix": "2022/03/28/1648523098-testerino.txt",
            "file_size": 13,
            "timestamp": 1648523098
        },
        {
            "file_name": "bubba.zip",
            "prefix": "2022/03/28/1648523166-bubba.zip",
            "file_size": 5,
            "timestamp": 1648523166
        }
    ]
}
```