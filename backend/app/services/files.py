from __future__ import annotations

import uuid
from datetime import timedelta

import boto3
from botocore.client import Config

from ..config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def generate_object_key(pig_id: uuid.UUID, filename: str) -> str:
    ext = filename.split(".")[-1].lower() if "." in filename else "bin"
    return f"pigs/{pig_id}/{uuid.uuid4()}.{ext}"

