"""Cross-account AWS session management for MCP (Model Context Protocol) Lambda functions.

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Used when deploying to data collection account with access to
Cost Explorer and CUR data in the management/payer account.
"""

import os
import time

import boto3

# ISO 27001 A.8.28: TTL-based credential caching to prevent use of expired STS credentials.
# Lambda execution environments can live longer than the 1-hour STS credential TTL, so
# lru_cache (which never expires) would silently serve expired credentials. We refresh
# proactively 5 minutes before expiry.
_cached_session = None
_session_expiry: float = 0.0
_REFRESH_BUFFER_SECONDS = 300  # refresh 5 min before expiry


def get_cross_account_session():
    """Get boto3 session with assumed role credentials (TTL-cached for Lambda reuse).

    Returns:
        boto3.Session with assumed role credentials, or None if not configured.
    """
    global _cached_session, _session_expiry

    role_arn = os.environ.get("CROSS_ACCOUNT_ROLE_ARN", "")
    external_id = os.environ.get("CROSS_ACCOUNT_EXTERNAL_ID", "")

    if not role_arn:
        return None

    # Return cached session if still valid (with refresh buffer)
    if _cached_session is not None and time.time() < _session_expiry - _REFRESH_BUFFER_SECONDS:
        return _cached_session

    sts = boto3.client("sts")
    params = {
        "RoleArn": role_arn,
        "RoleSessionName": "mcp-gateway-cross-account",
        "DurationSeconds": 3600,
    }
    if external_id:
        params["ExternalId"] = external_id

    response = sts.assume_role(**params)
    creds = response["Credentials"]
    _session_expiry = creds["Expiration"].timestamp()
    _cached_session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )
    return _cached_session


def get_aws_client(service_name, region_name=None, **kwargs):
    """Get boto3 client - uses cross-account role if configured, else execution role.

    Args:
        service_name: AWS service name (e.g., 'ce', 'athena', 's3')
        region_name: Optional AWS region
        **kwargs: Additional arguments passed to boto3.client()

    Returns:
        boto3 client for the specified service
    """
    session = get_cross_account_session()
    client_kwargs = {"region_name": region_name} if region_name else {}
    client_kwargs.update(kwargs)

    if session:
        return session.client(service_name, **client_kwargs)
    return boto3.client(service_name, **client_kwargs)
