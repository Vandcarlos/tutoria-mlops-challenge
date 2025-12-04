from pathlib import Path

import boto3


def upload_file_to_s3(file_path: Path, bucket: str, key: str) -> None:
    """
    Upload a single local file to S3.

    Parameters
    ----------
    local_path :
        Local file path to upload.
    bucket :
        Target S3 bucket name.
    key :
        Target S3 object key within the bucket.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Local file does not exist: {file_path}")

    s3 = boto3.client("s3")
    s3.upload_file(str(file_path), bucket, key)


def download_file_from_s3(bucket: str, key: str, file_path: Path) -> None:
    """
    Download a single file from S3 to a local path.

    Parameters
    ----------
    bucket :
        Source S3 bucket name.
    key :
        Source S3 object key.
    local_path :
        Local path where the file will be downloaded.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3")
    s3.download_file(bucket, key, str(file_path))
