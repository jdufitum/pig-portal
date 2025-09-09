from __future__ import annotations

import uuid
from datetime import timedelta

import boto3
from botocore.client import Config

from ..core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def generate_object_key(pig_id: uuid.UUID, filename: str) -> str:
    ext = filename.split(".")[-1].lower() if "." in filename else "bin"
    return f"pigs/{pig_id}/{uuid.uuid4()}.{ext}"

