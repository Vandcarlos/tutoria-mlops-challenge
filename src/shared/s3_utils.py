from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def upload_file_to_s3(file_path: Path, bucket: str, key: str) -> None:
    """
    Upload a single local file to S3.

    Parameters
    ----------
    file_path :
        Local file path to upload.
    bucket :
        Target S3 bucket name.
    key :
        Target S3 object key within the bucket.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Local file does not exist: {file_path}")

    s3 = boto3.client("s3")
    print(
        "[S3_UTILS] Uploading file"
        f" from path: {file_path}"
        f" to bucket: {bucket}"
        f" with key: {key}"
    )
    s3.upload_file(str(file_path), bucket, key)
    print(
        "[S3_UTILS] Uploaded file"
        f" from path: {file_path}"
        f" to bucket: {bucket}"
        f" with key: {key}"
    )


def download_file_from_s3(bucket: str, key: str, file_path: Path | str) -> None:
    """
    Download a single file from S3 to a local path.

    Parameters
    ----------
    bucket :
        Source S3 bucket name.
    key :
        Source S3 object key.
    file_path :
        Local path where the file will be downloaded.
    """

    if isinstance(file_path, str):
        file_path = Path(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3")
    print(
        "[S3_UTILS] Downloading file"
        f" from bucket: {bucket}"
        f" with key: {key}"
        f" to path: {file_path}"
    )
    s3.download_file(bucket, key, str(file_path))
    print(
        "[S3_UTILS] Downloaded file"
        f" from bucket: {bucket}"
        f" with key: {key}"
        f" to path: {file_path}"
    )


def download_folder_from_s3(bucket: str, folder_key: str, folder_path: Path) -> None:
    """
    Download all files from an S3 folder/prefix to local directory

    Args:
        bucket (str): Name of the S3 bucket
        folder_key (str): S3 folder/prefix path (e.g., 'data/images/')
        folder_path (Path): Local directory to save files
    """
    folder_path.mkdir(parents=True, exist_ok=True)

    folder_key = folder_key.lstrip("/")

    if folder_key and not folder_key.endswith("/"):
        folder_key += "/"

    print(
        "[S3_UTILS] Downloading folder"
        f" from bucket: {bucket}"
        f" with key: {folder_key}"
        f" to path: {folder_path}"
    )

    s3_client = boto3.client("s3")

    try:
        # List all objects in the S3 folder
        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=folder_key)

        downloaded_files_count = 0

        for page in pages:
            if "Contents" in page:
                for obj in page["Contents"]:
                    s3_key = obj["Key"]

                    # Skip if it's just a folder (ends with /)
                    if s3_key.endswith("/"):
                        continue

                    # Create local file path
                    # Remove the s3_folder prefix and create relative path
                    relative_path = s3_key[len(folder_key) :].lstrip("/")
                    local_file_path = folder_path / relative_path

                    download_file_from_s3(
                        bucket=bucket,
                        key=s3_key,
                        file_path=local_file_path,
                    )

                    downloaded_files_count += 1

        print(
            "[S3_UTILS] Downloaded folder"
            f" from bucket: {bucket}"
            f" with key: {folder_key}"
            f" to path: {folder_path}"
            f" total files: {downloaded_files_count}"
        )

    except NoCredentialsError:
        print("[S3_UTILS] Error: AWS credentials not found.")
    except ClientError as e:
        print(f"[S3_UTILS] Error while downloading from S3: {e}")
