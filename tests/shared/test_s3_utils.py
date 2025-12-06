# tests/shared/test_s3_utils.py

from __future__ import annotations

from pathlib import Path
from typing import Any

from botocore.exceptions import ClientError, NoCredentialsError
import pytest

import src.shared.s3_utils as s3_utils


def test_upload_file_to_s3_raises_when_file_not_exists(tmp_path):
    """
    Deve levantar FileNotFoundError quando o arquivo local não existe.
    """
    nonexistent = tmp_path / "does_not_exist.txt"

    with pytest.raises(FileNotFoundError) as excinfo:
        s3_utils.upload_file_to_s3(
            file_path=nonexistent,
            bucket="my-bucket",
            key="some/key.txt",
        )

    assert "Local file does not exist" in str(excinfo.value)


def test_upload_file_to_s3_calls_boto3_client_and_upload(monkeypatch, tmp_path, capsys):
    """
    Quando o arquivo existe, deve criar client S3 e chamar upload_file
    com os parâmetros corretos.
    """
    # Cria arquivo local
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    calls: list[dict[str, Any]] = []

    class FakeS3Client:
        def upload_file(self, filename, bucket, key):
            calls.append(
                {
                    "filename": filename,
                    "bucket": bucket,
                    "key": key,
                }
            )

    def fake_client(service_name: str):
        assert service_name == "s3"
        return FakeS3Client()

    monkeypatch.setattr(s3_utils, "boto3", type("Boto3", (), {"client": fake_client}))

    s3_utils.upload_file_to_s3(
        file_path=file_path, bucket="my-bucket", key="folder/file.txt"
    )

    captured = capsys.readouterr()
    assert "[S3_UTILS] Uploading file" in captured.out
    assert "[S3_UTILS] Uploaded file" in captured.out

    assert len(calls) == 1
    assert calls[0]["filename"] == str(file_path)
    assert calls[0]["bucket"] == "my-bucket"
    assert calls[0]["key"] == "folder/file.txt"


@pytest.mark.parametrize("path_type", ["str", "path"])
def test_download_file_from_s3_creates_parent_and_calls_boto(
    monkeypatch, tmp_path, path_type, capsys
):
    """
    Deve criar o diretório pai (se necessário) e chamar s3.download_file
    com os parâmetros corretos, tanto recebendo str quanto Path.
    """
    bucket = "my-bucket"
    key = "some/prefix/file.txt"

    target_path = tmp_path / "nested" / "dir" / "file.txt"
    file_arg: str | Path = str(target_path) if path_type == "str" else target_path

    calls: list[dict[str, Any]] = []

    class FakeS3Client:
        def download_file(self, bucket_name, s3_key, filename):
            calls.append(
                {
                    "bucket": bucket_name,
                    "key": s3_key,
                    "filename": filename,
                }
            )

    def fake_client(service_name: str):
        assert service_name == "s3"
        return FakeS3Client()

    monkeypatch.setattr(s3_utils, "boto3", type("Boto3", (), {"client": fake_client}))

    s3_utils.download_file_from_s3(bucket=bucket, key=key, file_path=file_arg)

    captured = capsys.readouterr()
    assert "[S3_UTILS] Downloading file" in captured.out
    assert "[S3_UTILS] Downloaded file" in captured.out

    # Diretório pai deve existir após a chamada
    assert target_path.parent.exists()

    assert len(calls) == 1
    assert calls[0]["bucket"] == bucket
    assert calls[0]["key"] == key
    assert calls[0]["filename"] == str(target_path)


def test_download_folder_from_s3_downloads_all_files(monkeypatch, tmp_path, capsys):
    """
    Deve listar os objetos por prefixo, pular chaves que terminam com '/',
    e chamar o helper download_file_from_s3 para cada arquivo.
    Também deve normalizar o folder_key (strip leading '/' + trailing '/').
    """
    bucket = "my-bucket"
    folder_key = "/my-prefix/monitoring"  # com barra no início de propósito
    local_folder = tmp_path / "monitoring_download"

    # Fake paginator/pages
    pages = [
        {
            "Contents": [
                {"Key": "my-prefix/monitoring/"},
                {"Key": "my-prefix/monitoring/file1.json"},
                {"Key": "my-prefix/monitoring/subdir/file2.json"},
            ]
        }
    ]

    class FakePaginator:
        def paginate(self, Bucket, Prefix):
            # Prefix deve estar normalizado: sem leading '/' e com trailing '/'
            assert Prefix == "my-prefix/monitoring/"
            assert Bucket == bucket
            return pages

    class FakeS3Client:
        def get_paginator(self, name: str):
            assert name == "list_objects_v2"
            return FakePaginator()

    def fake_client(service_name: str):
        assert service_name == "s3"
        return FakeS3Client()

    # Monkeypatch boto3.client
    monkeypatch.setattr(s3_utils, "boto3", type("Boto3", (), {"client": fake_client}))

    # Monkeypatch do helper download_file_from_s3 para inspecionar chamadas
    calls: list[dict[str, Any]] = []

    def fake_download_file_from_s3(bucket, key, file_path):
        calls.append(
            {
                "bucket": bucket,
                "key": key,
                "file_path": file_path,
            }
        )

    monkeypatch.setattr(s3_utils, "download_file_from_s3", fake_download_file_from_s3)

    s3_utils.download_folder_from_s3(
        bucket=bucket, folder_key=folder_key, folder_path=local_folder
    )

    captured = capsys.readouterr()
    assert "[S3_UTILS] Downloading folder" in captured.out
    assert "[S3_UTILS] Downloaded folder" in captured.out
    assert "total files: 2" in captured.out

    # Local folder deve existir
    assert local_folder.exists()

    # Deve ter baixado 2 arquivos (file1.json e subdir/file2.json)
    assert len(calls) == 2

    keys = {c["key"] for c in calls}
    assert keys == {
        "my-prefix/monitoring/file1.json",
        "my-prefix/monitoring/subdir/file2.json",
    }

    # Verifica que o path relativo foi montado corretamente
    paths = {Path(c["file_path"]).relative_to(local_folder) for c in calls}
    assert paths == {Path("file1.json"), Path("subdir") / "file2.json"}


def test_download_folder_from_s3_handles_empty_prefix(monkeypatch, tmp_path, capsys):
    """
    Quando não houver nenhum objeto (sem 'Contents' nas páginas),
    deve apenas logar e não chamar o helper de download.
    """
    bucket = "my-bucket"
    folder_key = "empty-prefix"
    local_folder = tmp_path / "empty_download"

    class FakePaginator:
        def paginate(self, Bucket, Prefix):
            assert Bucket == bucket
            assert Prefix == "empty-prefix/"
            return [{"IsTruncated": False}]  # sem "Contents"

    class FakeS3Client:
        def get_paginator(self, name: str):
            assert name == "list_objects_v2"
            return FakePaginator()

    def fake_client(service_name: str):
        assert service_name == "s3"
        return FakeS3Client()

    monkeypatch.setattr(s3_utils, "boto3", type("Boto3", (), {"client": fake_client}))

    calls: list[dict[str, Any]] = []

    def fake_download_file_from_s3(bucket_arg, key_arg, file_path_arg):
        calls.append(
            {
                "bucket": bucket_arg,
                "key": key_arg,
                "file_path": file_path_arg,
            }
        )

    monkeypatch.setattr(s3_utils, "download_file_from_s3", fake_download_file_from_s3)

    s3_utils.download_folder_from_s3(
        bucket=bucket, folder_key=folder_key, folder_path=local_folder
    )

    captured = capsys.readouterr()
    assert "[S3_UTILS] Downloading folder" in captured.out
    assert "[S3_UTILS] Downloaded folder" in captured.out
    assert "total files: 0" in captured.out

    assert local_folder.exists()
    assert calls == []


def test_download_folder_from_s3_handles_no_credentials_error(
    monkeypatch, tmp_path, capsys
):
    """
    Quando o boto/cliente levantar NoCredentialsError, deve logar a mensagem
    e não propagar a exceção.
    """
    bucket = "my-bucket"
    folder_key = "any-prefix"
    local_folder = tmp_path / "folder"

    class FakeS3Client:
        def get_paginator(self, name: str):
            raise NoCredentialsError()

    def fake_client(service_name: str):
        assert service_name == "s3"
        return FakeS3Client()

    monkeypatch.setattr(s3_utils, "boto3", type("Boto3", (), {"client": fake_client}))

    # Não deve levantar
    s3_utils.download_folder_from_s3(
        bucket=bucket, folder_key=folder_key, folder_path=local_folder
    )

    captured = capsys.readouterr()
    assert "AWS credentials not found" in captured.out


def test_download_folder_from_s3_handles_client_error(monkeypatch, tmp_path, capsys):
    """
    Quando ocorrer ClientError durante listagem/download, deve logar a mensagem
    de erro e não propagar a exceção.
    """
    bucket = "my-bucket"
    folder_key = "any-prefix"
    local_folder = tmp_path / "folder"

    class FakePaginator:
        def paginate(self, Bucket, Prefix):
            # Simula erro ao paginar
            raise ClientError(
                error_response={"Error": {"Code": "AccessDenied", "Message": "Denied"}},
                operation_name="ListObjectsV2",
            )

    class FakeS3Client:
        def get_paginator(self, name: str):
            return FakePaginator()

    def fake_client(service_name: str):
        assert service_name == "s3"
        return FakeS3Client()

    monkeypatch.setattr(s3_utils, "boto3", type("Boto3", (), {"client": fake_client}))

    # Não deve levantar
    s3_utils.download_folder_from_s3(
        bucket=bucket, folder_key=folder_key, folder_path=local_folder
    )

    captured = capsys.readouterr()
    assert "Error while downloading from S3" in captured.out
    assert "AccessDenied" in captured.out
